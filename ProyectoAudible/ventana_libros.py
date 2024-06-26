from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, QGridLayout, QFrame, QLabel, QScrollArea, QListWidget, QListWidgetItem, QSlider, QHBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from db import Books
from position import *
import os

class VentanaLibros(QMainWindow):

    def __init__(self):
        super().__init__()
        self.database = Books()
        self.initUI()


    def initUI(self):
        self.setWindowTitle('Audio Manager')
        self.center()

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(False)

        container_widget = QWidget()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)

        layout = QVBoxLayout(container_widget)

        name_books = [os.path.basename(path) for path in self.database.search_books()]
        path_books = self.database.search_books()
        booksLayout = QGridLayout()
        row, col = 0, 0
        for index, book in enumerate(name_books):
            book_frame = QFrame()
            saved_book = self.return_book()
            
            book_button = QPushButton()
            if book == saved_book:
                book_button.setStyleSheet("background-color: #6EEA5A;")
            book_button.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","book_icon.png")))
            book_button.clicked.connect(lambda _, p=path_books[index]: self.show_chapters(p))
            book_frame.setFrameShape(QFrame.Box)
            book_label = QLabel(book)
            book_layout = QVBoxLayout()
            book_layout.addWidget(book_label, alignment=Qt.AlignCenter)
            book_layout.addWidget(book_button)
            book_frame.setLayout(book_layout)
            booksLayout.addWidget(book_frame, row, col)
            col += 1
            if col == 2:
                col = 0
                row += 1

        if len(name_books) > 10:
            layout.setContentsMargins(10, 0, 25, 0)
        else:
            layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(booksLayout)

        container_widget.setLayout(layout)
        scroll_area.setWidget(container_widget)
        self.setCentralWidget(scroll_area)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","play_icon.png")))
        else:
            self.mediaPlayer.play()
            self.playButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","pause_icon.png")))


    def on_item_double_clicked(self, item):
        #Simulates a double click on a chapter to initiate the play of the audio
        chapter_path = item.data(Qt.UserRole)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(chapter_path)))
        self.mediaPlayer.play()
        self.playButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","pause_icon.png")))


    def clicked_on_saved_position(self, item):
        #Loads the last known moment played of the chapter
        chapter_path = item.data(Qt.UserRole)
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(chapter_path)))
        if not self.return_position() == None:
            self.mediaPlayer.setPosition(self.return_position())
        self.mediaPlayer.play()
        self.playButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","pause_icon.png")))


    def show_chapters(self, book_path):
        self.chapters = self.database.search_chapters(book_path)

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)
        self.mediaPlayer.positionChanged.connect(self.update_position)
        self.mediaPlayer.durationChanged.connect(self.update_duration)
        self.chapter_coincidence = False

        for chapter in self.chapters:
            item = QListWidgetItem(os.path.basename(chapter))
            item.setData(Qt.UserRole, chapter)
            self.list_widget.addItem(item)
            if item.text() == self.return_chapter():
                self.list_widget.setCurrentItem(item)
                self.chapter_coincidence = True
                self.actual_item = item

        book_name = os.path.basename(os.path.dirname(chapter))
        backButton = QPushButton('Menu')
        backButton.clicked.connect(lambda: self.boton_back(book_name, self.list_widget.currentItem().text()))

        self.setWindowTitle('Audio Manager')
        self.center()

        container_widget = QWidget()

        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","play_icon.png")))
        self.playButton.clicked.connect(self.play_pause)

        # Create buttons for rewinding and forwarding 10 seconds
        rewindButton = QPushButton()
        rewindButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images", "rewind10sec_icon.png")))
        rewindButton.clicked.connect(self.rewind_10s)

        forwardButton = QPushButton()
        forwardButton.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","forward10sec_icon.png")))
        forwardButton.clicked.connect(self.forward_10s)

        #Create next and previous episode buttons
        next_episode = QPushButton()
        next_episode.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","next_episode_icon.png")))
        next_episode.clicked.connect(self.go_next_episode)

        previous_episode = QPushButton()
        previous_episode.setIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","previous_episode_icon.png")))
        previous_episode.clicked.connect(self.go_previous_episode)

        # Layout for the media control buttons
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(previous_episode)
        controls_layout.addWidget(rewindButton)
        controls_layout.addWidget(self.playButton)
        controls_layout.addWidget(forwardButton)
        controls_layout.addWidget(next_episode)

        layout = QVBoxLayout(container_widget)
        layout.addWidget(self.list_widget)
        layout.addLayout(controls_layout)

        # Add QSlider and QLabel 
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.label_duration = QLabel("00:00:00 / 00:00:00")
        layout.addWidget(self.label_duration, alignment=Qt.AlignCenter)
        layout.addWidget(self.slider)

        layout.addWidget(backButton)

        container_widget.setLayout(layout)
        self.setCentralWidget(container_widget)
        if self.chapter_coincidence:
            self.clicked_on_saved_position(self.actual_item)
        else:
            self.list_widget.setCurrentRow(0)
            self.on_item_double_clicked(self.list_widget.currentItem())


    def rewind_10s(self):
        current_position = self.mediaPlayer.position()
        new_position = max(0, current_position - 10000)  # Retrocede 10 segundos
        self.mediaPlayer.setPosition(new_position)


    def forward_10s(self):
        current_position = self.mediaPlayer.position()
        new_position = min(self.mediaPlayer.duration(), current_position + 10000)  # Avanza 10 segundos
        self.mediaPlayer.setPosition(new_position)


    def go_next_episode(self):
        index = self.list_widget.currentRow()
        new_episode = min(index + 1, self.list_widget.count())
        self.list_widget.setCurrentRow(new_episode)
        self.on_item_double_clicked(self.list_widget.currentItem())


    def go_previous_episode(self):
        index = self.list_widget.currentRow()
        new_episode = max(index - 1, 0)
        self.list_widget.setCurrentRow(new_episode)
        self.on_item_double_clicked(self.list_widget.currentItem())
    

    def boton_back(self, book, chapter):
        self.checkPoint(book, chapter)
        self.initUI()
        

    def checkPoint(self, book, chapter):
        # Save the current position of the audio
        position = Position(book, chapter, self.mediaPlayer.position())
        self.database.save_position(position)
    

    def return_book(self):
        return self.database.obtain_position().book
    
    def return_chapter(self):
        return self.database.obtain_position().chapter
    
    def return_position(self):
        return self.database.obtain_position().position

    def check_time(self):
        #Checks when the chapter finishes to continue with the next one
        if self.mediaPlayer.duration() > 0:
            if self.mediaPlayer.duration() - self.mediaPlayer.position() < 500:
                print(f'{self.mediaPlayer.duration() - self.mediaPlayer.position()}')
                current_index = self.list_widget.currentRow()
                if current_index < self.list_widget.count() - 1:
                    new_index = current_index + 1
                    self.list_widget.setCurrentRow(new_index)
                    item = self.list_widget.currentItem()
                    self.on_item_double_clicked(item)


    def update_position(self, position):
        self.slider.setValue(position)
        self.check_time()
        self.update_duration_label()
        

    def update_duration(self, duration):
        self.slider.setRange(0, duration)
        self.update_duration_label()


    def set_position(self, position):
        self.mediaPlayer.setPosition(position)


    def update_duration_label(self):
        position = self.mediaPlayer.position()
        duration = self.mediaPlayer.duration()
        
        pos_time = self.format_time(position)
        dur_time = self.format_time(duration)
        
        self.label_duration.setText(f"{pos_time} / {dur_time}")


    def format_time(self, ms):
        seconds = ms // 1000
        minutes = seconds // 60
        hours = minutes // 60
        seconds = seconds % 60
        minutes = minutes % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"
