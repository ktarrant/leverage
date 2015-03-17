import eventfile
from descriptor import RecordDescriptor

class Game(object):
    
    def __init__(self, gameId):
        self.gameId = gameId
        self.starters = {}
        self.infos = {}
        self.events = []
        self.coms = {}
        self.ERs = {}

    def addInfoRecord(self, record):
    	rk = record["key"]
    	if rk == "info":
    		self.infos[record["infoKey"]] = record["infoValue"]
    	elif rk == "start":
    		self.starters[record["batNum"]] = record
    	elif rk == "data":
    		self.ERs[record["playerId"]] = record["earnedRuns"]
    	else:
    		#print "Did not process record with key: %s" % rk
    		pass

    def addEventRecord(self, record):
    	if record["key"] == "com":
    		self.coms[len(self.events)] = record["msg"]
    	else:
    		self.events += [record]

def processEventFile(fileObj, *gameConsumers):
    """ Processes an event file by assembling a game object for each game in
    the event file using the records for the game. For each game object
    produced, all the gameConsumers will be notified of the game. """
    
    gameObj = None
    for line in fileObj:
        record = eventfile.unpack(line)
        if record["key"] == "id":
			# Give the game consumers the old game object
			if gameObj != None:
				for consumer in gameConsumers:
					consumer.process(gameObj)

				print "Exiting @ game.processEventFile"
				exit()

			gameObj = Game(record["id"])
        elif eventfile.getRecordType(record["key"]) == \
        	RecordDescriptor.INFO_RECORD:
        	gameObj.addInfoRecord(record)
        else:
        	gameObj.addEventRecord(record)




