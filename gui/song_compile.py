import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox

class SongInfo(QWidget):
    def __init__(self):
        super().__init__()

        self.setGeometry(100, 100, 400, 300)

        self.title_label = QLabel('Title:')
        self.title_input = QLineEdit()

        self.artist_text_label = QLabel('Artist Text:')
        self.artist_text_input = QComboBox()
        self.artist_text_input.addItems(['By', 'As Made Famous By', 'From', 'Other'])
        self.artist_text_input.setCurrentText('By')
        self.artist_text_input.currentTextChanged.connect(self.handle_artist_text_change)

        self.other_artist_text_label = QLabel('Other Artist Text:')
        self.other_artist_text_input = QLineEdit()
        self.other_artist_text_input.setDisabled(True)

        self.other_artist_text_layout = QHBoxLayout()
        self.other_artist_text_layout.addWidget(self.other_artist_text_label)
        self.other_artist_text_layout.addWidget(self.other_artist_text_input)
        self.other_artist_text_widget = QWidget()
        self.other_artist_text_widget.setLayout(self.other_artist_text_layout)
        self.other_artist_text_widget.setHidden(True)

        self.artist_label = QLabel('Artist:')
        self.artist_input = QLineEdit()

        self.year_label = QLabel('Year:')
        self.year_input = QLineEdit()

        self.submit_button = QPushButton('Submit')
        self.submit_button.setDisabled(True)
        self.submit_button.clicked.connect(self.submit_song_info)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.title_input)
        layout.addWidget(self.artist_text_label)
        layout.addWidget(self.artist_text_input)
        layout.addWidget(self.other_artist_text_widget)
        layout.addWidget(self.artist_label)
        layout.addWidget(self.artist_input)
        layout.addWidget(self.year_label)
        layout.addWidget(self.year_input)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def handle_artist_text_change(self, text):
        if text == 'Other':
            self.other_artist_text_widget.setHidden(False)
            self.other_artist_text_input.setDisabled(False)
        else:
            self.other_artist_text_widget.setHidden(True)
            self.other_artist_text_input.setDisabled(True)

        self.check_fields_complete()

    def submit_song_info(self):
        title = self.title_input.text()
        artist_text = self.artist_text_input.currentText()
        artist = self.artist_input.text() if artist_text != 'Other' else self.other_artist_text_input.text()
        year = self.year_input.text()
        print(f'Title: {title}, Artist Text: {artist_text}, Artist: {artist}, Year: {year}')

    def check_fields_complete(self):
        if self.title_input.text() and self.artist_input.text() and (self.artist_text_input.currentText() != 'Other' or self.other_artist_text_input.text()):
            self.submit_button.setDisabled(False)
        else:
            self.submit_button.setDisabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SongInfo()
    window.show()
    sys.exit(app.exec())