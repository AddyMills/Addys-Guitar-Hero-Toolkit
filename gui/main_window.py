import io
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QGroupBox,
                               QGridLayout, QTextEdit, QStackedWidget)
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import QMargins
from pak_edit.pak_manipulation import PakExtract as pakEx
from gui_initialize import compile_package as compPack

class ConsoleOutput(io.StringIO):
    def __init__(self, console_widget):
        super().__init__()
        self.console_widget = console_widget

    def write(self, text):
        self.console_widget.append(text)
        self.console_widget.moveCursor(QTextCursor.End)

class AddysToolkit(QMainWindow):
    def __init__(self, ghproj = ""):
        super().__init__()

        self.ghproj = ghproj
        self.initUI()
        # if self.ghproj:
        self.stacked_widget.setCurrentIndex(1)
        # self.initConsole()

    def initUI(self):
        self.setWindowTitle("Addy's Guitar Hero Toolkit")
        self.setGeometry(100, 100, 400, 300)

        central_widget = QWidget(self)
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(central_widget)

        main_container = QWidget(self)
        main_container_layout = QVBoxLayout()
        main_container_layout.addWidget(self.stacked_widget)

        main_container.setLayout(main_container_layout)

        layout = QVBoxLayout()

        # Pak/QB Manipulation
        pak_qb_group = QGroupBox("Pak/QB Manipulation")
        pak_qb_layout = QVBoxLayout()

        extract_pak_btn = QPushButton("Extract PAK")
        extract_pak_btn.clicked.connect(self.extract_pak)
        pak_qb_layout.addWidget(extract_pak_btn)

        convert_qb_btn = QPushButton("QB2Text2QB")
        convert_qb_btn.clicked.connect(self.qb_to_text)
        pak_qb_layout.addWidget(convert_qb_btn)

        compile_pak_btn = QPushButton("PAK Compilation")
        compile_pak_btn.clicked.connect(self.compile_pak)
        pak_qb_layout.addWidget(compile_pak_btn)

        pak_qb_group.setLayout(pak_qb_layout)
        layout.addWidget(pak_qb_group)

        # Compile a Song
        song_group = QGroupBox("Compile a Song")
        song_layout = QVBoxLayout()

        full_package_btn = QPushButton("Full Package w/ Audio")
        full_package_btn.clicked.connect(self.full_package)
        song_layout.addWidget(full_package_btn)

        compile_pak_midi_btn = QPushButton("Compile PAK from MIDI file")
        compile_pak_midi_btn.clicked.connect(self.compile_pak_midi)
        song_layout.addWidget(compile_pak_midi_btn)

        encrypt_fsb_btn = QPushButton("Encrypt FSB Audio")
        encrypt_fsb_btn.clicked.connect(self.encrypt_fsb)
        song_layout.addWidget(encrypt_fsb_btn)

        song_group.setLayout(song_layout)
        layout.addWidget(song_group)

        # GH3/GHA PC Customs
        customs_group = QGroupBox("GH3/GHA PC Customs")
        customs_layout = QVBoxLayout()

        load_gh3_btn = QPushButton("Load GH3")
        load_gh3_btn.clicked.connect(self.load_gh3)
        customs_layout.addWidget(load_gh3_btn)

        load_gha_btn = QPushButton("Load GHA")
        load_gha_btn.clicked.connect(self.load_gha)
        customs_layout.addWidget(load_gha_btn)

        customs_group.setLayout(customs_layout)
        layout.addWidget(customs_group)

        # Other Tools
        tools_group = QGroupBox("Other Tools")
        tools_layout = QVBoxLayout()

        gh3_gha_conversion_btn = QPushButton("GH3 <-> GHA Conversion")
        gh3_gha_conversion_btn.clicked.connect(self.gh3_gha_conversion)
        tools_layout.addWidget(gh3_gha_conversion_btn)

        wt_gh5_conversion_btn = QPushButton("WT -> GH5 Conversion")
        wt_gh5_conversion_btn.clicked.connect(self.wt_gh5_conversion)
        tools_layout.addWidget(wt_gh5_conversion_btn)

        tools_group.setLayout(tools_layout)
        layout.addWidget(tools_group)

        # self.console_log = QTextEdit(self)
        # self.console_log.setReadOnly(True)

        # main_container_layout.addWidget(self.console_log)

        central_widget.setLayout(layout)

        full_package_page = self.create_full_package_page()
        self.stacked_widget.addWidget(full_package_page)

        self.setCentralWidget(main_container)

    def create_full_package_page(self):
        full_package_page = compPack(self.ghproj)

        # Add a back button to return to the main page
        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        # Assuming the layout is a QVBoxLayout, add the back button to the bottom of the layout
        # full_package_page.layout().addWidget(back_button)

        return full_package_page

    def extract_pak(self):
        # Add functionality to extract PAK file
        self.pak_ex = pakEx()
        self.pak_ex.show()


    def qb_to_text(self):
        # Add functionality to convert QB files to text
        pass

    def compile_pak(self):
        # Add functionality to compile PAK file
        pass

    def full_package(self):
        self.stacked_widget.setCurrentIndex(1)

    def compile_pak_midi(self):
        pass

    def encrypt_fsb(self):
        pass

    def load_gh3(self):
        pass

    def load_gha(self):
        pass

    def gh3_gha_conversion(self):
        pass

    def wt_gh5_conversion(self):
        pass

    def initConsole(self):
        sys.stdout = ConsoleOutput(self.console_log)
