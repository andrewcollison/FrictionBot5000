from tracemalloc import start
from motorInterface import motorInterface
import time

class motorControl():
    # def __init__(self, homeP, minP, maxP):
    #     self.homePosition = homeP
    #     self.minPosition = minP
    #     self.maxPosition = maxP

    def move2target(self, target):
        motorInterface.startMotor()
        motorInterface.moveMotor(target)
        currTarget = motorInterface.getTarget()
        currPos = motorInterface.getFeedback()
        moe = 10
        timeout = 10   # [seconds]
        timeout_start = time.time()
        while True:
                if abs(currTarget - currPos) > moe:
                    print('motor in transit')
                    print(abs(currTarget - currPos)) 
                    time.sleep(0.5)
                    currTarget = motorInterface.getTarget()
                    currPos = motorInterface.getFeedback()
                elif abs(currTarget - currPos) < moe:
                    print("Motor at target")
                    motorInterface.stopMotor()
                    return 'Motor at Target'
                if time.time() < timeout_start + timeout:
                    return "Motor movement error"
                
    
    # def motorAtTarget():
    #     if abs(currTarget - currPos) > moe:
    #                 print('motor in transit')
    #                 print(abs(currTarget - currPos)) 
    #                 time.sleep(0.5)
    #                 currTarget = motorInterface.getTarget()
    #                 currPos = motorInterface.getFeedback()
    #                 return ''
    #             elif abs(currTarget - currPos) < moe:
    #                 print("Motor at target")

        
