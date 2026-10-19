"""Renders the README banner: MuJoCo Menagerie robots on a white stage.

    python docs/figures/render_scenes.py /path/to/mujoco_menagerie

Google Robot and WidowX (wx250s here) are the two SIMPLER embodiments; Panda and
the Unitree G1 humanoid are added for the platforms proxyrank is meant to cover.
"""

from __future__ import annotations

import sys
from pathlib import Path

import mujoco
import numpy as np
from PIL import Image

OUT = Path(__file__).parent

# (menagerie dir, model file, keyframe name or None, x position, yaw degrees)
# yaw -90 turns each robot's +x front toward the camera
ROBOTS = [
    ("trossen_wx250s", "wx250s.xml", "home", -1.25, -90),
    ("franka_emika_panda", "panda.xml", "home", -0.55, -90),
    ("google_robot", "robot.xml", None, 0.3, -90),
    ("unitree_g1", "g1.xml", "stand", 1.2, -90),
]
# the Google Robot has no keyframe and stands with its arm straight up at qpos0
OVERRIDES = {"google_robot": {"joint_shoulder": -1.0, "joint_bicep": 1.2, "joint_elbow": 1.6, "joint_wrist": 0.6}}


def stage() -> mujoco.MjSpec:
    spec = mujoco.MjSpec()
    spec.visual.headlight.ambient = [0.3, 0.3, 0.3]
    spec.visual.headlight.diffuse = [0.12, 0.12, 0.12]
    spec.visual.headlight.specular = [0, 0, 0]
    spec.visual.quality.shadowsize = 8192
    spec.visual.global_.offwidth = 2800
    spec.visual.global_.offheight = 1300
    spec.add_texture(
        name="sky", type=mujoco.mjtTexture.mjTEXTURE_SKYBOX, builtin=mujoco.mjtBuiltin.mjBUILTIN_GRADIENT,
        rgb1=[1, 1, 1], rgb2=[1, 1, 1], width=64, height=384,
    )
    spec.worldbody.add_geom(type=mujoco.mjtGeom.mjGEOM_PLANE, size=[4, 3, 0.1], rgba=[1, 1, 1, 1])
    # a spot key light: its cone bounds the shadow map, so contact shadows stay sharp
    spec.worldbody.add_light(pos=[-0.8, -2.5, 4.5], dir=[0.16, 0.5, -0.9], type=mujoco.mjtLightType.mjLIGHT_SPOT,
                             cutoff=45, exponent=1, diffuse=[0.6, 0.6, 0.6], castshadow=True)
    spec.worldbody.add_light(pos=[2, 2, 3], dir=[-0.4, -0.4, -1], type=mujoco.mjtLightType.mjLIGHT_DIRECTIONAL,
                             diffuse=[0.1, 0.1, 0.1], castshadow=False)
    return spec


def build(menagerie: Path):
    spec = stage()
    poses = []
    for i, (folder, xml, key, x, yaw) in enumerate(ROBOTS):
        child = mujoco.MjSpec.from_file(str(menagerie / folder / xml))
        alone = child.compile()
        data = mujoco.MjData(alone)
        if key is not None:
            mujoco.mj_resetDataKeyframe(alone, data, mujoco.mj_name2id(alone, mujoco.mjtObj.mjOBJ_KEY, key))
        for name, value in OVERRIDES.get(folder, {}).items():
            data.qpos[alone.jnt_qposadr[alone.joint(name).id]] = value
        # keep each robot's own pose; keyframes are dropped on attach
        poses.append({alone.joint(j).name: data.qpos[alone.jnt_qposadr[j]: alone.jnt_qposadr[j] + _width(alone, j)].copy()
                      for j in range(alone.njnt)})
        for k in list(child.keys):
            child.delete(k)
        quat = [np.cos(np.radians(yaw) / 2), 0, 0, np.sin(np.radians(yaw) / 2)]
        frame = spec.worldbody.add_frame(pos=[x, 0, 0], quat=quat)
        spec.attach(child, frame=frame, prefix=f"r{i}_")
    model = spec.compile()
    data = mujoco.MjData(model)
    for i, pose in enumerate(poses):
        for name, q in pose.items():
            j = model.joint(f"r{i}_{name}")
            adr = model.jnt_qposadr[j.id]
            if model.jnt_type[j.id] == mujoco.mjtJoint.mjJNT_FREE:
                q = q.copy()
                yaw = np.radians(ROBOTS[i][4])
                q[0] += ROBOTS[i][3]
                q[3:7] = [np.cos(yaw / 2), 0, 0, np.sin(yaw / 2)]
            data.qpos[adr: adr + len(q)] = q
    mujoco.mj_forward(model, data)
    return model, data


def _width(model, j):
    return {int(mujoco.mjtJoint.mjJNT_FREE): 7, int(mujoco.mjtJoint.mjJNT_BALL): 4}.get(int(model.jnt_type[j]), 1)


def _crop(img, pad):
    ink = np.argwhere(img.min(axis=2) < 245)
    (y0, x0), (y1, x1) = ink.min(0), ink.max(0)
    h, w = img.shape[:2]
    return img[max(y0 - pad, 0): min(y1 + pad, h), max(x0 - pad, 0): min(x1 + pad, w)]


def render(model, data, w, h, lookat, distance, azimuth, elevation):
    cam = mujoco.MjvCamera()
    cam.lookat[:] = lookat
    cam.distance, cam.azimuth, cam.elevation = distance, azimuth, elevation
    opt = mujoco.MjvOption()
    with mujoco.Renderer(model, height=h, width=w) as r:
        r.update_scene(data, camera=cam, scene_option=opt)
        return r.render()


def main():
    menagerie = Path(sys.argv[1])
    model, data = build(menagerie)
    img = render(model, data, 2800, 1300, lookat=[0.0, 0.1, 0.6], distance=2.9, azimuth=90, elevation=-16)
    # the floor is lit to the background white, so only robots and their shadows survive the crop
    Image.fromarray(_crop(img, pad=60)).save(OUT / "banner.png", optimize=True)
    print("wrote", OUT / "banner.png")


if __name__ == "__main__":
    main()
