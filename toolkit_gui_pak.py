import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget
from PySide6.QtCore import Slot

class FileProcessor(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Mass PAK Extractor')

        self.layout = QVBoxLayout()

        self.folder_label = QLabel('No folder selected')
        self.layout.addWidget(self.folder_label)

        self.folder_button = QPushButton('Select folder', self)
        self.folder_button.clicked.connect(self.select_folder)
        self.layout.addWidget(self.folder_button)

        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        self.process_button = QPushButton('Extract PAK files', self)
        self.process_button.clicked.connect(self.process_files)
        self.layout.addWidget(self.process_button)

        self.setLayout(self.layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select folder')
        if folder:
            self.folder_label.setText(f'Selected folder: {folder}')
            self.populate_file_list(folder)

    def populate_file_list(self, folder):
        self.file_list.clear()
        for file in os.listdir(folder):
            if os.path.isfile(os.path.join(folder, file)):
                self.file_list.addItem(os.path.join(folder, file))

    def process_files(self):
        for index in range(self.file_list.count()):
            file_path = self.file_list.item(index).text()
            self.perform_action(file_path)

    def perform_action(self, file_path):
        # Implement your custom action here
        print(f'Processing: {file_path}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    file_processor = FileProcessor()
    file_processor.show()
    sys.exit(app.exec())