#!/usr/bin/env python3
import sys
from PyQt5 import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from game import Game
from shipPlacement import ShipPlacement, Ships


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.availableFirstPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                        for a in range(10)}
                                        for b in range(10)}
        self.availableSecondPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                         for a in range(10)}
                                         for b in range(10)}
        self.firstPlayerField = ShipPlacement('First')
        self.secondPlayerField = ShipPlacement('Second')
        self.readyPlayers = 0
        self.isGame = False
        self.gameMode = ''
        self.isFirstPlacement = False
        self.isSecondPlacement = False
        self.currentDeck = 0
        self.isSave = False

        self.createButton('Выход', 1200, 150, self.quitEvent)
        self.createButton('Играть', 1200, 50, self.gameEvent)
        self.createButton('Расстановка', 1200, 100, self.placementEvent)
        self.createButton('1палубник', 1200, 300, lambda: self.chooseDeck(1))
        self.createButton('2палубник', 1200, 350, lambda: self.chooseDeck(2))
        self.createButton('3палубник', 1200, 400, lambda: self.chooseDeck(3))
        self.createButton('4палубник', 1200, 450, lambda: self.chooseDeck(4))
        self.createButton('Очистить', 1200, 500, lambda: self.chooseDeck(0))
        self.createButton('Принять', 850, 560, lambda: self.acceptEvent(2))
        self.createButton('Принять', 250, 560, lambda: self.acceptEvent(1))
        self.createButton('Поставить подлодку', 400, 600, self.submarineEvent)
        self.createButton('Залп!!!', 400, 650, self.fireEvent)
        self.createButton('Сохранить', 800, 600, self.saveGameEvent)
        self.createButton('Загрузить', 800, 650, self.loadGameEvent)

        self.setGeometry(0, 0, 1400, 700)
        self.setWindowTitle('BattleShip')
        self.show()

    def saveGameEvent(self):
        if self.isGame:
            self.game.saveGame()
            self.isSave = True

    def loadGameEvent(self):
        if (self.isGame and self.isSave):
            self.game.loadGame()

    def chooseDeck(self, deck):
        self.currentDeck = deck

    def fireEvent(self):
        if (self.isGame and self.game.torpedoDirection != ''):
            self.game.submarineFire()
            self.game.checkShip()

    def submarineEvent(self):
        if self.isGame:
            self.chooseTorpedoDirection()

    def chooseTorpedoDirection(self):
        messageBox = QMessageBox()
        messageBox.setWindowTitle("Выбор")
        messageBox.setText("Выберите направление торпед")
        hor = messageBox.addButton('Горизонтальное', QMessageBox.AcceptRole)
        vert = messageBox.addButton('Вертикальное', QMessageBox.AcceptRole)
        messageBox.exec()
        if messageBox.clickedButton() == hor:
            self.game.torpedoDirection = 'Horizontal'
        if messageBox.clickedButton() == vert:
            self.game.torpedoDirection = 'Vertical'

    def acceptEvent(self, player):
        if player == 1:
            self.isFirstPlacement = False
            self.availableFirstPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                            for a in range(10)}
                                            for b in range(10)}
            self.isFirstPlacement = self.checkEvent(self.firstPlayerField)
            if self.isFirstPlacement:
                self.firstPlayerField = ShipPlacement("First")
        if player == 2:
            self.availableSecondPlayerPos = {60+(b*50): {50+(a*50): 'Empty'
                                             for a in range(10)}
                                             for b in range(10)}
            self.isSecondPlacement = False
            self.isSecondPlacement = self.checkEvent(self.secondPlayerField)
            if self.isSecondPlacement:
                self.secondPlayerField = ShipPlacement("Second")

    def checkEvent(self, field):
        playerShips = {1: 0, 2: 0, 3: 0, 4: 0}
        neededPlayerShips = {1: 4, 2: 6, 3: 6, 4: 4}
        for i in range(10):
            for j in range(10):
                if field.deckField[i][j] != 0:
                    playerShips[field.deckField[i][j]] += 1
        if playerShips != neededPlayerShips:
            playerShips = {1: 0, 2: 0, 3: 0, 4: 0}
            self.repeatEvent()
            return True
        else:
            self.readyPlayers += 1
            return False

    def repeatEvent(self):
        reply = QMessageBox.warning(self, 'Error',
                                    'Пожалуйста расставьте корабли правильно',
                                    QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            pass

    def mousePressEvent(self, event):
        point = event.pos()
        x = point.x()
        y = point.y()
        sndx = (x - 60) // 50
        sndy = (y - 50) // 50
        snd2x = sndx - 12
        curx = 60 + 50*sndx
        cury = 50 + 50*sndy
        cur2x = curx - 600
        try:
            if x < 580:
                self.SecondPlayerAction(sndx, sndy, curx, cury)
            else:
                self.FirstPlayerAction(snd2x, sndy, cur2x, cury)
        except (LookupError, AttributeError):
            pass

    def FirstPlayerAction(self, snd2x, sndy, cur2x, cury):
        if self.isSecondPlacement:
            self.placeDeck(2, snd2x, sndy, cur2x, cury)
        if (self.isGame and self.game.playerTurn == 'First'):
            if self.game.torpedoDirection != '':
                self.game.availableSecondPlayerPos[cur2x][cury] = 'Submarine'
            elif self.game.secondPlayerField.coordField[cur2x][cury] == 'ship':
                self.game.availableSecondPlayerPos[cur2x][cury] = 'Yes'
                self.game.checkShip()
                self.game.secondPlayerShips -= 1
                if self.game.secondPlayerShips == 0:
                    self.winEvent('First')
            else:
                self.game.availableSecondPlayerPos[cur2x][cury] = 'No'
                self.game.playerTurn = 'Second'
                if self.gameMode == 'easy':
                    self.game.easyBotTurn()
                    self.game.checkShip()
                if self.gameMode == 'hard':
                    self.game.hardBotTurn()
                    self.game.checkShip()
            if self.game.firstPlayerShips == 0:
                self.winEvent('Second')

    def SecondPlayerAction(self, sndx, sndy, curx, cury):
        if self.isFirstPlacement:
            self.placeDeck(1, sndx, sndy, curx, cury)
        if (self.isGame and self.game.playerTurn == 'Second'):
            if self.game.torpedoDirection != '':
                self.game.availableFirstPlayerPos[curx][cury] = 'Submarine'
            elif self.game.firstPlayerField.coordField[curx][cury] == 'ship':
                self.game.availableFirstPlayerPos[curx][cury] = 'Yes'
                self.game.checkShip()
                self.game.firstPlayerShips -= 1
                if self.game.firstPlayerShips == 0:
                    self.winEvent('Second')
            else:
                self.game.availableFirstPlayerPos[curx][cury] = 'No'
                self.game.playerTurn = 'First'

    def placeDeck(self, field, x, y, xCoord, yCoord):
        fields = [self.firstPlayerField, self.secondPlayerField]
        pos = [self.availableFirstPlayerPos, self.availableSecondPlayerPos]
        fields[field-1].deckField[x][y] = self.currentDeck
        fields[field-1].coordField[xCoord][yCoord] = 'ship'
        pos[field-1][xCoord][yCoord] = 'Yes'

    def createButton(self, buttonName, x, y, event):
        button = QPushButton('{}'.format(buttonName), self)
        button.clicked.connect(event)
        button.resize(button.sizeHint())
        button.move(x, y)

    def quitEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Вы уверены?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()
        else:
            pass

    def gameEvent(self, event):
        if self.readyPlayers == 2:
            self.firstPlayerField.addShips()
            self.secondPlayerField.addShips()
            self.game = Game(self.firstPlayerField,
                             self.secondPlayerField,
                             'First')
            self.isGame = True
        if self.readyPlayers < 2:
            self.error()

    def error(self):
        reply = QMessageBox.warning(self, 'Error',
                                    'Поле уже существует или не выбрано',
                                    QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            pass

    def placementEvent(self, event):
        messageBox = QMessageBox()
        messageBox.setWindowTitle("GameMode")
        messageBox.setText("Choose Game Mode")
        hotSeat = messageBox.addButton('Два игрока', QMessageBox.AcceptRole)
        easyMode = messageBox.addButton('Легко', QMessageBox.AcceptRole)
        hardMode = messageBox.addButton('Сложно', QMessageBox.AcceptRole)
        back = messageBox.addButton('Назад', QMessageBox.AcceptRole)
        if self.readyPlayers > 0:
            self.error()
        else:
            messageBox.exec()
            if messageBox.clickedButton() == back:
                pass
            if messageBox.clickedButton() == hotSeat:
                self.gameMode = 'hotSeat'
            if messageBox.clickedButton() == hardMode:
                self.gameMode = 'hard'
            if messageBox.clickedButton() == easyMode:
                self.gameMode = 'easy'
            if self.gameMode != '':
                self.choosePlacement()

    def choosePlacement(self):
        messageBox = QMessageBox()
        messageBox.setWindowTitle("Placement")
        messageBox.setText("Как вы хотите расставить корабли?")
        byOwn = messageBox.addButton('Самостоятельно', QMessageBox.AcceptRole)
        random = messageBox.addButton('Случайно', QMessageBox.AcceptRole)
        messageBox.exec()
        if messageBox.clickedButton() == byOwn:
            if self.gameMode == 'hotSeat':
                self.isFirstPlacement = True
                self.isSecondPlacement = True
            if self.gameMode in ["hard", "easy"]:
                self.secondPlayerField.randomPlacement()
                self.isFirstPlacement = True
                self.readyPlayers += 1
        if messageBox.clickedButton() == random:
            self.firstPlayerField.randomPlacement()
            self.secondPlayerField.randomPlacement()
            self.readyPlayers += 2

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawRec(qp)
        self.drawLines(qp)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        letters = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ж', 'З', 'И', 'К']
        numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        qp.setPen(QColor(168, 34, 3))
        qp.setFont(QFont('Decorative', 10))
        for i in range(10):
            qp.drawText(80+i*50, 40, letters[i])
            qp.drawText(35, 85+i*50, numbers[i])
            qp.drawText(670+i*50, 40, letters[i])
            qp.drawText(625, 85+i*50, numbers[i])
        for i in range(10):
            for j in range(10):
                x = 60+i*50
                y = 50+j*50
                if self.isFirstPlacement:
                    if self.availableFirstPlayerPos[x][y] == 'Yes':
                        deck1 = self.firstPlayerField.deckField[i][j]
                        qp.drawText(20+x, 20+y, '{}'.format(deck1))
                if self.isSecondPlacement:
                    if self.availableSecondPlayerPos[x][y] == 'Yes':
                        deck2 = self.secondPlayerField.deckField[i][j]
                        qp.drawText(610+x, 20+y, '{}'.format(deck2))
        self.update()

    def drawLines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        qp.setPen(pen)
        for i in range(11):
            qp.drawLine(60, 50+i*50, 560, 50+i*50)
            qp.drawLine(60+i*50, 50, 60+i*50, 550)
            qp.drawLine(660, 50+i*50, 1160, 50+i*50)
            qp.drawLine(660+i*50, 50, 660+i*50, 550)

    def drawRec(self, qp):
        col = QColor(0, 0, 0)
        col.setNamedColor('0099FF')
        qp.setPen(col)
        if not self.isGame:
            for i in range(10):
                for j in range(10):
                    x = 60+i*50
                    y = 50+j*50
                    if self.availableFirstPlayerPos[x][y] == 'Empty':
                        qp.setBrush(QColor(100, 100, 255))
                        qp.drawRect(x, y, 50, 50)
                    if self.availableFirstPlayerPos[x][y] == 'Yes':
                        qp.setBrush(QColor(255, 100, 100))
                        qp.drawRect(x, y, 50, 50)
                    if self.availableFirstPlayerPos[x][y] == 'No':
                        qp.setBrush(QColor(0, 0, 255))
                        qp.drawRect(x, y, 50, 50)
                    if self.availableSecondPlayerPos[x][y] == 'Empty':
                        qp.setBrush(QColor(100, 100, 255))
                        qp.drawRect(x+600, y, 50, 50)
                    if self.availableSecondPlayerPos[x][y] == 'Yes':
                        qp.setBrush(QColor(255, 100, 100))
                        qp.drawRect(x+600, y, 50, 50)
                    if self.availableSecondPlayerPos[x][y] == 'No':
                        qp.setBrush(QColor(0, 0, 255))
                        qp.drawRect(x+600, y, 50, 50)
                    self.update()
        if self.isGame:
            for i in range(10):
                for j in range(10):
                    x = 60+i*50
                    y = 50+j*50
                    if self.game.availableFirstPlayerPos[x][y] == 'Empty':
                        qp.setBrush(QColor(100, 100, 255))
                        qp.drawRect(x, y, 50, 50)
                    if self.game.availableFirstPlayerPos[x][y] == 'Yes':
                        qp.setBrush(QColor(255, 100, 100))
                        qp.drawRect(x, y, 50, 50)
                    if self.game.availableFirstPlayerPos[x][y] == 'No':
                        qp.setBrush(QColor(0, 0, 255))
                        qp.drawRect(x, y, 50, 50)
                    if self.game.availableFirstPlayerPos[x][y] == 'Submarine':
                        qp.setBrush(QColor(255, 255, 0))
                        qp.drawRect(x, y, 50, 50)
                    if self.game.availableSecondPlayerPos[x][y] == 'Empty':
                        qp.setBrush(QColor(100, 100, 255))
                        qp.drawRect(x+600, y, 50, 50)
                    if self.game.availableSecondPlayerPos[x][y] == 'Yes':
                        qp.setBrush(QColor(255, 100, 100))
                        qp.drawRect(x+600, y, 50, 50)
                    if self.game.availableSecondPlayerPos[x][y] == 'No':
                        qp.setBrush(QColor(0, 0, 255))
                        qp.drawRect(x+600, y, 50, 50)
                    if self.game.availableSecondPlayerPos[x][y] == 'Submarine':
                        qp.setBrush(QColor(255, 255, 0))
                        qp.drawRect(x+600, y, 50, 50)
                    self.update()

    def winEvent(self, player):
        messageBox = QMessageBox()
        messageBox.setWindowTitle("Gratz")
        messageBox.setText("Player {} won!".format(player))
        agree = messageBox.addButton('Круто!', QMessageBox.AcceptRole)
        messageBox.exec()
        if messageBox.clickedButton() == agree:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
