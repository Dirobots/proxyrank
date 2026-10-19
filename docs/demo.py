# Typed-out demo for docs/demo.gif; record with docs/record.sh
import sys, time

def type_out(line, delay=0.025):
    for ch in line:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

def step(code, pause=1.2):
    for line in code.strip("\n").splitlines():
        type_out(">>> " + line if not line.startswith(" ") else "... " + line)
    exec(code, globals())
    time.sleep(pause)

type_out("# SIMPLER, Google Robot, pick coke can: 6 policies, 75 real trials each", 0.015)
step("import proxyrank as pr")
step("sim  = [0.857, 0.710, 0.567, 0.787, 0.170, 0.027]")
step("real = [64, 69, 57, 68, 22, 10]   # successes out of 75")
step("print(pr.validate(sim, real, [75] * 6, metric='spearman'))", 3.0)
type_out("# observed 0.771 is below what a perfect simulator would get (0.948), p = 0.03", 0.015)
time.sleep(2.5)
