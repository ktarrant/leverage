from descriptor import RecordDescriptor

def makeIdDescriptor():
	# id - Each game begins with a twelve character ID record which identifies 
	# the date, home team, and number of the game. For example, ATL198304080 
	# should be read as follows. The first three characters identify the home 
	# team (the Braves). The next four are the year (1983). The next two are 
	# the month (April) using the standard numeric notation, 04, followed by 
	# the day (08). The last digit indicates if this is a single game (0), 
	# first game (1) or second game (2) if more than one game is played during 
	# a day, usually a double header The id record starts the description of a 
	# game thus ending the description of the preceding game in the file
	desc = RecordDescriptor(RecordDescriptor.INFO_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "id")
	return desc

def makeInfoDescriptor():
	# info There are up to 34 info records, each of which contains a single 
	# piece of information, such as the temperature, attendance, identity of 
	# each umpire, etc. The record format is info,type,data . The complete list 
	# of info record types is given below. 
	# Format is info, key, value
	desc = RecordDescriptor(RecordDescriptor.INFO_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "infoKey")
	desc.add_arg("%s", "infoValue")
	return desc

def makeVersionDescriptor():
	# version - The version record is next, but is obsolete and can be ignored.
	desc = RecordDescriptor(RecordDescriptor.INFO_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%1d", "version")
	return desc

def makeStartDescriptor(ftype=RecordDescriptor.INFO_RECORD):
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
	desc = RecordDescriptor(ftype)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "playerId")
	desc.add_arg("%s", "playerName")
	desc.add_arg("%1d", "homeTeam")
	desc.add_arg("%d", "batNum")
	desc.add_arg("%d", "fieldNum")
	return desc

def makePlayDescriptor():
	# play The play records contain the events of the game. Each play record
	# has 7 fields.

	# 1. The first field is the inning, an integer starting at 1.
	# 2. The second field is either 0 (for visiting team) or 1 (for home team).
	# 3. The third field is the Retrosheet player id of the player at the plate.
	# 4. The fourth field is the count on the batter when this particular event
	# (play) occurred. Most Retrosheet games do not have this information, and
	# in such cases, "??" appears in this field.
	# 5. The fifth field is of variable length and contains all pitches to this 
	# batter in this plate appearance and is described below. If pitches are 
	# unknown, this field is left empty, nothing is between the commas.
	# 6. The sixth field describes the play or event that occurred.

	# play,5,1,ramir001,00,,S8.3-H;1-2
	# A play record ending in a number sign, #, indicates that there is some
	# uncertainty in the play. Occasionally, a com record may follow providing
	# additional information. A play record may also contain exclamation points,
	# "!" indicating an exceptional play and question marks "?" indicating some
	# uncertainty in the play. These characters can be safely ignored.
	# play,3,1,kearb001,??,,PB.2-3#
	# com,"Not sure if PB, may have been balk"
	# The event is the most complex of all the fields and is described in detail
	# here: http://www.retrosheet.org/eventfile.htm#5
	desc = RecordDescriptor(RecordDescriptor.EVENT_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%d", "inning")
	desc.add_arg("%1d", "homeTeam")
	desc.add_arg("%s", "playerId")
	desc.add_arg("%2s", "count")
	desc.add_arg("%s", "pitches")
	desc.add_arg("%s", "event")
	return desc

def makeAdjDescriptor(adjType):
	# badj This record is used to mark a plate appearance in which the batter
	# bats from the side that is not expected ("badj" means "batting
	# adjustment"). The syntax is:

	# badj,playerid,hand
	# The expectation is defined by the roster file. There are two general cases
	# in which this is used:

	# 1. Many switch-hitters bat right-handed against right-handed
	# knuckle ball pitchers even though the default assumption is that they
	# would be batting left-handed.

	# badj,bonib001,R
	# indicates that switch-hitter Bobby Bonilla was batting right-handed 
	# against a right-handed pitcher.

	# 2. Occasionally a player will be listed in a roster as batting
	# "R" or "L" but will bat the other way. For example, Rick Dempsey did this
	# 13 times in 1983. The syntax this is: badj,dempr101,L

	# padj This record covers the very rare case in which a pitcher pitches to 
	# a batter with the hand opposite the one listed in the roster file. To date
	# this has only happened once, when Greg Harris of the Expos, a 
	# right-hander, pitched left-handed to two Cincinnati batters on 9-28-1995. 
	# The syntax is parallel to that for the badj record: padj,harrg001,L

	# ladj This record is used when teams bat out of order.
	adjTypes = ["p", "b", "l"]
	assert adjType in adjTypes, "Must be one of: [%s]" % ",".join(adjTypes)
	desc = RecordDescriptor(RecordDescriptor.EVENT_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "playerId")
	desc.add_arg("%1s", "hand")
	return desc

def makeDataDescriptor():
	# bdata Data records appear after all play records from the game. At
	# present, the only data type, field 2, that is defined specifies the number
	# of earned runs allowed by a pitcher. Each such record contains the
	# pitcher's Retrosheet player id and the number of earned runs he allowed.
	# There is a data record for each pitcher that appeared in the game.
	# data,er,showe001,2
	desc = RecordDescriptor(RecordDescriptor.INFO_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "dataKey")
	desc.add_arg("%s", "playedId")
	desc.add_arg("%d", "earnedRuns")
	return desc

def makeComDescriptor():
	# com The final record type is used primarily to add explanatory
	# information for a play. However, it may occur anywhere in a file. The
	# second field of the com record is quoted.

	# com,"ML debut for Behenna"
	# There is a standard record ordering for each game. An id record starts the
	# description of a particular game. This is followed by the version and info
	# records. The start records follow the info records. The game is described
	# by a series of play, sub and com records. A sub record is always preceded
	# by a play np record. data records follow the last play record for the
	# game. A game description is terminated by an id record starting another
	# game or the end of the file.
	desc = RecordDescriptor(RecordDescriptor.EVENT_RECORD)
	desc.add_arg("%s", "key")
	desc.add_arg("%s", "msg")
	return desc

EVENT_DESCRIPTOR = {
	"id"		: makeIdDescriptor(),
	"info"		: makeInfoDescriptor(),
	"version"	: makeVersionDescriptor(),
	"start"		: makeStartDescriptor(ftype=RecordDescriptor.INFO_RECORD),
	"sub"		: makeStartDescriptor(ftype=RecordDescriptor.EVENT_RECORD),
	"play"		: makePlayDescriptor(),
	"badj"		: makeAdjDescriptor("b"),
	"padj"		: makeAdjDescriptor("p"),
	"ladj"		: makeAdjDescriptor("l"),
	"data"		: makeDataDescriptor(),
	"com"		: makeComDescriptor()
}

def unpack(recordLine):
	""" Unpacks a record line from an event file. The format of the record
	is derived from the first field of the event file, called the "key", which
	indicates the type of record the record line is. """
	key = recordLine.split(",")[0]
	desc = EVENT_DESCRIPTOR[key]
	return desc.unpack(recordLine)

def pack(key, **kargs):
	""" Packs a record into a record line. The format of the record line is
	derived from the key parameter."""
	desc = EVENT_DESCRIPTOR[key]
	return desc.pack(**kargs)