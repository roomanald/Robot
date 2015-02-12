#!/usr/bin/env/python

class RobotInputBase:
	def Register(self, robot):
		raise NotImplementedError

class RobotInputWiiMote:
	def Register(self, robot):
		print "Registering Wiimote with Robot"

class RobotInputBrain:
	def Register(self, robot):
		print "Registering Brain with Robot"
