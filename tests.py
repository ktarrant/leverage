from descriptor import RecordDescriptor, ParseError
import eventfile
import unittest


class TestRecordUnpacking(unittest.TestCase):
    
    def setUp(self):
    	# Create a descriptor for an "info" record
    	self.desc = RecordDescriptor(RecordDescriptor.INFO_RECORD)
    	info_keys = ["id", "name", "age", "likes"]
    	self.desc.add_arg("%s", "key")
    	self.desc.add_arg("%3d%s%3d%2s", *info_keys)
    	self.desc.add_arg("%s", "loneStr")
    	self.desc.add_arg("%2d", "loneInt")
    	self.expected_keys = ["key"] + info_keys + ["loneStr", "loneInt"]
    	
    def testNormalUnpack(self):
        record = "info,123doggie456xx,cat,44"
    	result = self.desc.unpack(record)
    	# Every key defined in the descriptor should be a key in the result
    	# of an unpack command.
    	for key in self.expected_keys:
    	    self.assertIn(key, result)
    	gen_rec = self.desc.pack(**result)
    	# A packed and then unpacked record should be identical to the original
    	# record.
    	self.assertEqual(record, gen_rec)

    def testEmptyVarString(self):
        record = "info,123456xx,dog,67"
    	result = self.desc.unpack(record)
    	# Every key defined in the descriptor should be a key in the result
    	# of an unpack command.
    	for key in self.expected_keys:
    	    self.assertIn(key, result)
    	gen_rec = self.desc.pack(**result)
    	# A packed and then unpacked record should be identical to the original
    	# record.
    	self.assertEqual(record, gen_rec)
    	# The variable-length field should be empty in this case
    	self.assertEqual(result["name"], "")
    	
    def testEmptyStrField(self):
        record = "info,123pudding456xx,,67"
    	result = self.desc.unpack(record)
    	# Every key defined in the descriptor should be a key in the result
    	# of an unpack command.
    	for key in self.expected_keys:
    	    self.assertIn(key, result)
    	gen_rec = self.desc.pack(**result)
    	# A packed and then unpacked record should be identical to the original
    	# record.
    	self.assertEqual(record, gen_rec)
    	# The lone string field should be empty in this case
    	self.assertEqual(result["loneStr"], "")
    	
    def testEmptyIntField(self):
        record = "info,123pudding456xx,dog,"
        # An empty int field should cause an exception
        self.assertRaises(ParseError, self.desc.unpack, record)
        
    def testMissingField(self):
        record="info,123pudding456xx,dog"
        # We are missing our last field, shoud cause an exception
        self.assertRaises(ParseError, self.desc.unpack, record)
        
    def testMissingSubfield(self):
        record="info,123pudding456,dog,12"
        # We are missing the "likes" field, shoud cause an exception
        self.assertRaises(ParseError, self.desc.unpack, record)
        
class TestEventfileUnpacking(unittest.TestCase):
    
    def testInfo(self):
        self.assertEqual(eventfile.unpack("info,sky,overcast"), \
            {"key": "info", "infoKey": "sky", "infoValue": "overcast"})
            
        self.assertEqual(eventfile.unpack("info,timeofgame,183"), \
            {"key": "info", "infoKey": "timeofgame", "infoValue": "183"})
		    
    def testPlay(self):
	    # unpack play test
	    self.assertEqual(eventfile.unpack( \
            "play,5,1,ramir001,00,,S8.3-H;1-2"), \
            {"key": "play", "inning": 5, "homeTeam": 1, "playerId": "ramir001",\
            "count": "00", "pitches": "", "event": "S8.3-H;1-2"})
    		
    def testVersion(self):
	    # unpack version test
	    self.assertEqual(eventfile.unpack("version,2"), \
	        {"key": "version", "version": 2})
    
    def testId(self):
        self.assertEqual(eventfile.unpack("id,WAS201404040"), \
		    {"key": "id", "id": "WAS201404040"})
		   
    def testStart(self):
        self.assertEqual(eventfile.unpack( \
            "start,heywj001,\"Jason Heyward\",0,1,9"), \
            {"key": "start", "playerId": 'heywj001', \
            "playerName": '"Jason Heyward"', "homeTeam": 0, \
            "batNum": 1, "fieldNum": 9})
    
        self.assertEqual(eventfile.unpack( \
            "start,zimmj003,\"Jordan Zimmermann\",1,0,1"), \
            {"key": "start", "playerId": "zimmj003", \
            "playerName": '"Jordan Zimmermann"', "homeTeam": 1, \
            "batNum": 0, "fieldNum": 1})
        
if __name__ == "__main__":
    descriptorSuite = \
        unittest.TestLoader().loadTestsFromTestCase(TestRecordUnpacking)
    eventfileSuite = \
        unittest.TestLoader().loadTestsFromTestCase(TestEventfileUnpacking)
    allTests = unittest.TestSuite([descriptorSuite, eventfileSuite])
    unittest.TextTestRunner(verbosity=2).run(allTests)