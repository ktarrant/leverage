# Calculate PARK FACTOR

# Step 1. Find games, losses, and runs scored and allowed for each team at home 
# and on the road. Take runs per game scored and allowed at home over runs per 
# game scored and allowed on the road. This is the initial figure, but we must 
# make two corrections to it.

import sqlite3
import os

database_dir = "./lahman-csv_2015-01-24"
database_name = "Teams.csv"
database_fn = os.path.join(database_dir, database_name)

team_count = 30


def getParkStats():
	with open(database_fn, "r") as fobj:
		contents = fobj.read()

	table = [[entry.strip() for entry in line.split(",")] for \
		line in contents.split("\n")]

	headers = table[0] # row 0 contains the names of the values

	recent = [ { key : value for (key, value) in zip(headers, row) } for \
		row in table[- (team_count + 1):] ]

	parkStats = { team["park"] : (team["BPF"], team["PPF"]) \
		for team in recent if "park" in team }

	return parkStats


print getParkStats()

def makeComment(string):
	words = string.split(" ")
	lines = ["# "]
	colmax = 80


	for word in words:
		piece = word + " "
		if len(piece) + len(lines[-1]) > colmax:
			lines += ["# "]

		lines[-1] += piece

	return "\n".join(lines)