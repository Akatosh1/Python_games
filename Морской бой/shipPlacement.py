import random


class ShipPlacement(object):
    def __init__(self, player):
        self.player = player
        self.coordField = {60+(b*50): {50+(a*50): 'Empty' for a in range(10)}
                           for b in range(10)}
        self.availablePos = {a: {b: 'Yes' for b in range(10)}
                             for a in range(10)}
        self.deckField = {a: {b: 0 for b in range(10)} for a in range(10)}
        self.endDeckField = {a: {b: 0 for b in range(10)} for a in range(10)}
        self.playerFourDeck = Ships()
        self.playerThreeDeck = Ships()
        self.playerTwoDeck = Ships()
        self.playerOneDeck = Ships()

    def randomPlacement(self):
        self.createWarship(4)
        self.createWarship(3)
        self.createWarship(3)
        self.createWarship(2)
        self.createWarship(2)
        self.createWarship(2)
        self.createWarship(1)
        self.createWarship(1)
        self.createWarship(1)
        self.createWarship(1)

    def createWarship(self, decksNumber):
        startCoord = {}
        endCoord = {}
        variantCounter = 0
        counter = 0
        for i in range(11-decksNumber):
            for j in range(11-decksNumber):
                try:
                    for k in range(decksNumber):
                        if self.availablePos[i+k][j] == 'Yes':
                            counter += 1
                    if counter == decksNumber:
                        startCoord[variantCounter] = {}
                        endCoord[variantCounter] = {}
                        startCoord[variantCounter][i] = j
                        endCoord[variantCounter][i+decksNumber-1] = j
                        variantCounter += 1
                except LookupError:
                    pass
                counter = 0
                try:
                    for m in range(decksNumber):
                        if self.availablePos[i][j+m] == 'Yes':
                            counter += 1
                    if counter == decksNumber:
                        startCoord[variantCounter] = {}
                        endCoord[variantCounter] = {}
                        startCoord[variantCounter][i] = j
                        endCoord[variantCounter][i] = j+decksNumber-1
                        variantCounter += 1
                except LookupError:
                    pass
                counter = 0
        if decksNumber == 1:
            variantCounter = variantCounter/2
        if variantCounter == 1:
            variant = 0
        else:
            variant = random.randint(0, variantCounter-1)
        beginX = list(startCoord[variant])[0]
        beginY = startCoord[variant][beginX]
        endX = list(endCoord[variant])[0]
        endY = endCoord[variant][endX]
        for x in range(beginX, endX+1):
            for y in range(beginY, endY+1):
                xCoord = 60 + (x * 50)
                yCoord = 50 + (y * 50)
                self.deckField[x][y] = decksNumber
                self.coordField[xCoord][yCoord] = 'ship'
        for i in range(beginX-1, endX+2):
            for j in range(beginY-1, endY+2):
                try:
                    self.availablePos[i][j] = 'No'
                except LookupError:
                    pass
        variantCounter = 0

    def addShips(self):
        for deck in [1, 2, 3, 4]:
            decks = [self.playerOneDeck, self.playerTwoDeck,
                     self.playerThreeDeck, self.playerFourDeck]
            playerDeck = decks[deck-1]
            ships = [4, 3, 2, 1]
            self.addShip(deck, playerDeck)

    def addShip(self, deck, playerDeck):
        numberOfDeck = 0
        counter = 0
        for i in range(10):
            for j in range(10):
                try:
                    for k in range(deck):
                        if self.deckField[i+k][j] == deck:
                            counter += 1
                    if counter == deck:
                        playerDeck.startCoord[numberOfDeck] = (i, j)
                        playerDeck.endCoord[numberOfDeck] = (i+deck-1, j)
                        numberOfDeck += 1
                        for m in range(deck):
                            self.deckField[i+m][j] = 0
                            self.endDeckField[i+m][j] = deck
                    counter = 0
                except LookupError:
                    counter = 0
                try:
                    for k in range(deck):
                        if self.deckField[i][j+k] == deck:
                            counter += 1
                    if counter == deck:
                        playerDeck.startCoord[numberOfDeck] = (i, j)
                        playerDeck.endCoord[numberOfDeck] = (i, j+deck-1)
                        numberOfDeck += 1
                        for m in range(deck):
                            self.deckField[i][j+m] = 0
                            self.endDeckField[i][j+m] = deck
                    counter = 0
                except LookupError:
                    counter = 0
        playerDeck.counter = numberOfDeck


class Ships(object):
    def __init__(self):
        self.startCoord = {}
        self.endCoord = {}
        self.counter = 0
