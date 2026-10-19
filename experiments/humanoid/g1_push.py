"""Unitree G1 push recovery in MuJoCo: balance controllers scored in several worlds.

A "world" is a set of dynamics parameters. One world plays the real robot; the
others are simulators of different fidelity. A "policy" is a standing balance
controller on top of the G1's position servos. Each trial pushes the pelvis
from one of eight directions (the conditions) and succeeds if the robot is
still upright when the episode ends.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import mujoco
import numpy as np

STEPS, DT = 1000, 0.002          # 2 s episodes
PUSH_AT, PUSH_STEPS = 150, 75    # push from 0.3 s to 0.45 s
DIRECTIONS = 8
UPRIGHT_Z = 0.55
PUSH_LO, PUSH_HI = 30.0, 110.0   # N
INIT_NOISE = 0.03                # rad, joint angles at reset


@dataclass(frozen=True)
class Policy:
    name: str
    crouch: float      # knee flexion of the nominal posture, rad
    ankle_fb: float    # ankle torque-angle feedback on pelvis tilt
    hip_fb: float      # hip feedback on pelvis tilt
    stiffness: float   # scale on the servo gains


@dataclass(frozen=True)
class World:
    name: str
    torso_mass: float = 1.0     # scale on pelvis and torso link masses
    motor: float = 1.0          # scale on servo strength
    delay: int = 0              # control delay, steps
    friction: float = 0.6       # foot sliding friction
    joint_friction: float = 0.3
    tilt_noise: float = 0.0     # std of the tilt observation noise, rad
    push: float = 1.0           # scale on push force
    randomize: dict = field(default_factory=dict)   # name -> (lo, hi), drawn per trial


def _load(menagerie: Path):
    return mujoco.MjModel.from_xml_path(str(menagerie / "unitree_g1" / "scene.xml"))


class Runner:
    """Holds one compiled model per process and runs trials in any world."""

    def __init__(self, menagerie: Path):
        self.m = _load(menagerie)
        self.d = mujoco.MjData(self.m)
        self.key = self.m.key("stand").id
        self.pelvis = self.m.body("pelvis").id
        self.base = {
            "mass": self.m.body_mass.copy(),
            "gain": self.m.actuator_gainprm[:, 0].copy(),
            "bias": self.m.actuator_biasprm[:, :3].copy(),
            "fric": self.m.geom_friction[:, 0].copy(),
            "jfric": self.m.dof_frictionloss.copy(),
        }
        heavy = [self.m.body(n).id for n in ("pelvis", "torso_link")]
        self.heavy = np.array(heavy)
        self.feet = np.array([g for g in range(self.m.ngeom) if self.m.geom_friction[g, 0] == 0.6])
        names = [self.m.actuator(i).name for i in range(self.m.nu)]
        self.idx = {n: names.index(n + "_joint") for n in (
            "left_hip_pitch", "right_hip_pitch", "left_knee", "right_knee",
            "left_ankle_pitch", "right_ankle_pitch", "left_ankle_roll", "right_ankle_roll",
            "left_hip_roll", "right_hip_roll")}

    def _apply(self, w: World, policy: Policy, rng):
        p = {k: getattr(w, k) for k in ("torso_mass", "motor", "delay", "friction", "joint_friction", "tilt_noise", "push")}
        for k, (lo, hi) in w.randomize.items():
            p[k] = rng.uniform(lo, hi)
        m, b = self.m, self.base
        m.body_mass[:] = b["mass"]
        m.body_mass[self.heavy] = b["mass"][self.heavy] * p["torso_mass"]
        g = b["gain"] * p["motor"] * policy.stiffness
        m.actuator_gainprm[:, 0] = g
        m.actuator_biasprm[:, 1] = -g
        m.actuator_biasprm[:, 2] = b["bias"][:, 2] * p["motor"] * np.sqrt(policy.stiffness)
        m.geom_friction[self.feet, 0] = p["friction"]
        m.dof_frictionloss[:] = b["jfric"] / 0.3 * p["joint_friction"]
        p["delay"] = int(round(p["delay"]))
        return p

    def trial(self, w: World, policy: Policy, direction: int, seed: int) -> bool:
        rng = np.random.default_rng(seed)
        p = self._apply(w, policy, rng)
        m, d = self.m, self.d
        mujoco.mj_resetDataKeyframe(m, d, self.key)
        d.qpos[7:] += rng.normal(0, INIT_NOISE, m.nq - 7)
        ref = m.key_ctrl[self.key].copy()
        c, ix = policy.crouch, self.idx
        for s in ("left", "right"):
            ref[ix[f"{s}_hip_pitch"]] -= c / 2
            ref[ix[f"{s}_knee"]] += c
            ref[ix[f"{s}_ankle_pitch"]] -= c / 2
        mujoco.mj_forward(m, d)
        angle = 2 * np.pi * (direction + rng.uniform(-0.3, 0.3)) / DIRECTIONS
        force = p["push"] * rng.uniform(PUSH_LO, PUSH_HI) * np.array([np.cos(angle), np.sin(angle), 0])
        queue = [ref.copy()] * (p["delay"] + 1)
        for t in range(STEPS):
            # pelvis tilt: gravity direction in the pelvis frame
            R = d.xmat[self.pelvis].reshape(3, 3)
            gx, gy = R[2, 0], R[2, 1]
            pitch = gx + rng.normal(0, p["tilt_noise"])
            roll = -gy + rng.normal(0, p["tilt_noise"])
            u = ref.copy()
            for s in ("left", "right"):
                u[ix[f"{s}_ankle_pitch"]] += policy.ankle_fb * pitch
                u[ix[f"{s}_hip_pitch"]] += policy.hip_fb * pitch
                u[ix[f"{s}_ankle_roll"]] -= policy.ankle_fb * roll
                u[ix[f"{s}_hip_roll"]] -= policy.hip_fb * roll
            queue.append(u)
            d.ctrl[:] = queue.pop(0)
            d.xfrc_applied[self.pelvis, :3] = force if PUSH_AT <= t < PUSH_AT + PUSH_STEPS else 0
            mujoco.mj_step(m, d)
            if d.xpos[self.pelvis, 2] < 0.4:
                return False
        return bool(d.xpos[self.pelvis, 2] > UPRIGHT_Z)


POLICIES = [Policy(f"P{i:02d}", *args) for i, args in enumerate([
    (0.30, -0.4, 0.0, 1.0), (0.30, -0.4, -0.4, 0.6), (0.00, -0.4, 0.4, 1.0), (0.15, 0.0, 0.0, 1.0),
    (0.00, 0.0, 0.0, 0.6), (0.30, 0.0, -0.4, 0.6), (0.15, 0.0, 0.0, 0.6), (0.30, 0.0, 0.4, 0.6),
    (0.15, 0.4, 0.0, 0.6), (0.00, 0.4, 0.0, 0.6), (0.15, 0.4, 0.4, 1.0), (0.00, 0.4, 0.4, 0.6),
])]

REAL = World("real", torso_mass=1.2, motor=0.75, delay=6, friction=0.45, joint_friction=0.6, tilt_noise=0.01)
SIMS = [
    World("nominal"),
    World("randomized", randomize={"torso_mass": (0.9, 1.3), "motor": (0.7, 1.1), "delay": (0, 8), "friction": (0.4, 0.8)}),
    World("sysid", torso_mass=1.2, motor=0.75),
    World("sysid+delay", torso_mass=1.2, motor=0.75, delay=6),
    World("misidentified", torso_mass=0.8, motor=1.2),
]
