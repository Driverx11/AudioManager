from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDesktopWidget, QGridLayout, QFrame, QLabel, QScrollArea, QListWidget, QListWidgetItem, QSlider, QHBoxLayout, QComboBox, QMessageBox
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from db import Books
from book import *
from position import *
import os
import webbrowser

class VentanaLibros(QMainWindow):

    def __init__(self):
        super().__init__()
        self.index_guardado = 0
        self.book_name = None
        self.selected_item = None
        self.clear = False
        self.database = Books()
        self.book = Book(None, None)
        self.initUI()

    
    def initUI(self):
        self.setWindowTitle('Audio Manager - Home')
        self.setWindowIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","app_icon.png")))
        self.resize(270, 400)
        
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)

        items_list_button = QPushButton('Books/Playlists')
        items_list_button.clicked.connect(self.show_books)
        
        how_to_use_button = QPushButton('How to use')
        how_to_use_button.clicked.connect(self.show_how_to_use)

        readMe_button = QPushButton('ReadMe')
        readMe_button.clicked.connect(self.show_readme)

        layout.addWidget(items_list_button)
        layout.addWidget(how_to_use_button)
        layout.addWidget(readMe_button)

        container_widget.setLayout(layout)
        self.setCentralWidget(container_widget)
        self.center()
        
    def show_books(self):
        self.setWindowTitle("AudioManager - Books")
        self.setWindowIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","app_icon.png")))
        self.resize(270, 400)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setWidgetResizable(False)

        container_widget = QWidget()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.LowLatency)

        layout = QVBoxLayout(container_widget)

        add_button = QPushButton('Add book/playlist')
        add_button.clicked.connect(self.reload_books_added)

        del_button = QPushButton('Delete book/playlist')
        del_button.clicked.connect(self.select_elimination)

        manager_buttons = QHBoxLayout()
        manager_buttons.addWidget(add_button)
        manager_buttons.addWidget(del_button)
        
        self.name_books = [os.path.basename(path) for path in self.database.search_books()]
        path_books = self.database.search_books()
        booksLayout = QGridLayout()
        row, col = 0, 0
        for index, book in enumerate(self.name_books):
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

        if len(self.name_books) > 20:
            layout.setContentsMargins(10, 5, 25, 5)
        else:
            layout.setContentsMargins(10, 5, 10, 5)

        button_home = QPushButton('Home')
        button_home.clicked.connect(self.button_home)

        layout.addLayout(manager_buttons)
        layout.addLayout(booksLayout)
        layout.addWidget(button_home)
        
        container_widget.setLayout(layout)
        scroll_area.setWidget(container_widget)
        self.setCentralWidget(scroll_area)

       
        self.center()


    def show_chapters(self, book_path):
        self.setWindowTitle("AudioManager - Chapters")
        self.setWindowIcon(QIcon(os.path.join(os.path.expanduser("~"), "ProyectosPyQt","AudioManager", "ProyectoAudible", "images","app_icon.png")))
        self.resize(270, 400)

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

        self.book_name = os.path.basename(os.path.dirname(chapter))
        backButton = QPushButton('Menu')
        backButton.clicked.connect(self.go_back_menu)
        

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

        self.center()

    def go_back_menu(self):
        self.selected_item = self.list_widget.currentItem().text()
        self.button_back(self.book_name, self.list_widget.currentItem().text())

    def show_how_to_use(self):
        QMessageBox.information(self, "How to use", "To play an episode, double click on")


    def show_readme(self):
         webbrowser.open("https://github.com/Driverx11/AudioManager/blob/main/README.md")


    def center(self):
        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.center())


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

    def reload_books_added(self):
        #Reloads the list of books
        self.database.add_book()
        self.show_books()


    def reload_books_deleted(self):
        selected_book = self.combo_box.itemData(self.combo_box.currentIndex()).get("info")
        path_books = [path for path in self.database.search_books()]
        for book in path_books:
            if selected_book == book:
                self.database.delete_book(selected_book)
                self.show_books()
                
            

    def select_elimination(self):
        self.setWindowTitle('Book list')
        self.center()

        container = QWidget()
        layout_books = QVBoxLayout()

        self.combo_box = QComboBox()
        index = 0
        path_books = [path for path in self.database.search_books()]
        for book in path_books:
            self.combo_box.addItem(os.path.basename(book))
            self.combo_box.setItemData(index, {"info": book})
            index += 1

        label = QLabel("Which one do you want to delete?")

        del_button = QPushButton("Delete book", self)
        del_button.clicked.connect(self.reload_books_deleted)

        layout_books.addWidget(label)
        layout_books.addWidget(self.combo_box)
        layout_books.addWidget(del_button)
        container.setLayout(layout_books)
        self.setCentralWidget(container)


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
        new_episode = min(index + 1, self.list_widget.count() - 1 )
        self.list_widget.setCurrentRow(new_episode)
        self.on_item_double_clicked(self.list_widget.currentItem())


    def go_previous_episode(self):
        index = self.list_widget.currentRow()
        new_episode = max(index - 1, 0)
        self.list_widget.setCurrentRow(new_episode)
        self.on_item_double_clicked(self.list_widget.currentItem())
    

    def button_back(self, book, chapter):
        self.checkPoint(book, chapter)
        self.show_books()

    def button_home(self):
        self.initUI()

    def checkPoint(self, book, chapter):
        # Save the current position of the audio
        position = Position(book, chapter, max(self.mediaPlayer.position() - 2000, 0))
        print(self.mediaPlayer.position())
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
        # Updates the position of the audio
        if self.index_guardado < 1:
            self.checkPoint(self.book_name, self.list_widget.currentItem().text())
            self.index_guardado += 1

        first_value = self.slider.value()
        self.slider.setValue(position)
        last_value = self.slider.value()

        if last_value - first_value >= 1000:
            self.checkPoint(self.book_name, self.list_widget.currentItem().text())
            
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
