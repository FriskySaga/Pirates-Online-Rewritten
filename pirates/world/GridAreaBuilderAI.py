from pirates.world.AreaBuilderBaseAI import AreaBuilderBaseAI
from direct.directnotify.DirectNotifyGlobal import directNotify
from pirates.piratesbase import PiratesGlobals
from pirates.leveleditor import ObjectList
from pirates.interact.DistributedSearchableContainerAI import DistributedSearchableContainerAI
from pirates.minigame.DistributedFishingSpotAI import DistributedFishingSpotAI
from pirates.minigame.DistributedPotionCraftingTableAI import DistributedPotionCraftingTableAI
from pirates.minigame.DistributedRepairBenchAI import DistributedRepairBenchAI
from pirates.world.DistributedBuildingDoorAI import DistributedBuildingDoorAI
from pirates.world.DistributedDinghyAI import DistributedDinghyAI
from pirates.treasuremap.DistributedBuriedTreasureAI import DistributedBuriedTreasureAI
from pirates.treasuremap.DistributedSurfaceTreasureAI import DistributedSurfaceTreasureAI

class GridAreaBuilderAI(AreaBuilderBaseAI):
    notify = directNotify.newCategory('GridAreaBuilderAI')

    def __init__(self, air, parent):
        AreaBuilderBaseAI.__init__(self, air, parent)
        self.wantSearchables = config.GetBool('want-searchables', True)
        self.wantFishing = config.GetBool('want-fishing-game', True)
        self.wantPotionTable = config.GetBool('want-potion-game', False)
        self.wantBuildingInteriors = config.GetBool('want-building-interiors', True)
        self.wantDinghys = config.GetBool('want-dignhys', True)
        self.wantSpawnNodes = config.GetBool('want-spawn-nodes', False)
        self.wantRepairBench = config.GetBool('want-repair-game', True)
        self.wantIslandAreas = config.GetBool('want-island-game-areas', True)

    def createObject(self, objType, objectData, parent, parentUid, objKey, dynamic):
        newObj = None

        if objType == 'Searchable Container' and self.wantSearchables:
            newObj = self.__generateSearchableContainer(parent, parentUid, objKey, objectData)
        elif objType == 'FishingSpot' and self.wantFishing:
            newObj = self.__generateFishingSpot(parent, parentUid, objKey, objectData)
        elif objType == 'PotionTable' and self.wantPotionTable:
            newObj = self.__generatePotionTable(parent, parentUid, objKey, objectData)
        elif objType in ['Animal', 'Townsperson', 'Spawn Node', 'Dormant NPC Spawn Node', 'Skeleton', 'NavySailor', 'Creature', 'Ghost']:
            newObj = self.air.spawner.createObject(objType, objectData, parent, parentUid, objKey, dynamic)
        elif objType == 'Building Exterior' and self.wantBuildingInteriors:
            newObj = self.__generateBuildingExterior(parent, parentUid, objKey, objectData)
        elif objType == 'Dinghy' and self.wantDinghys:
            newObj = self.__generateDinghy(parent, parentUid, objKey, objectData)
        elif objType == 'Object Spawn Node' and self.wantSpawnNodes:
            newObj = self.__generateObjectSpawnNode(parent, parentUid, objKey, objectData)
        elif objType == 'RepairBench' and self.wantRepairBench:
            newObj = self.__generateRepairBench(parent, parentUid, objKey, objectData)
        elif objType == ObjectList.AREA_TYPE_ISLAND_REGION and self.wantIslandAreas:
            newObj = self.__generateIslandArea(parent, parentUid, objKey, objectData)

        return newObj

    def __generateSearchableContainer(self, parent, parentUid, objKey, objectData):
        container = DistributedSearchableContainerAI(self.air)
        container.setUniqueId(objKey)
        container.setPos(objectData.get('Pos', (0, 0, 0)))
        container.setHpr(objectData.get('Hpr', (0, 0, 0)))
        container.setScale(objectData.get('Scale', (1, 1, 1)))
        container.setType(objectData.get('type', 'Crate'))

        if 'Visual' in objectData and 'Color' in objectData['Visual']:
            container.setContainerColor(objectData['Visual'].get('Color', (1.0, 1.0, 1.0, 1.0)))

        container.setSearchTime(float(objectData.get('searchTime', '6.0')))
        container.setVisZone(objectData.get('VisZone', ''))
        container.setSphereScale(float(objectData.get('Aggro Radius', 1.0)))

        parent.generateChildWithRequired(container, PiratesGlobals.IslandLocalZone)
        self.addObject(container)
        self.broadcastObjectPosition(container)

        return container

    def __generateFishingSpot(self, parent, parentUid, objKey, objectData):
        fishingSpot = DistributedFishingSpotAI(self.air)
        fishingSpot.setPos(objectData.get('Pos', (0, 0, 0)))
        fishingSpot.setHpr(objectData.get('Hpr', (0, 0, 0)))
        fishingSpot.setScale(objectData.get('Scale', (1, 1, 1)))
        fishingSpot.setOceanOffset(float(objectData.get('Ocean Offset', 1)))

        parent.generateChildWithRequired(fishingSpot, PiratesGlobals.IslandLocalZone)
        self.addObject(fishingSpot)
        self.broadcastObjectPosition(fishingSpot)

        return fishingSpot

    def __generatePotionTable(self, parent, parentUid, objKey, objectData):
        table = DistributedPotionCraftingTableAI(self.air)
        table.setPos(objectData.get('Pos', (0, 0, 0)))
        table.setHpr(objectData.get('Hpr', (0, 0, 0)))
        table.setScale(objectData.get('Scale', (1, 1, 1)))

        parent.generateChildWithRequired(table, PiratesGlobals.IslandLocalZone)
        self.addObject(table)
        self.broadcastObjectPosition(table)

        return table

    def __generateBuildingExterior(self, parent, parentUid, objKey, objectData):
        from pirates.world.DistributedJailInteriorAI import DistributedJailInteriorAI
        from pirates.world.DistributedGAInteriorAI import DistributedGAInteriorAI

        interiorFile = objectData.get('File', None)
        exteriorUid = objectData.get('ExtUid', None)

        if not interiorFile:
            return None

        interiorModel = self.air.worldCreator.getModelPathFromFile(interiorFile)
        if not interiorModel:
            self.notify.warning('Failed to spawn interior: %s; No interior model found in %s.' % (objKey, interiorFile))
            return None

        # allocate a new zone for this interior
        interiorZone = self.air.allocateZone()

        if 'Jail' in interiorFile:
            interiorClass = DistributedJailInteriorAI
        else:
            interiorClass = DistributedGAInteriorAI

        interior = interiorClass(self.air)
        interior.setUniqueId(exteriorUid)
        interior.setModelPath(interiorModel)
        interior.setName(interior.getLocalizerName())

        parent.generateChildWithRequired(interior, interiorZone)
        self.addObject(interior)

        # Create exterior doors
        foundDoor = False
        if 'Objects' in objectData:
            for childKey, childData in objectData['Objects'].items():
                childType = childData.get('Type', '')
                if childType == 'Door Locator Node':
                    extDoor = DistributedBuildingDoorAI(self.air)

                    extDoor.setUniqueId(childKey)
                    extDoor.setPos(childData.get('Pos', (0, 0, 0)))
                    extDoor.setHpr(childData.get('Hpr', (0, 0, 0)))
                    extDoor.setScale(childData.get('Scale', (1, 1, 1)))

                    extDoor.setInteriorId(interior.doId, interior.getUniqueId(), interior.parentId, interior.zoneId)
                    extDoor.setBuildingUid(objKey)

                    parent.generateChildWithRequired(extDoor, PiratesGlobals.IslandLocalZone)

                    foundDoor = True

        if not foundDoor:
            self.notify.warning('%s (%s) has an interior, but no exterior door was found!' % (interior.getLocalizerName(), objKey))

        self.air.worldCreator.loadObjectsFromFile(interiorFile + '.py', interior)

        return interior

    def __generateDinghy(self, parent, parentUid, objKey, objectData):
        dinghy = DistributedDinghyAI(self.air)
        dinghy.setPos(objectData.get('Pos', (0, 0, 0)))
        dinghy.setHpr(objectData.get('Hpr', (0, 0, 0)))
        dinghy.setInteractRadius(float(objectData.get('Aggro Radius', 25)))

        parent.generateChildWithRequired(dinghy, PiratesGlobals.IslandLocalZone)
        self.addObject(dinghy)
        self.broadcastObjectPosition(dinghy)

        return dinghy

    def __generateObjectSpawnNode(self, parent, parentUid, objKey, objectData):
        spawnClass = DistributedSurfaceTreasureAI if objectData['Spawnables'] == 'Surface Treasure' else DistributedBuriedTreasureAI

        spawnNode = spawnClass(self.air)
        spawnNode.setPos(objectData.get('Pos', (0, 0, 0)))
        spawnNode.setHpr(objectData.get('Hpr', (0, 0, 0)))
        spawnNode.setScale(objectData.get('Scale', (1, 1, 1)))
        spawnNode.setStartingDepth(int(objectData.get('startingDepth', 10)))
        spawnNode.setCurrentDepth(spawnNode.getStartingDepth())
        spawnNode.setVisZone(objectData.get('VisZone', ''))

        parent.generateChildWithRequired(spawnNode, PiratesGlobals.IslandLocalZone)
        self.addObject(spawnNode)
        self.broadcastObjectPosition(spawnNode)

        return spawnNode

    def __generateRepairBench(self, parent, parentUid, objKey, objectData):
        bench = DistributedRepairBenchAI(self.air)
        bench.setPos(objectData.get('Pos', (0, 0, 0)))
        bench.setHpr(objectData.get('Hpr', (0, 0, 0)))
        bench.setScale(objectData.get('Scale', (1, 1, 1)))
        bench.setDifficulty(int(objectData.get('difficulty', '0')))

        parent.generateChildWithRequired(bench, PiratesGlobals.IslandLocalZone)
        self.addObject(bench)
        self.broadcastObjectPosition(bench)

        return bench

    def __generateIslandArea(self, parent, parentUid, objKey, objectData):
        from pirates.world.DistributedGameAreaAI import DistributedGameAreaAI

        areaFile = objectData.get('File', None)
        if not areaFile:
            self.notify.warning('Failed to generate Island Game Area %s; No file defined' % objKey)
            return

        # allocate a new zone for this area
        areaZone = self.air.allocateZone()

        islandArea = DistributedGameAreaAI(self.air)
        islandArea.setUniqueId(objKey)
        islandArea.setName(islandArea.getLocalizerName())
        islandArea.setModelPath(objectData['Visual']['Model'])

        self.parent.generateChildWithRequired(islandArea, areaZone)
        self.addObject(islandArea)
        self.broadcastObjectPosition(islandArea)
        self.air.worldCreator.loadObjectsFromFile(areaFile + '.py', islandArea)

        return islandArea
