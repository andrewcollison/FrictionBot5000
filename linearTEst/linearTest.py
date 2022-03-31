import subprocess
import time
from types import ModuleType

class motorControl():
    def __init__(self, homeP, minP, maxP):
        self.homePosition = homeP
        self.minPosition = minP
        self.maxPosition = maxP

    def move2target(self, target):
        subprocess.run('jrkcmd --clear-errors --target {target} --pause-on-error'.format(target = target))

    def getFeedback(self):
        currPos = subprocess.run(
            ['jrkcmd', '--clear-errors', '--stream', '--noheader','--limit', '1', '--format', '"{5,5}"'], 
            capture_output=True, text=True
            )
        return currPos.stdout

    def getTarget(self):
        currTarget = subprocess.run(
            ['jrkcmd', '--clear-errors', '--stream', '--noheader','--limit', '1', '--format', '"{3,3}"'], 
            capture_output=True, text=True
            )
        return currTarget.stdout
           
    def move2home(self):
        subprocess.run('jrkcmd --clear-errors --target {target} --pause-on-error'.format(target = self.homePosition))


def main():
    motorPlan = motorControl(100, 100, 3500)
    # print("Move to home position")
    motorPlan.move2target(666)
    time.sleep(1)
    print("target location" + motorPlan.getTarget())
    # motorPlan.move2home()
    # time.sleep(10)
    # while(1):
    #     print("Target 100")
    #     motorPlan.move2target(100)
    #     time.sleep(10)
    #     print("Target 3000")
    #     motorPlan.move2target(3000)
    #     time.sleep(10)    
    # subprocess.run("dir")


main()


# import subprocess
# import sys

# result = subprocess.run(
#     ['jrkcmd', '--clear-errors', '--stream', '--noheader','--limit', '1', '--format', '"{3,3}"'], capture_output=True, text=True
# )
# print("stdout:", result.stdout)
# print("stderr:", result.stderr)