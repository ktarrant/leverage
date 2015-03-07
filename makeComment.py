import sys

def usage():
	name = sys.argv[0].split("/")[-1]
	print "Usage: " + name + " <string>"
	print "Prints a comment formatted version of string to stdout."

def makeComment(string, colmax=80):
	words = string.split(" ")
	lines = ["# "]

	for word in words:
		piece = word + " "
		if len(piece) + len(lines[-1]) > colmax:
			lines += ["# "]

		lines[-1] += piece

	return "\n".join(lines)

contents = sys.stdin.read()

if len(contents) == 0:
	usage()
	exit()
if len(sys.argv) == 2:	
	colmax = int(sys.argv[1])
	print makeComment(contents, colmax)
else:
	print makeComment(contents)

