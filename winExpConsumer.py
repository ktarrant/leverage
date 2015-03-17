import game
import re

# some regex helpers for parsing the event information
modRe = re.compile(r"(/|\.)([A-Za-z0-9\-])")
foutRe = re.compile(r"([0-9]+)(\(([1-3]|B)\))?")

class GameConsumer(object):

	def __init__(self):
		self.reset()

	def reset(self):
		self.gameObj = None # Handled by the process task
		self.state = { "vR" : 0, "hR" : 0, \
			"i" : 1, "o" : 0, \
			"1b" : None, "2b" : None, "3b" : None }

	def buildState(self, eventStr):
		foutMatch = foutRe.match(eventStr)
		if foutMatch == None:
			# TODO: process other formats
			return self.state
		else:
			# Handle outs that were fielded
			for match in foutRe.finditer(eventStr):
				print match.group(0),
			return self.state

	def processPlay(self, record):
		eventStr = record["event"]
		match = modRe.search(eventStr)

		# Look for modifiers and use the beginning for the play type
		if match == None: playType = eventStr
		else: playType = eventStr[:match.start(0)] 

		# Read in all the modifiers and base runners
		mods = []
		movs = []
		while match != None:
			if match.group(1) == "/":
				mods += [match.group(2)]
			elif match.group(1) == ".":
				movs += [match.group(2)]
			match = modRe.search(eventStr, match.end(0))

		# Figure out the new state based on the play type
		newState = self.buildState(playType)
		


	def process(self, gameObj):
		self.reset()
		self.gameObj = gameObj

		print gameObj.infos["date"],
		for record in gameObj.events:
			if record["key"] == "play":
				if record["inning"] != self.state["i"]:
					self.state["i"] = record["inning"]
					print "\n%d: " % record["inning"],
				self.processPlay(record)
		print ""



