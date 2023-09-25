
from PySide6.QtWidgets import (QHBoxLayout, QWidget, QLabel, QLineEdit, QComboBox, QPushButton, QCheckBox, QFileDialog,
                               QGridLayout, QButtonGroup, QRadioButton, QGroupBox)
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent

import sys
import os

sys.path.append(os.path.join(".."))

# from toolkit_functions import extract_pak as x_pak

class FullPackage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Full Package Compiler")

        self.game_select = QGroupBox("Game")
        game_select_layout = QHBoxLayout()
        self.game_select_group = QButtonGroup()
        game1 = QRadioButton('GH3')
        game2 = QRadioButton('GHWT')
        game3 = QRadioButton('GH5')
        game4 = QRadioButton('GHWoR')
        self.game_select_group.exclusive()
        game1.setChecked(True)
        game_select_layout.addWidget(game1)
        game_select_layout.addWidget(game2)
        game_select_layout.addWidget(game3)
        game_select_layout.addWidget(game4)
        self.game_select.setLayout(game_select_layout)


        self.title_label = QLabel('Title:')
        self.title_input = QLineEdit()


        self.artist_text_label = QLabel('Artist Text:')
        self.artist_text_input = QComboBox()
        self.artist_text_input.addItems(['By', 'As Made Famous By', 'From', 'Other'])
        self.artist_text_input.setCurrentText('By')

        self.artist_byline_text_input = QLineEdit()
        self.artist_byline_text_input.setDisabled(True)
        self.artist_text_input.currentTextChanged.connect(self.artist_text_change)

        self.artist_label = QLabel('Artist:')
        self.artist_input = QLineEdit()

        self.year_label = QLabel('Year:')
        self.year_input = QLineEdit()

        self.gender_label = QLabel('Gender:')
        self.gender_input = QComboBox()
        self.gender_input.addItems(['Male', 'Female', 'None'])
        self.gender_input.setCurrentText('None')

        self.genre_label = QLabel('Genre:')
        self.genre_input = QComboBox()
        self.genre_input.addItems(sorted(['Rock', 'Pop', 'Jazz', 'Country', 'Other']))

        options = QGridLayout()
        self.original_artist = QCheckBox('Original Artist')



        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.submit_song_info)

        layout = QGridLayout()
        layout.addWidget(self.game_select, 0, 0, 1, 2)
        layout.addWidget(self.title_label, 1, 0)
        layout.addWidget(self.title_input, 1, 1)
        layout.addWidget(self.artist_text_label, 2, 0)
        layout.addWidget(self.artist_text_input, 2, 1)
        layout.addWidget(self.artist_byline_text_input, 3, 1)
        layout.addWidget(self.artist_label, 4, 0)
        layout.addWidget(self.artist_input, 4, 1)
        layout.addWidget(self.year_label, 5, 0)
        layout.addWidget(self.year_input, 5, 1)


        self.setLayout(layout)

    def artist_text_change(self):
        if self.artist_text_input.currentText() == 'Other':
            self.artist_byline_text_input.setDisabled(False)
        else:
            self.artist_byline_text_input.setText('')
            self.artist_byline_text_input.setDisabled(True)

    def submit_song_info(self):
        print('Submitting song info')