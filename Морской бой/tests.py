import os
import sys
import unittest
from shipPlacement import ShipPlacement, Ships
from game import Game
import copy


class ShipPlacementTest(unittest.TestCase):

    def setUp(self):
        self.randomPlacement = ShipPlacement('Test')
        self.randomPlacement.randomPlacement()

    def test_is_right_deck_count(self):
        decks = [1, 2, 3, 4]
        rightNumberOfDecks = [4, 6, 6, 4]
        for deck in decks:
            counter = 0
            for x in range(10):
                for y in range(10):
                    if self.randomPlacement.deckField[x][y] == deck:
                        counter += 1
            self.assertEqual(rightNumberOfDecks[deck-1], counter)

    def test_is_deckField_eq_endDeckField(self):
        deckField = copy.deepcopy(self.randomPlacement.deckField)
        self.randomPlacement.addShips()
        self.assertEqual(deckField, self.randomPlacement.endDeckField)

    def test_is_right_ships_count(self):
        self.randomPlacement.addShips()
        self.assertEqual(self.randomPlacement.playerFourDeck.counter, 1)
        self.assertEqual(self.randomPlacement.playerThreeDeck.counter, 2)
        self.assertEqual(self.randomPlacement.playerTwoDeck.counter, 3)
        self.assertEqual(self.randomPlacement.playerOneDeck.counter, 4)

    def test_is_deckField_eq_coordField(self):
        for i in range(10):
            for j in range(10):
                if self.randomPlacement.deckField[i][j] > 0:
                    x = 60+i*50
                    y = 50+j*50
                    self.assertEqual(self.randomPlacement.coordField[x][y],
                                     'ship')


class GameTests(unittest.TestCase):

    def setUp(self):
        self.firstPlayerField = ShipPlacement('First')
        self.secondPlayerField = ShipPlacement('Second')
        self.firstPlayerField.randomPlacement()
        self.secondPlayerField.randomPlacement()
        self.firstPlayerField.addShips()
        self.secondPlayerField.addShips()

    def test_easy_bot_turn(self):
        self.game = Game(self.firstPlayerField,
                         self.secondPlayerField,
                         'Second')
        self.testGame = copy.deepcopy(self.game)
        while self.game.firstPlayerShips == 20:
            self.game.easyBotTurn()
            self.game.playerTurn = 'Second'
        self.assertNotEqual(self.testGame.availableFirstPlayerPos,
                            self.game.availableFirstPlayerPos)

    def test_hard_bot_turn(self):
        self.game = Game(self.firstPlayerField,
                         self.secondPlayerField,
                         'Second')
        self.testGame = copy.deepcopy(self.game)
        while self.game.firstPlayerShips == 20:
            self.game.hardBotTurn()
            self.game.playerTurn = 'Second'
        self.assertNotEqual(self.testGame.availableFirstPlayerPos,
                            self.game.availableFirstPlayerPos)

    def test_check_direction(self):
        # делаем пустое поле чтобы на нем не было ничего лишнего
        self.field = ShipPlacement('Test')
        self.game = Game(self.field, self.secondPlayerField, 'Second')
        # выбираем рандомную точку отсчета
        self.game.mark = (160, 150)
        self.game.firstPlayerField.coordField[110][150] = 'ship'
        self.game.firstPlayerField.coordField[210][150] = 'ship'
        X = self.game.mark[0]
        Y = self.game.mark[1]

        self.game.checkDirection(X-50, Y, 'Left')
        self.assertEqual(self.game.direction, 'Left')

        self.game.checkDirection(X+50, Y, 'Right')
        self.assertEqual(self.game.direction, 'Right')

        with self.assertRaises(Exception):
            self.game.checkDirection(X, Y-50, 'Up')

        with self.assertRaises(Exception):
            self.game.checkDirection(X, Y+50, 'Down')

    def test_one_torpedo_fire(self):
        # делаем пустое поле чтобы на нем не было ничего лишнего
        self.field = ShipPlacement('Test')
        self.game = Game(self.field, self.secondPlayerField, 'Second')
        self.game.firstPlayerField.coordField[110][150] = 'ship'
        self.game.firstPlayerField.coordField[110][400] = 'ship'
        self.game.firstPlayerField.coordField[210][200] = 'ship'
        self.game.torpedoDirection = 'Horizontal'
        pos = self.game.availableFirstPlayerPos

        self.game.oneTorpedoFire(2, 110, 250)
        self.assertEqual(pos[110][150], 'Yes')
        self.assertEqual(pos[110][400], 'Yes')
        for x in range(110, 111):
            for y in range(200, 250, 50):
                self.assertEqual(pos[x][y], 'No')
        for x in range(110, 111):
            for y in range(300, 400, 50):
                self.assertEqual(pos[x][y], 'No')

        self.game.oneTorpedoFire(2, 210, 300)
        self.assertEqual(pos[210][200], 'Yes')
        self.assertEqual(pos[210][250], 'No')

        self.game.oneTorpedoFire(2, 310, 100)
        for x in range(310, 311):
            for y in range(50, 500, 50):
                self.assertEqual(pos[x][y], 'Empty')

    def test_save_and_load(self):
        self.testGame = Game(self.firstPlayerField,
                             self.secondPlayerField,
                             'Second')
        self.testGame2 = copy.deepcopy(self.testGame)

        self.testGame.saveGame()

        while self.testGame.firstPlayerShips == 20:
            self.testGame.easyBotTurn()
            self.testGame.playerTurn = 'Second'

        self.assertNotEqual(self.testGame.availableFirstPlayerPos,
                            self.testGame2.availableFirstPlayerPos)
        self.assertNotEqual(self.testGame.firstPlayerShips,
                            self.testGame2.firstPlayerShips)
        self.assertNotEqual(self.testGame.coordinatesSet,
                            self.testGame2.coordinatesSet)

        self.testGame.loadGame()

        self.assertEqual(self.testGame.availableFirstPlayerPos,
                         self.testGame2.availableFirstPlayerPos)
        self.assertEqual(self.testGame.firstPlayerShips,
                         self.testGame2.firstPlayerShips)
        self.assertEqual(self.testGame.coordinatesSet,
                         self.testGame2.coordinatesSet)

    def test_open_neighbours(self):
        self.field = {60+(b*50): {50+(a*50): 'Empty' for a in range(10)}
                      for b in range(10)}
        for i in range(1, 4):
            for j in range(1, 4):
                x = 60+i*50
                y = 50+j*50
                self.field[x][y] = 'No'
        self.field[160][150] = 'Yes'
        self.testField = {60+(b*50): {50+(a*50): 'Empty' for a in range(10)}
                          for b in range(10)}
        self.testField[160][150] = 'Yes'
        self.game = Game(self.field, self.testField, 'First')
        self.game.openNeighbours(self.testField, 2, 2, 2, 2)
        self.assertEqual(self.field, self.testField)

    def test_check_ship(self):
        self.testField = copy.deepcopy(self.firstPlayerField)
        self.game = Game(self.firstPlayerField,
                         self.testField,
                         'First')
        self.assertEqual(self.game.firstPlayerField.endDeckField,
                         self.game.secondPlayerField.endDeckField)
        for i in range(10):
            for j in range(10):
                if self.game.firstPlayerField.endDeckField[i][j] == 4:
                    pos = self.game.availableFirstPlayerPos
                    x = 60+i*50
                    y = 50+j*50
                    pos[x][y] = 'Yes'
                    self.game.openNeighbours(pos, i, j, i, j)
        for i in range(10):
            for j in range(10):
                if self.game.secondPlayerField.endDeckField[i][j] == 4:
                    x = 60+i*50
                    y = 50+j*50
                    self.game.availableSecondPlayerPos[x][y] = 'Yes'
        self.game.checkShip()
        self.assertEqual(self.game.availableFirstPlayerPos,
                         self.game.availableSecondPlayerPos)


if __name__ == '__main__':
    unittest.main()
