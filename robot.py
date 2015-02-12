#!/usr/bin/env/python

class Robot:
	isStarted = False

	def Start(self, input):
		if self.isStarted:
			raise Exception("already started") 
		print "robot started"
		input.Register(self)
		self.isStarted = True
	def Stop(self):
		self.isStarted = False
		print "robot stopped"
	def MoveFwd(self):
		print "robot moving forward"
	def MoveBwd(self):
		print "robot moving backward"
	def MoveLeft(self):
		print "robot moving left"
	def MoveRight(self):
		print "robot moving right"
	
