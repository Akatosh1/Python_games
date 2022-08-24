import copy
import random


class Game(object):
    def __init__(self, FPField, SPField, playerTurn):
        self.firstPlayerField = FPField
        self.secondPlayerField = SPField
        self.playerTurn = playerTurn
        self.firstPlayerShips = 20
        self.secondPlayerShips = 20
        self.botCounter = 100
        self.torpedoDirection = ''
        self.xCoordinatesSet = [a for a in range(10)]
        self.coordinatesSet = {a: [b for b in range(10)] for a in range(10)}
        self.availableFirstPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                        for a in range(10)}
                                        for b in range(10)}
        self.availableSecondPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                         for a in range(10)}
                                         for b in range(10)}
        self.isWrecked = False
        self.shipWreckCounter = 0
        self.mark = (0, 0)
        self.direction = ''

    def checkShip(self):
        for player in [1, 2]:
            fields = [self.firstPlayerField, self.secondPlayerField]
            availablePos = [self.availableFirstPlayerPos,
                            self.availableSecondPlayerPos]
            pos = availablePos[player-1]
            field = fields[player-1]
            for deck in [4, 3, 2, 1]:
                decks = [field.playerFourDeck, field.playerThreeDeck,
                         field.playerTwoDeck, field.playerOneDeck]
                currentDeck = decks[4-deck]
                ship = 5-deck
                self.checkCurrentShip(currentDeck, ship, deck, pos)

    def checkCurrentShip(self, currentDeck, ships, decks, pos):
        counter = 0
        for ship in range(ships):
            beginX = currentDeck.startCoord[ship][0]
            endX = currentDeck.endCoord[ship][0]
            beginY = currentDeck.startCoord[ship][1]
            endY = currentDeck.endCoord[ship][1]
            for k in range(beginX, endX+1):
                for i in range(beginY, endY+1):
                    x = 60+k*50
                    y = 50+i*50
                    if pos[x][y] == 'Yes':
                        counter += 1
            if counter == decks:
                self.openNeighbours(pos, beginX, beginY, endX, endY)
            counter = 0

    def openNeighbours(self, pos, beginX, beginY, endX, endY):
        for k in range(beginX-1, endX+2):
            for i in range(beginY-1, endY+2):
                try:
                    x = 60+k*50
                    y = 50+i*50
                    if pos[x][y] == 'Empty':
                        pos[x][y] = 'No'
                except LookupError:
                    pass

    def easyBotTurn(self):
        while (self.playerTurn == 'Second' and self.firstPlayerShips > 0):
            for i in range(10):
                for j in range(10):
                    m = 60+i*50
                    n = 50+j*50
                    if not self.availableFirstPlayerPos[m][n] == 'Empty':
                        try:
                            self.coordinatesSet[i].remove(j)
                            if not self.coordinatesSet[i]:
                                self.coordinatesSet.pop(i)
                                self.xCoordinatesSet.remove(i)
                        except (LookupError, ValueError):
                            pass
            x = random.choice(self.xCoordinatesSet)
            y = random.choice(self.coordinatesSet[x])
            coordX = 60+x*50
            coordY = 50+y*50
            if self.firstPlayerField.coordField[coordX][coordY] == 'ship':
                self.firstPlayerShips -= 1
                self.availableFirstPlayerPos[coordX][coordY] = 'Yes'
            else:
                self.availableFirstPlayerPos[coordX][coordY] = 'No'
                self.playerTurn = 'First'

    def hardBotTurn(self):
        while (self.playerTurn == 'Second' and self.firstPlayerShips > 0):
            if self.isWrecked:
                self.finishing()
            else:
                for i in range(10):
                    for j in range(10):
                        m = 60+i*50
                        n = 50+j*50
                        if not self.availableFirstPlayerPos[m][n] == 'Empty':
                            try:
                                self.coordinatesSet[i].remove(j)
                                if not self.coordinatesSet[i]:
                                    self.coordinatesSet.pop(i)
                                    self.xCoordinatesSet.remove(i)
                            except (LookupError, ValueError):
                                pass
                x = random.choice(self.xCoordinatesSet)
                y = random.choice(self.coordinatesSet[x])
                coordX = 60+x*50
                coordY = 50+y*50
                if self.firstPlayerField.coordField[coordX][coordY] == 'ship':
                    self.firstPlayerShips -= 1
                    self.availableFirstPlayerPos[coordX][coordY] = 'Yes'
                    targetShip = self.firstPlayerField.endDeckField[x][y] - 1
                    self.shipWreckCounter = targetShip
                    if self.shipWreckCounter > 0:
                        self.mark = (coordX, coordY)
                        self.isWrecked = True
                        self.finishing()
                else:
                    self.availableFirstPlayerPos[coordX][coordY] = 'No'
                    self.playerTurn = 'First'

    def finishing(self):
        if self.direction == '':
            self.findDirection()
        else:
            self.hitDirection()

    def hitDirection(self):
        self.hit = self.mark
        while self.direction != '':
            try:
                if self.direction == 'Up':
                    self.hit = (self.hit[0], self.hit[1]-50)
                if self.direction == 'Down':
                    self.hit = (self.hit[0], self.hit[1]+50)
                if self.direction == 'Left':
                    self.hit = (self.hit[0]-50, self.hit[1])
                if self.direction == 'Right':
                    self.hit = (self.hit[0]+50, self.hit[1])
                x = self.hit[0]
                y = self.hit[1]
                if self.firstPlayerField.coordField[x][y] == 'ship':
                    self.availableFirstPlayerPos[x][y] = 'Yes'
                    self.firstPlayerShips -= 1
                    self.shipWreckCounter -= 1
                    if self.shipWreckCounter == 0:
                        self.direction = ''
                        self.isWrecked = False
                if self.firstPlayerField.coordField[x][y] == 'Empty':
                    self.availableFirstPlayerPos[x][y] = 'No'
                    self.direction = ''
            except LookupError:
                self.direction = ''

    def findDirection(self):
        X = self.mark[0]
        Y = self.mark[1]
        while (self.direction == '' and self.playerTurn == 'Second'):
            try:
                self.checkDirection(X-50, Y, 'Left')
                self.checkDirection(X+50, Y, 'Right')
                self.checkDirection(X, Y-50, 'Up')
                self.checkDirection(X, Y+50, 'Down')
            except Exception:
                break

    def checkDirection(self, x, y, direction):
        try:
            if (self.availableFirstPlayerPos[x][y] == 'No' or
               self.availableFirstPlayerPos[x][y] == 'Yes'):
                pass
            else:
                if self.firstPlayerField.coordField[x][y] == 'Empty':
                    self.availableFirstPlayerPos[x][y] = 'No'
                    self.playerTurn = 'First'
                    raise Exception
                else:
                    self.direction = direction
        except LookupError:
            pass

    def submarineFire(self):
        for i in range(10):
            for j in range(10):
                x = 60+i*50
                y = 50+j*50
                if self.playerTurn == 'First':
                    if self.availableSecondPlayerPos[x][y] == 'Submarine':
                        self.oneTorpedoFire(1, x, y)
                        self.availableSecondPlayerPos[x][y] = 'Empty'
                if self.playerTurn == 'Second':
                    if self.availableFirstPlayerPos[x][y] == 'Submarine':
                        self.oneTorpedoFire(2, x, y)
                        self.availableFirstPlayerPos[x][y] = 'Empty'
        self.torpedoDirection = ''

    def oneTorpedoFire(self, player, xCoord, yCoord):
        x = xCoord
        y = yCoord
        fields = [self.secondPlayerField, self.firstPlayerField]
        poses = [self.availableSecondPlayerPos, self.availableFirstPlayerPos]
        field = fields[player-1]
        pos = poses[player-1]
        if self.torpedoDirection == 'Horizontal':
            counter = y
        else:
            counter = x
        while counter > 60:
            if self.torpedoDirection == 'Horizontal':
                y -= 50
                counter -= 50
            else:
                x -= 50
                counter -= 50
            if pos[x][y] == 'Empty':
                pos[x][y] = 'PotentialEmpty'
            if field.coordField[x][y] == 'ship':
                self.fire(pos)
                pos[x][y] = 'Yes'
                if player == 1:
                    self.secondPlayerShips -= 1
                else:
                    self.firstPlayerShips -= 1
                break
            else:
                pass
        self.clearPotentialEmpty(pos)
        x = xCoord
        y = yCoord
        if self.torpedoDirection == 'Horizontal':
            counter = y
        else:
            counter = x
        while counter < 500:
            if self.torpedoDirection == 'Horizontal':
                y += 50
                counter += 50
            else:
                x += 50
                counter += 50
            if pos[x][y] == 'Empty':
                pos[x][y] = 'PotentialEmpty'
            if field.coordField[x][y] == 'ship':
                self.fire(pos)
                pos[x][y] = 'Yes'
                if player == 1:
                    self.secondPlayerShips -= 1
                else:
                    self.firstPlayerShips -= 1
                break
            else:
                pass
        self.clearPotentialEmpty(pos)

    def fire(self, pos):
        for i in range(10):
            for j in range(10):
                x = 60+i*50
                y = 50+j*50
                if pos[x][y] == 'PotentialEmpty':
                    pos[x][y] = 'No'

    def clearPotentialEmpty(self, pos):
        for i in range(10):
            for j in range(10):
                x = 60+i*50
                y = 50+j*50
                if pos[x][y] == 'PotentialEmpty':
                    pos[x][y] = 'Empty'

    def saveGame(self):
        self.saveFirstPlayerShips = copy.deepcopy(self.firstPlayerShips)
        self.saveSecondPlayerShips = copy.deepcopy(self.secondPlayerShips)
        self.saveBotCounter = copy.copy(self.botCounter)
        self.saveXCoordinatesSet = copy.deepcopy(self.xCoordinatesSet)
        self.saveCoordinatesSet = copy.deepcopy(self.coordinatesSet)
        self.savePlayerTurn = copy.copy(self.playerTurn)
        self.saveFPpos = copy.deepcopy(self.availableFirstPlayerPos)
        self.saveSPpos = copy.deepcopy(self.availableSecondPlayerPos)
        self.saveShipWreckCounter = copy.copy(self.shipWreckCounter)
        self.saveMark = copy.deepcopy(self.mark)
        self.saveIsWrecked = copy.copy(self.isWrecked)
        self.saveShipWreckCounter = copy.copy(self.shipWreckCounter)
        self.saveDirection = copy.copy(self.direction)

    def loadGame(self):
        self.firstPlayerShips = copy.deepcopy(self.saveFirstPlayerShips)
        self.secondPlayerShips = copy.deepcopy(self.saveSecondPlayerShips)
        self.botCounter = copy.copy(self.saveBotCounter)
        self.xCoordinatesSet = copy.deepcopy(self.saveXCoordinatesSet)
        self.coordinatesSet = copy.deepcopy(self.saveCoordinatesSet)
        self.playerTurn = copy.copy(self.savePlayerTurn)
        self.availableFirstPlayerPos = copy.deepcopy(self.saveFPpos)
        self.availableSecondPlayerPos = copy.deepcopy(self.saveSPpos)
        self.shipWreckCounter = copy.copy(self.saveShipWreckCounter)
        self.mark = copy.copy(self.saveMark)
        self.isWrecked = copy.copy(self.saveIsWrecked)
        self.shipWreckCounter = copy.copy(self.saveShipWreckCounter)
        self.direction = copy.copy(self.saveDirection)
