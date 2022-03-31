import subprocess
import time
from types import ModuleType

class motorInterface():
    def moveMotor(self, target):
        subprocess.run('jrkcmd --clear-errors --target {target} --pause-on-error'.format(target = target))

    def startMotor(self):
        subprocess.run('jrkcmd --start')
    
    def stopMotor(self):
        subprocess.run('jrkcmd --stop')

    def getPos(self):
        currPos = subprocess.run(
            ['jrkcmd', '--clear-errors', '--stream', '--noheader','--limit', '1', '--format', '"{5,5}"'], 
            capture_output=True, text=True
            )
        currPos = str(currPos.stdout).strip("'\n")
        currPos = currPos.strip('"')
        currPos = currPos.replace(" ", "")
        print(currPos)
        return int(currPos)

    def getTarget(self):
        currTarget = subprocess.run(
            ['jrkcmd', '--clear-errors', '--stream', '--noheader','--limit', '1', '--format', '"{3,3}"'], 
            capture_output=True, text=True
            )
        currTarget = str(currTarget.stdout).strip("'\n")
        currTarget = currTarget.strip('"')
        currTarget = currTarget.replace(" ", "")
        print(currTarget)
        return int(currTarget)
