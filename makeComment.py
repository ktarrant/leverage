inputString = """

com The final record type is used primarily to add explanatory information for a play. However, it may occur anywhere in a file. The second field of the com record is quoted.

com,"ML debut for Behenna"
There is a standard record ordering for each game. An id record starts the description of a particular game. This is followed by the version and info records. The start records follow the info records. The game is described by a series of play, sub and com records. A sub record is always preceded by a play np record. data records follow the last play record for the game. A game description is terminated by an id record starting another game or the end of the file.

"""

RULER_WIDTH = 80
TAB_WIDTH 	= 4
CMNT_WIDTH	= 2 # Width of " #"
TAB_LEVEL	= 1
TEXT_WIDTH	= RULER_WIDTH - (TAB_LEVEL * TAB_WIDTH + CMNT_WIDTH)

import textwrap
w = textwrap.TextWrapper(width=TEXT_WIDTH, \
	break_long_words=False,
	replace_whitespace=False)
print "\n".join(w.wrap(inputString))



