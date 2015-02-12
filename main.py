#!/usr/bin/env/python
import robot
import robotInputBase

robot = robot.Robot()
robot.Start(robotInputBase.RobotInputWiiMote())
#robot.Start(robotInputBase.RobotInputBrain())
raw_input("press any key to stop...")
robot.Stop()

