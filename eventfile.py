MAX_LINES = 256

def tryInt(strInt):
	try:
		return int(strInt)
	except ValueError:
		return strInt

# Make a hierarchy dict
class hidict(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __setitem__(self, key, value):
		if isinstance(value, hidict) and key in self and \
			isinstance(self[key], hidict):

			self[key].update(value)
		else:
			super(hidict, self).__setitem__(key, value)

    def update(self, *args, **kwargs):
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, "
                                "got %d" % len(args))
            other = dict(args[0])
            for key in other:
                self[key] = other[key]
        for key in kwargs:
            self[key] = kwargs[key]

    def setdefault(self, key, value=None):
        if key not in self:
            self[key] = value
        return self[key]

    def __str__(self):
    	return "hidict: " + super(hidict, self).__str__()

# decorator for automatically making hierarchal results from returned dict
def makehidict(func):

	def inner(fields): # Input functions always take fields as an input
		badict = func(fields)
		newdict = hidict(badict)
		newdict = subhidict(newdict)
		return newdict

	return inner


@makehidict
def processId(fields):
	# id - Each game begins with a twelve character ID record which identifies 
	# the date, home team, and number of the game. For example, ATL198304080 
	# should be read as follows. The first three characters identify the home 
	# team (the Braves). The next four are the year (1983). The next two are 
	# the month (April) using the standard numeric notation, 04, followed by 
	# the day (08). The last digit indicates if this is a single game (0), 
	# first game (1) or second game (2) if more than one game is played during 
	# a day, usually a double header The id record starts the description of a 
	# game thus ending the description of the preceding game in the file. 
	idstr = fields[1]
	rval = {}
	keys = ("team", "year", "month", "day", "multigame")
	values = (idstr[0:3], \
			int(idstr[3:7]), int(idstr[7:9]), int(idstr[9:11]), \
			int(idstr[11]))

	return { key : value for (key, value) in zip(keys, values)}

@makehidict
def processVersion(fields):
	# version - The version record is next, but is obsolete and can be ignored.
	return {}

@makehidict
def processInfo(fields):
	# info There are up to 34 info records, each of which contains a single 
	# piece of information, such as the temperature, attendance, identity of 
	# each umpire, etc. The record format is info,type,data . The complete list 
	# of info record types is given below. 
	# Format is info, key, value
	key = fields[1]
	value = tryInt(fields[2]) # Try to make it an int - else, leave it
	return {key: value}

@makehidict
def processStart(fields):
	# start and sub  There are 18 (for the NL and pre-DH AL) or 20 (for the AL 
	# with the DH) start records, which identify the starting lineups for the 
	# game. Each start or sub record has five fields. The sub records are used 
	# when a player is replaced during a game. The roster files that accompany 
	# the event files include throwing and batting handedness information.
	# 1. The first field is the Retrosheet player id, which is unique for each 
	#  player.
	# 2. The second field is the player's name.
	# 3. The next field is either 0 (for visiting team), or 1 (for home team).
	# 4. The next field is when a game is played using the the position in
	#  the batting order, 1 - 9. DH rule the pitcher is given the batting
	#  order position 0.
	# 5. The last field is the fielding position. The numbers are in the 
	#  standard notation, with designated hitters being identified as position
	#  10. On sub records 11 indicates a pinch hitter and 12 is used for a 
	#  pinch runner. 
	keys = ["playerId", "playerName", "homeTeam", "fieldNum"]
	values = [fields[1], fields[2], int(fields[3]), int(fields[5])]
	batNum = int(fields[4])

	return hidict({ "start" : hidict({batNum: {key: value for \
		(key, value) in zip(keys, values)}}) })


def subhidict(d):
	for key in d:
		if isinstance(d[key], dict):
			d[key] = hidict(d[key])
			d[key] = subhidict(d[key])
	return d

def process(fields):
	func_name = "process" + fields[0][0].upper() + fields[0][1:]
	try:
		value = eval(func_name)(fields)
	except NameError:
		# TODO: Make this an error, since every record type should be known
		# eventually.
		print "Record type not processed: " + func_name
		value = {}

	value = subhidict(hidict(value))
	return value

def processEventLog(fobj):
	games = []
	game = None
	lineCount = 0
	for line in fobj:
		fields = [field.strip() for field in line.split(",")]
		print fields

		# Special case for id - indicates start of new game
		if fields[0] == "id":
			if game != None:
				print game # Reap the rewards...
				games += [game]
			game = hidict()

		# Find the process function for this key
		game.update(process(fields))

		# TODO: Remove line limit
		lineCount += 1
		if lineCount == MAX_LINES:
			print "Quitting after processing %d lines" % MAX_LINES
			exit()

if __name__ == "__main__":
	def assertEqual(a, b):
		try:
			assert a == b
		except AssertionError, e:
			e.args += (a, b)
			raise e

	assertEqual(process(['id', 'WAS201404040']), \
		{"team": "WAS", "year": 2014, "month": 4, "day": 4, "multigame": 0})
	# processVersion test
	assertEqual(process(['version', '2']), {})
	# processInfo test
	assertEqual(process(['info', 'sky', 'overcast']), {'sky': 'overcast'})
	assertEqual(process(['info', 'timeofgame', '183']), {'timeofgame': 183})
	# processStart test
	# Lead-Off hitter
	assertEqual( \
		process(['start', 'heywj001', '"Jason Heyward"', '0', '1', '9']), \
		{"start": {1: \
		{"playerId": 'heywj001', \
		 "playerName": '"Jason Heyward"', \
		 "homeTeam": 0, "fieldNum": 9}} })
	# Pitcher in DH-mode - batNum 0
	assertEqual( \
		process(['start', 'zimmj003', '"Jordan Zimmermann"', '1', '0', '1']),\
		{"start": {0: {'playerId': 'zimmj003', \
			'playerName': '"Jordan Zimmermann"', \
			'homeTeam': 1, 'fieldNum': 1}}})


