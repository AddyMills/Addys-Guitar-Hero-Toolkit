from PySide6.QtWidgets import (QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog)
from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent

import sys

sys.path.append("..\\")

from toolkit_functions import extract_pak as x_pak

class PakExtract(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Extract PAK File")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.pak_input_label = QLabel('PAK Input File:', self)
        layout.addWidget(self.pak_input_label)

        self.pak_input_field = FileDropLineEdit(self)
        self.pak_input_field.setPlaceholderText('Drag and drop PAK file or click to browse...')
        self.pak_input_field.setAcceptDrops(True)
        self.pak_input_field.installEventFilter(self)
        self.pak_input_field.fileDropped.connect(self.set_output_filename)  # Connect the signal
        layout.addWidget(self.pak_input_field)

        self.output_label = QLabel('Output Folder:', self)
        layout.addWidget(self.output_label)

        self.output_field = QLineEdit(self)
        self.output_field.setPlaceholderText('Output file will be automatically generated...')
        layout.addWidget(self.output_field)

        self.extract_button = QPushButton('Extract', self)
        self.extract_button.clicked.connect(self.extract_pak)
        layout.addWidget(self.extract_button)

        self.setLayout(layout)


    def eventFilter(self, obj, event):
        if obj == self.pak_input_field and event.type() == QEvent.DragEnter:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
            else:
                event.ignore()
        elif obj == self.pak_input_field and event.type() == QEvent.MouseButtonPress:
            if not self.pak_input_field.text():
                options = QFileDialog.Options()
                filename, _ = QFileDialog.getOpenFileName(self, "Open PAK File", "",
                                                          "PAK Files (*.pak *.pak.xen *.pak.ps3)", options=options)
                if filename:
                    self.pak_input_field.setText(filename)
                    self.set_output_filename()
        return super().eventFilter(obj, event)

    def set_input_filepath(self, filepath):
        self.pak_input_field.setText(filepath)
        self.set_output_filename()

    def set_output_filename(self):
        pak_filename = self.pak_input_field.text()
        if pak_filename.endswith(('.pak', '.pak.xen', 'pak.ps3')):
            output_filename = pak_filename[:pak_filename.find(".")]
            self.output_field.setText(output_filename)


    def extract_pak(self):
        if self.pak_input_field.text() and self.output_field.text():
            x_pak(self.pak_input_field.text(), self.output_field.text())
        elif self.pak_input_field.text():
            print("Output folder missing!")
        elif self.output_field.text():
            print("Input PAK missing!")
        else:
            print("Nothing found in either field!")

class FileDropLineEdit(QLineEdit):
    fileDropped = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            file_path = file_path.replace("/", "\\")
            self.setText(file_path)
            event.acceptProposedAction()
            self.fileDropped.emit()
        else:
            event.ignore()