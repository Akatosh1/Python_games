import sys
from PyQt5 import Qt, QtCore, QtGui
from PyQt5 import QtMultimedia as M
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import re
import time
import os

isKaraoke = False
current_adder = 0


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.songs = ["music/кино-спокойная ночь.mp3",
                      "music/дайте танк-маленький.mp3"]
        self.texts = ["texts/kino.txt",
                      "texts/tank.txt"]
        self.urls = []
        self.contents = []
        for song in self.songs:
            curr_url = QtCore.QUrl.fromLocalFile(song)
            self.urls.append(curr_url)
            curr_content = M.QMediaContent(curr_url)
            self.contents.append(curr_content)
        self.player = M.QMediaPlayer()
        self.choice_song = 1
        self.current_song = 0

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout()

        play_button = QPushButton("Старт")
        pause_button = QPushButton("Стоп")
        exit_button = QPushButton("Выход")
        edit_button = QPushButton("Редактор")
        writer_button = QPushButton("Прописать путь")
        adder_button = QPushButton("Добавить")

        play_button.clicked.connect(self.play_event)
        pause_button.clicked.connect(self.pause_event)
        exit_button.clicked.connect(self.quitEvent)
        edit_button.clicked.connect(self.edit_event)
        writer_button.clicked.connect(self.write_event)
        adder_button.clicked.connect(self.add_event)

        review = QLabel('Список песен')

        reviewEdit = QListView()

        reviewEdit.setObjectName("review")
        self.model = QStandardItemModel()
        reviewEdit.setModel(self.model)

        song1 = QtGui.QStandardItem("кино-спокойная ночь")
        song2 = QtGui.QStandardItem("дайте танк-маленький")

        reviewEdit.clicked.connect(self.choose_song_event)

        self.model.appendRow(song1)
        self.model.appendRow(song2)

        self.grid.setSpacing(10)

        self.grid.addWidget(review, 2, 0)
        self.grid.addWidget(reviewEdit, 2, 1, 5, 1)

        self.grid.addWidget(adder_button, 1, 2)
        self.grid.addWidget(writer_button, 2, 2)
        self.grid.addWidget(edit_button, 3, 2)
        self.grid.addWidget(play_button, 4, 2)
        self.grid.addWidget(pause_button, 5, 2)
        self.grid.addWidget(exit_button, 7, 2)

        self.central_widget.setLayout(self.grid)

        self.setGeometry(0, 0, 1400, 700)
        self.setWindowTitle('Караоке')
        self.show()

    def choose_song_event(self, event):
        self.choice_song = (event.row() + 1)

    def add_event(self):
        global current_adder
        if current_adder != 0:
            song = current_adder[0]
            text = current_adder[1]
            self.songs.append(song)
            self.texts.append(text)

            curr_url = QtCore.QUrl.fromLocalFile(song)
            self.urls.append(curr_url)
            curr_content = M.QMediaContent(curr_url)
            self.contents.append(curr_content)
            pattern = re.match(r".*/(.*).mp3", song)
            song = QtGui.QStandardItem(pattern.group(1))
            self.model.appendRow(song)
            current_adder = 0

    def write_event(self):
        self.adder = Adder()

    def play_event(self):
        global isKaraoke
        if isKaraoke:
            self.karaoke.timer.start()
        if ((self.current_song != self.choice_song) or (not isKaraoke)):
            play_song = self.contents[self.choice_song - 1]
            song_text = self.texts[self.choice_song - 1]
            self.player.setMedia(play_song)
            self.player.play()
            self.current_song = self.choice_song
            isKaraoke = True
            self.karaoke = Karaoke(song_text)
        elif ((self.current_song != 0) and
              (self.current_song == self.choice_song)):
            self.player.play()

    def quitEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Вы уверены?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            quit()
        else:
            pass

    def pause_event(self):
        global isKaraoke
        if isKaraoke:
            self.karaoke.timer.stop()
        self.player.pause()

    def resizeEvent(self, event):
        palette = QPalette()
        img = QImage('slides/micro.jpg')
        scaled = img.scaled(self.size(), Qt.KeepAspectRatioByExpanding,
                            transformMode=Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled))
        self.setPalette(palette)

    def edit_event(self):
        play_song = self.contents[self.choice_song - 1]
        song_text = self.texts[self.choice_song - 1]
        self.helper = Helper(play_song, song_text)


class Adder(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        instuction = 'Введите путь к файлам с музыкой и текстом'
        self.instruction_label = QLabel(instuction, self)
        self.song_label = QLabel('Песня', self)
        self.text_label = QLabel('Текст', self)
        self.instruction_label.move(10, 10)
        self.song_label.move(10, 50)
        self.text_label.move(10, 100)
        self.song_edit = QLineEdit(self)
        self.song_edit.move(75, 50)
        self.text_edit = QLineEdit(self)
        self.text_edit.move(75, 100)

        self.new_line_button = QPushButton('Принять', self)
        self.new_line_button.clicked.connect(self.accept_event)
        self.new_line_button.resize(self.new_line_button.sizeHint())
        self.new_line_button.move(125, 150)

        self.setGeometry(0, 0, 400, 250)
        self.setWindowTitle('Добавить песню')
        self.show()

    def accept_event(self):
        global current_adder
        self.text = self.text_edit.text()
        self.song = self.song_edit.text()
        if (self.text != "" and self.song != "" and
            os.path.isfile(self.song) and os.path.isfile(self.text) and
           ".mp3" in self.song and ".txt" in self.text):
            current_adder = (self.song, self.text)
            self.close()
        else:
            pass


class Karaoke(QWidget):
    def __init__(self, text):
        super().__init__()
        self.initUI()
        self.timings = []
        self.lines = []
        self.words_timings = []
        self.slides = ["slides/winter1.jpg",
                       "slides/winter2.jpg",
                       "slides/winter3.jpg"]
        self.current_slide = 0
        self.text = open(text, encoding="utf-8")
        for line in self.text:
            pattern = re.match(r"\[(.*)\](.*)\((.*)\)", line)
            self.timings.append(pattern.group(1))
            self.lines.append(pattern.group(2))
            self.words_timings.append(pattern.group(3))
        self.current_line = ""
        self.flag = 0
        self.current_line_words = []
        self.begin_time = time.time()
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

    def initUI(self):
        self.setGeometry(0, 0, 1270, 700)
        self.setWindowTitle('Караоке')
        self.show()

    def tick(self):
        self.time_left = time.time() - self.begin_time
        normal_time = self.get_normal_time()
        for i in range(len(self.timings)):
            if self.timings[i] == normal_time:
                self.current_line_timings = []
                self.current_line_words = self.lines[i].split()
                timings = self.words_timings[i].split(", ")
                for i in range(len(self.current_line_words)):
                    tim = float(timings[i])
                    self.current_line_timings.append(tim)

    def get_normal_time(self):
        minutes = int(self.time_left // 60)
        seconds = int(self.time_left % 60)
        if ((seconds % 20) == 0 and (self.flag - (60 * minutes)) < seconds):
            self.flag += 20
            self.get_slide()
        if (self.time_left % 60) < 10:
            return ("0" + str(minutes) + ":0" + str(seconds))
        else:
            return ("0" + str(minutes) + ":" + str(seconds))

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setFont(QFont('Decorative', 10))
        lenght = 0
        for i in range(len(self.current_line_words)):
            word = self.current_line_words[i]
            if self.current_line_timings[i] >= self.time_left:
                qp.setPen(QColor(255, 255, 255))
            else:
                qp.setPen(QColor(164, 34, 3))
            qp.drawText(50+(i*10)+lenght, 150, "{}".format(word))
            lenght += len(word)*12
        self.update()

    def resizeEvent(self, event):
        palette = QPalette()
        img = QImage('slides/winter1.jpg')
        scaled = img.scaled(self.size(), Qt.KeepAspectRatioByExpanding,
                            transformMode=Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled))
        self.setPalette(palette)

    def get_slide(self):
        if self.current_slide == (len(self.slides)-1):
            self.current_slide = 0
        else:
            self.current_slide += 1
        palette = QPalette()
        img = QImage(self.slides[self.current_slide])
        scaled = img.scaled(self.size(), Qt.KeepAspectRatioByExpanding,
                            transformMode=Qt.SmoothTransformation)
        palette.setBrush(QPalette.Window, QBrush(scaled))
        self.setPalette(palette)

    def closeEvent(self, event):
        global isKaraoke
        isKaraoke = False


class Helper(QWidget):
    def __init__(self, song, text):
        super().__init__()
        self.initUI()
        self.timing = 0
        self.song = song
        self.is_song = False
        self.player = M.QMediaPlayer()
        self.text = open(text, encoding="utf-8")
        self.lines = []
        self.words_timings = []
        self.int_words_timings = []
        for line in self.text:
            self.lines.append(line)
        self.flag = 0
        self.stop_timer = True
        self.current_line = self.lines[self.flag]

    def initUI(self):

        self.play_button = QPushButton('играть', self)
        self.play_button.clicked.connect(self.play_event)
        self.play_button.resize(self.play_button.sizeHint())
        self.play_button.move(100, 100)

        self.pause_button = QPushButton('пауза', self)
        self.pause_button.clicked.connect(self.pause_event)
        self.pause_button.resize(self.pause_button.sizeHint())
        self.pause_button.move(100, 150)

        self.new_line_button = QPushButton('новая строка', self)
        self.new_line_button.clicked.connect(self.new_line_event)
        self.new_line_button.resize(self.new_line_button.sizeHint())
        self.new_line_button.move(250, 100)

        self.prev_line_button = QPushButton('предыдущая строка', self)
        self.prev_line_button.clicked.connect(self.prev_line_event)
        self.prev_line_button.resize(self.prev_line_button.sizeHint())
        self.prev_line_button.move(250, 150)

        self.time_button = QPushButton('засечь время', self)
        self.time_button.clicked.connect(self.time_event)
        self.time_button.resize(self.time_button.sizeHint())
        self.time_button.move(450, 100)

        self.clear_button = QPushButton('очистить тайминги', self)
        self.clear_button.clicked.connect(self.clear_event)
        self.clear_button.resize(self.clear_button.sizeHint())
        self.clear_button.move(250, 450)

        self.text_edit = QLineEdit(self)
        self.text_edit.move(200, 600)

        self.setGeometry(0, 0, 900, 800)
        self.setWindowTitle('Караоке')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def clear_event(self, event):
        self.words_timings = []
        self.int_words_timings = []
        self.text_edit.setText("")

    def time_event(self, event):
        if self.stop_timer:
            self.words_timings.append(str(round(self.timing, 2)))
            self.int_words_timings.append(round(self.timing, 2))
        else:
            tim = round(self.timing + (time.time() - self.begin_time), 2)
            self.words_timings.append(str(tim))
            self.int_words_timings.append(tim)
        self.text_edit.setText(str(self.int_words_timings))

    def new_line_event(self, event):
        if self.flag == len(self.lines) - 1:
            pass
        else:
            self.flag += 1
            self.current_line = self.lines[self.flag]

    def prev_line_event(self, event):
        if self.flag == 0:
            pass
        else:
            self.flag -= 1
            self.current_line = self.lines[self.flag]

    def play_event(self, event):
        if not self.is_song:
            self.stop_timer = False
            self.begin_time = time.time()
            self.is_song = True
            self.player.setMedia(self.song)
            self.player.play()
        elif not self.stop_timer:
            pass
        else:
            self.stop_timer = False
            self.begin_time = time.time()
            self.player.play()

    def pause_event(self, event):
        if not self.stop_timer:
            self.stop_timer = True
            self.timing += (time.time() - self.begin_time)
            self.player.pause()

    def drawText(self, event, qp):
        qp.setFont(QFont('Decorative', 10))
        lenght = 0
        qp.setPen(QColor(1, 34, 3))
        qp.drawText(50, 250, self.current_line)
        if self.stop_timer:
            qp.drawText(400, 50, str(round(self.timing, 2)))
        else:
            tim = round(self.timing + (time.time() - self.begin_time), 2)
            qp.drawText(400, 50, str(tim))
        for i in range(len(self.words_timings)):
            word = self.words_timings[i]
            qp.drawText(50+(i*10)+lenght, 550, "{}".format(word))
            lenght += len(word)*12
        self.update()

    def closeEvent(self, event):
        self.player.stop()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
