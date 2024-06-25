from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, QGridLayout, QFrame, QLabel, QScrollArea, QListWidget, QListWidgetItem, QSlider
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from db import Books
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
            book_button = QPushButton("Open Book")
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
            self.playButton.setText('Play')
        else:
            self.mediaPlayer.play()
            self.playButton.setText('Pause')


    def on_item_double_clicked(self, item):
        chapter_path = item.data(Qt.UserRole)
        chapter_name = item.text()
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(chapter_path)))
        self.mediaPlayer.play()
        self.playButton.setText('Pause')

        backButton = QPushButton('Back')
        backButton.clicked.connect(lambda: self.boton_back(os.path.basename(os.path.dirname(chapter_path)), chapter_name))

        # Añadir slider y etiqueta de duración
        layout = self.centralWidget().layout()
        layout.addWidget(self.slider)
        layout.addWidget(self.label_duration)
        layout.addWidget(backButton)


    def show_chapters(self, book_path):
        chapters = self.database.search_chapters(book_path)
        list_widget = QListWidget()
        list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)
        self.mediaPlayer.positionChanged.connect(self.update_position)
        self.mediaPlayer.durationChanged.connect(self.update_duration)

        for chapter in chapters:
            item = QListWidgetItem(os.path.basename(chapter))
            item.setData(Qt.UserRole, chapter)
            list_widget.addItem(item)

        folder_name = os.path.basename(os.path.dirname(chapter))
        #backButton = QPushButton('Back')
#        backButton.clicked.connect(lambda: self.boton_back(folder_name, chapter_name))

        self.setWindowTitle('Audio Manager')
        self.center()

        container_widget = QWidget()

        self.playButton = QPushButton('Play')
        self.playButton.clicked.connect(self.play_pause)

        layout = QVBoxLayout(container_widget)
        layout.addWidget(list_widget)
        layout.addWidget(self.playButton)

        # Add QSlider and QLabel 
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)

        self.label_duration = QLabel("00:00:00 / 00:00:00")
        layout.addWidget(self.slider)
        layout.addWidget(self.label_duration)

        #layout.addWidget(backButton)

        container_widget.setLayout(layout)
        self.setCentralWidget(container_widget)


    def boton_back(self, book, chapter):
        self.initUI()
        self.checkPoint(book, chapter)


    def checkPoint(self, book, chapter):
        # Save the current position of the audio
        self.database.save_position(self.mediaPlayer.position(), book, chapter)


    def update_position(self, position):
        self.slider.setValue(position)
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
