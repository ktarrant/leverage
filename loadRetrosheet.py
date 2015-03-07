import urllib2
import zipfile
import hashlib
import os
import re
import eventfile

# List of URL's to process - usually a year per URL

url_list = [
	"http://www.retrosheet.org/events/2014eve.zip"
]

# Some regex helpers
eventName = re.compile(r"([0-9]{4})([A-Z]{3})\.EV(A|N)")

def downloadFile(url):
	extension = url.split(".")[-1]
	m = hashlib.md5()
	m.update(url)
	file_name = m.hexdigest() + "." + extension
	if os.path.exists(file_name):
		print "File already downloaded: " + file_name
		return file_name

	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	maxStatusCol = len(str(file_size)) + len("[100.00%]")
	maxProgCol = 32
	file_size_dl = 0
	block_sz = 8192
	while True:
	    buffer = u.read(block_sz)
	    if not buffer:
	        break

	    file_size_dl += len(buffer)
	    f.write(buffer)
	    percentDone = float(file_size_dl) / float(file_size)
	    status = ("%-" + str(maxStatusCol + 6) + "s") % \
	    	(r"%10d  [%3.2f%%]" % (file_size_dl, percentDone * 100.))
	    progressValue = int(percentDone * maxProgCol)
	    status += " [" + "#"*progressValue + \
	    	(maxProgCol - progressValue) * " " + "]"
	    print status

	f.close()
	print "Saved to: " + file_name
	return file_name

def loadTeamLogs(zipPath):
	zipFile = zipfile.ZipFile(zipPath)
	for zipInfo in zipFile.infolist():
		with zipFile.open(zipInfo) as zipElem:
			match = eventName.match(zipInfo.filename)
			if match != None:
				# print "Year: " + match.group(1)
				# print "Team: " + match.group(2)
				# print "League: " + match.group(3)
				if "WAS" in zipInfo.filename:
					eventfile.processEventLog(zipElem)

if __name__ == "__main__":
	for url in url_list:
		filename = downloadFile(url)
		loadTeamLogs(filename)