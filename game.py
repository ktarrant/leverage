import eventfile

class Game(object):
    
    def __init__(self):
        pass

def processEventFile(fileObj, *gameConsumers):
    """ Processes an event file by assembling a game object for each game in
    the event file using the records for the game. For each game object
    produced, all the gameConsumers will be notified of the game. """
    
    for line in fileObj:
        record = eventfile.unpack(line)
        if record["key"] == "id":
            gameObj = Game()