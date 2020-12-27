from direct.showbase import DirectObject

class NPCManager(DirectObject.DirectObject):

    def __int__(self):
        self.clearNpcData()

    def clearNpcData(self):
        self.npcData = {}

    def addNpcData(self, data):
        for currKey in list(data.keys()):
            self.npcData.setdefault(currKey, {}).update(data[currKey])

    def getNpcData(self, uid):
        return self.npcData.get(uid, {})