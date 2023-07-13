# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compile_package.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
    QDoubleSpinBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QRadioButton, QSizePolicy, QSpinBox, QTabWidget,
    QToolButton, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(562, 659)
        self.verticalLayout_11 = QVBoxLayout(Form)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.compile_tabs = QTabWidget(Form)
        self.compile_tabs.setObjectName(u"compile_tabs")
        self.compile_tabs.setEnabled(True)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.compile_tabs.sizePolicy().hasHeightForWidth())
        self.compile_tabs.setSizePolicy(sizePolicy)
        self.compile_tabs.setDocumentMode(True)
        self.compile_tabs.setTabsClosable(False)
        self.compile_tabs.setMovable(False)
        self.metadata_tab = QWidget()
        self.metadata_tab.setObjectName(u"metadata_tab")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.metadata_tab.sizePolicy().hasHeightForWidth())
        self.metadata_tab.setSizePolicy(sizePolicy1)
        self.verticalLayout_2 = QVBoxLayout(self.metadata_tab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.metadata_widget = QWidget(self.metadata_tab)
        self.metadata_widget.setObjectName(u"metadata_widget")
        self.verticalLayout_8 = QVBoxLayout(self.metadata_widget)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.game_select = QGroupBox(self.metadata_widget)
        self.game_select.setObjectName(u"game_select")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.game_select.sizePolicy().hasHeightForWidth())
        self.game_select.setSizePolicy(sizePolicy2)
        self.game_select.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.horizontalLayout = QHBoxLayout(self.game_select)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.gh3 = QRadioButton(self.game_select)
        self.game_select_group = QButtonGroup(Form)
        self.game_select_group.setObjectName(u"game_select_group")
        self.game_select_group.addButton(self.gh3)
        self.gh3.setObjectName(u"gh3")
        self.gh3.setEnabled(False)
        self.gh3.setText(u"GH3")
        self.gh3.setChecked(False)

        self.horizontalLayout.addWidget(self.gh3)

        self.gha = QRadioButton(self.game_select)
        self.game_select_group.addButton(self.gha)
        self.gha.setObjectName(u"gha")
        self.gha.setEnabled(False)

        self.horizontalLayout.addWidget(self.gha)

        self.ghwt = QRadioButton(self.game_select)
        self.game_select_group.addButton(self.ghwt)
        self.ghwt.setObjectName(u"ghwt")
        self.ghwt.setText(u"GHWT")
        self.ghwt.setChecked(True)

        self.horizontalLayout.addWidget(self.ghwt)

        self.gh5 = QRadioButton(self.game_select)
        self.game_select_group.addButton(self.gh5)
        self.gh5.setObjectName(u"gh5")
        self.gh5.setEnabled(False)
        self.gh5.setText(u"GH5")

        self.horizontalLayout.addWidget(self.gh5)

        self.ghwor = QRadioButton(self.game_select)
        self.game_select_group.addButton(self.ghwor)
        self.ghwor.setObjectName(u"ghwor")
        self.ghwor.setEnabled(True)
        self.ghwor.setText(u"GHWoR")

        self.horizontalLayout.addWidget(self.ghwor)


        self.verticalLayout_8.addWidget(self.game_select)

        self.metadata_fields = QWidget(self.metadata_widget)
        self.metadata_fields.setObjectName(u"metadata_fields")
        sizePolicy1.setHeightForWidth(self.metadata_fields.sizePolicy().hasHeightForWidth())
        self.metadata_fields.setSizePolicy(sizePolicy1)
        self.verticalLayout_6 = QVBoxLayout(self.metadata_fields)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.title_input = QLineEdit(self.metadata_fields)
        self.title_input.setObjectName(u"title_input")

        self.gridLayout.addWidget(self.title_input, 0, 1, 1, 4)

        self.artist_input = QLineEdit(self.metadata_fields)
        self.artist_input.setObjectName(u"artist_input")

        self.gridLayout.addWidget(self.artist_input, 3, 1, 1, 4)

        self.artist_text_label = QLabel(self.metadata_fields)
        self.artist_text_label.setObjectName(u"artist_text_label")

        self.gridLayout.addWidget(self.artist_text_label, 1, 0, 1, 1, Qt.AlignRight)

        self.cover_year_label = QLabel(self.metadata_fields)
        self.cover_year_label.setObjectName(u"cover_year_label")

        self.gridLayout.addWidget(self.cover_year_label, 4, 3, 1, 1, Qt.AlignRight)

        self.genre_label = QLabel(self.metadata_fields)
        self.genre_label.setObjectName(u"genre_label")

        self.gridLayout.addWidget(self.genre_label, 6, 0, 1, 1, Qt.AlignRight)

        self.year_input = QSpinBox(self.metadata_fields)
        self.year_input.setObjectName(u"year_input")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.year_input.sizePolicy().hasHeightForWidth())
        self.year_input.setSizePolicy(sizePolicy3)
        self.year_input.setMinimum(1900)
        self.year_input.setMaximum(3000)
        self.year_input.setValue(2023)
        self.year_input.setDisplayIntegerBase(10)

        self.gridLayout.addWidget(self.year_input, 4, 1, 1, 1)

        self.checksum_input = QLineEdit(self.metadata_fields)
        self.checksum_input.setObjectName(u"checksum_input")
        self.checksum_input.setClearButtonEnabled(False)

        self.gridLayout.addWidget(self.checksum_input, 9, 1, 1, 4)

        self.cover_checkbox = QCheckBox(self.metadata_fields)
        self.cover_checkbox.setObjectName(u"cover_checkbox")
        self.cover_checkbox.setChecked(False)

        self.gridLayout.addWidget(self.cover_checkbox, 4, 2, 1, 1)

        self.author_input = QLineEdit(self.metadata_fields)
        self.author_input.setObjectName(u"author_input")

        self.gridLayout.addWidget(self.author_input, 10, 1, 1, 4)

        self.genre_select = QComboBox(self.metadata_fields)
        self.genre_select.setObjectName(u"genre_select")

        self.gridLayout.addWidget(self.genre_select, 6, 1, 1, 4)

        self.year_label = QLabel(self.metadata_fields)
        self.year_label.setObjectName(u"year_label")

        self.gridLayout.addWidget(self.year_label, 4, 0, 1, 1, Qt.AlignRight)

        self.author_label = QLabel(self.metadata_fields)
        self.author_label.setObjectName(u"author_label")

        self.gridLayout.addWidget(self.author_label, 10, 0, 1, 1, Qt.AlignRight)

        self.title_label = QLabel(self.metadata_fields)
        self.title_label.setObjectName(u"title_label")

        self.gridLayout.addWidget(self.title_label, 0, 0, 1, 1, Qt.AlignRight)

        self.artist_text_other = QLineEdit(self.metadata_fields)
        self.artist_text_other.setObjectName(u"artist_text_other")
        self.artist_text_other.setEnabled(False)

        self.gridLayout.addWidget(self.artist_text_other, 2, 1, 1, 4)

        self.checksum_label = QLabel(self.metadata_fields)
        self.checksum_label.setObjectName(u"checksum_label")

        self.gridLayout.addWidget(self.checksum_label, 9, 0, 1, 1, Qt.AlignRight)

        self.cover_year_input = QSpinBox(self.metadata_fields)
        self.cover_year_input.setObjectName(u"cover_year_input")
        self.cover_year_input.setEnabled(False)
        self.cover_year_input.setMinimum(1900)
        self.cover_year_input.setMaximum(3000)
        self.cover_year_input.setValue(2023)

        self.gridLayout.addWidget(self.cover_year_input, 4, 4, 1, 1)

        self.artist_text_select = QComboBox(self.metadata_fields)
        self.artist_text_select.addItem("")
        self.artist_text_select.addItem("")
        self.artist_text_select.addItem("")
        self.artist_text_select.setObjectName(u"artist_text_select")

        self.gridLayout.addWidget(self.artist_text_select, 1, 1, 1, 4)

        self.line_2 = QFrame(self.metadata_fields)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.gridLayout.addWidget(self.line_2, 8, 0, 1, 5)

        self.artist_label = QLabel(self.metadata_fields)
        self.artist_label.setObjectName(u"artist_label")

        self.gridLayout.addWidget(self.artist_label, 3, 0, 1, 1, Qt.AlignRight)

        self.cover_artist_label = QLabel(self.metadata_fields)
        self.cover_artist_label.setObjectName(u"cover_artist_label")

        self.gridLayout.addWidget(self.cover_artist_label, 5, 0, 1, 1, Qt.AlignRight)

        self.cover_artist_input = QLineEdit(self.metadata_fields)
        self.cover_artist_input.setObjectName(u"cover_artist_input")
        self.cover_artist_input.setEnabled(False)

        self.gridLayout.addWidget(self.cover_artist_input, 5, 1, 1, 4)


        self.verticalLayout_6.addLayout(self.gridLayout)


        self.verticalLayout_8.addWidget(self.metadata_fields)


        self.verticalLayout_2.addWidget(self.metadata_widget, 0, Qt.AlignTop)

        self.compile_tabs.addTab(self.metadata_tab, "")
        self.audio_tab_wt = QWidget()
        self.audio_tab_wt.setObjectName(u"audio_tab_wt")
        self.verticalLayout_3 = QVBoxLayout(self.audio_tab_wt)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.wt_audio_widget = QWidget(self.audio_tab_wt)
        self.wt_audio_widget.setObjectName(u"wt_audio_widget")
        self.verticalLayout_9 = QVBoxLayout(self.wt_audio_widget)
        self.verticalLayout_9.setSpacing(6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.ghwt_stems_layout = QGridLayout()
        self.ghwt_stems_layout.setObjectName(u"ghwt_stems_layout")
        self.ghwt_stems_layout.setContentsMargins(0, 9, -1, 9)
        self.toms_input = QLineEdit(self.wt_audio_widget)
        self.toms_input.setObjectName(u"toms_input")
        self.toms_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.toms_input, 4, 2, 1, 1)

        self.backing_select = QToolButton(self.wt_audio_widget)
        self.backing_select.setObjectName(u"backing_select")
        self.backing_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.backing_select, 12, 3, 1, 1)

        self.cymbals_select = QToolButton(self.wt_audio_widget)
        self.cymbals_select.setObjectName(u"cymbals_select")
        self.cymbals_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.cymbals_select, 3, 3, 1, 1)

        self.line_4 = QFrame(self.wt_audio_widget)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setFrameShape(QFrame.HLine)
        self.line_4.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_4, 7, 0, 1, 4)

        self.bass_label = QLabel(self.wt_audio_widget)
        self.bass_label.setObjectName(u"bass_label")
        self.bass_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.bass_label, 8, 1, 1, 1)

        self.snare_select = QToolButton(self.wt_audio_widget)
        self.snare_select.setObjectName(u"snare_select")
        self.snare_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.snare_select, 2, 3, 1, 1)

        self.kick_label = QLabel(self.wt_audio_widget)
        self.kick_label.setObjectName(u"kick_label")
        self.kick_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.kick_label, 1, 1, 1, 1)

        self.bass_input = QLineEdit(self.wt_audio_widget)
        self.bass_input.setObjectName(u"bass_input")
        self.bass_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.bass_input, 8, 2, 1, 1)

        self.crowd_label = QLabel(self.wt_audio_widget)
        self.crowd_label.setObjectName(u"crowd_label")
        self.crowd_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.crowd_label, 14, 1, 1, 1)

        self.snare_label = QLabel(self.wt_audio_widget)
        self.snare_label.setObjectName(u"snare_label")
        self.snare_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.snare_label, 2, 1, 1, 1)

        self.line_8 = QFrame(self.wt_audio_widget)
        self.line_8.setObjectName(u"line_8")
        self.line_8.setFrameShape(QFrame.HLine)
        self.line_8.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_8, 15, 0, 1, 4)

        self.bass_select = QToolButton(self.wt_audio_widget)
        self.bass_select.setObjectName(u"bass_select")
        self.bass_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.bass_select, 8, 3, 1, 1)

        self.line_3 = QFrame(self.wt_audio_widget)
        self.line_3.setObjectName(u"line_3")
        self.line_3.setFrameShape(QFrame.HLine)
        self.line_3.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_3, 5, 0, 1, 4)

        self.vocals_input = QLineEdit(self.wt_audio_widget)
        self.vocals_input.setObjectName(u"vocals_input")
        self.vocals_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.vocals_input, 10, 2, 1, 1)

        self.guitar_select = QToolButton(self.wt_audio_widget)
        self.guitar_select.setObjectName(u"guitar_select")
        self.guitar_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.guitar_select, 6, 3, 1, 1)

        self.vocals_label = QLabel(self.wt_audio_widget)
        self.vocals_label.setObjectName(u"vocals_label")
        self.vocals_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.vocals_label, 10, 1, 1, 1)

        self.line_7 = QFrame(self.wt_audio_widget)
        self.line_7.setObjectName(u"line_7")
        self.line_7.setFrameShape(QFrame.HLine)
        self.line_7.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_7, 13, 0, 1, 4)

        self.toms_label = QLabel(self.wt_audio_widget)
        self.toms_label.setObjectName(u"toms_label")
        self.toms_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.toms_label, 4, 1, 1, 1)

        self.backing_input = QLineEdit(self.wt_audio_widget)
        self.backing_input.setObjectName(u"backing_input")
        self.backing_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.backing_input, 12, 2, 1, 1)

        self.toms_select = QToolButton(self.wt_audio_widget)
        self.toms_select.setObjectName(u"toms_select")
        self.toms_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.toms_select, 4, 3, 1, 1)

        self.guitar_label = QLabel(self.wt_audio_widget)
        self.guitar_label.setObjectName(u"guitar_label")
        self.guitar_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.guitar_label, 6, 1, 1, 1)

        self.crowd_select = QToolButton(self.wt_audio_widget)
        self.crowd_select.setObjectName(u"crowd_select")
        self.crowd_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.crowd_select, 14, 3, 1, 1)

        self.line_6 = QFrame(self.wt_audio_widget)
        self.line_6.setObjectName(u"line_6")
        self.line_6.setFrameShape(QFrame.HLine)
        self.line_6.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_6, 11, 0, 1, 4)

        self.cymbals_label = QLabel(self.wt_audio_widget)
        self.cymbals_label.setObjectName(u"cymbals_label")
        self.cymbals_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.cymbals_label, 3, 1, 1, 1)

        self.label = QLabel(self.wt_audio_widget)
        self.label.setObjectName(u"label")
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)
        self.label.setAlignment(Qt.AlignCenter)

        self.ghwt_stems_layout.addWidget(self.label, 0, 2, 1, 1)

        self.track_label = QLabel(self.wt_audio_widget)
        self.track_label.setObjectName(u"track_label")
        sizePolicy2.setHeightForWidth(self.track_label.sizePolicy().hasHeightForWidth())
        self.track_label.setSizePolicy(sizePolicy2)
        self.track_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.track_label, 0, 1, 1, 1)

        self.crowd_input = QLineEdit(self.wt_audio_widget)
        self.crowd_input.setObjectName(u"crowd_input")
        self.crowd_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.crowd_input, 14, 2, 1, 1)

        self.vocals_select = QToolButton(self.wt_audio_widget)
        self.vocals_select.setObjectName(u"vocals_select")
        self.vocals_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.vocals_select, 10, 3, 1, 1)

        self.cymbals_input = QLineEdit(self.wt_audio_widget)
        self.cymbals_input.setObjectName(u"cymbals_input")
        self.cymbals_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.cymbals_input, 3, 2, 1, 1)

        self.kick_select = QToolButton(self.wt_audio_widget)
        self.kick_select.setObjectName(u"kick_select")
        self.kick_select.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.kick_select, 1, 3, 1, 1)

        self.snare_input = QLineEdit(self.wt_audio_widget)
        self.snare_input.setObjectName(u"snare_input")
        self.snare_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.snare_input, 2, 2, 1, 1)

        self.backing_label = QLabel(self.wt_audio_widget)
        self.backing_label.setObjectName(u"backing_label")
        self.backing_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.ghwt_stems_layout.addWidget(self.backing_label, 12, 1, 1, 1)

        self.guitar_input = QLineEdit(self.wt_audio_widget)
        self.guitar_input.setObjectName(u"guitar_input")
        self.guitar_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.guitar_input, 6, 2, 1, 1)

        self.line_5 = QFrame(self.wt_audio_widget)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setFrameShape(QFrame.HLine)
        self.line_5.setFrameShadow(QFrame.Sunken)

        self.ghwt_stems_layout.addWidget(self.line_5, 9, 0, 1, 4)

        self.kick_input = QLineEdit(self.wt_audio_widget)
        self.kick_input.setObjectName(u"kick_input")
        self.kick_input.setEnabled(True)

        self.ghwt_stems_layout.addWidget(self.kick_input, 1, 2, 1, 1)


        self.verticalLayout_9.addLayout(self.ghwt_stems_layout)

        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.encrypt_audio = QCheckBox(self.wt_audio_widget)
        self.encrypt_audio.setObjectName(u"encrypt_audio")

        self.horizontalLayout_13.addWidget(self.encrypt_audio, 0, Qt.AlignRight)


        self.verticalLayout_9.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.preview_label = QLabel(self.wt_audio_widget)
        self.preview_label.setObjectName(u"preview_label")

        self.horizontalLayout_2.addWidget(self.preview_label)

        self.preview_minutes = QSpinBox(self.wt_audio_widget)
        self.preview_minutes.setObjectName(u"preview_minutes")

        self.horizontalLayout_2.addWidget(self.preview_minutes)

        self.preview_seconds = QSpinBox(self.wt_audio_widget)
        self.preview_seconds.setObjectName(u"preview_seconds")
        self.preview_seconds.setMaximum(59)
        self.preview_seconds.setValue(45)

        self.horizontalLayout_2.addWidget(self.preview_seconds)

        self.preview_mills = QSpinBox(self.wt_audio_widget)
        self.preview_mills.setObjectName(u"preview_mills")
        self.preview_mills.setMaximum(999)

        self.horizontalLayout_2.addWidget(self.preview_mills)

        self.length_label = QLabel(self.wt_audio_widget)
        self.length_label.setObjectName(u"length_label")

        self.horizontalLayout_2.addWidget(self.length_label)

        self.length_minutes = QSpinBox(self.wt_audio_widget)
        self.length_minutes.setObjectName(u"length_minutes")

        self.horizontalLayout_2.addWidget(self.length_minutes)

        self.length_seconds = QSpinBox(self.wt_audio_widget)
        self.length_seconds.setObjectName(u"length_seconds")
        self.length_seconds.setValue(30)

        self.horizontalLayout_2.addWidget(self.length_seconds)

        self.length_mills = QSpinBox(self.wt_audio_widget)
        self.length_mills.setObjectName(u"length_mills")
        self.length_mills.setMaximum(999)

        self.horizontalLayout_2.addWidget(self.length_mills)

        self.ghwt_set_end = QCheckBox(self.wt_audio_widget)
        self.ghwt_set_end.setObjectName(u"ghwt_set_end")

        self.horizontalLayout_2.addWidget(self.ghwt_set_end)


        self.verticalLayout_9.addLayout(self.horizontalLayout_2)


        self.verticalLayout_3.addWidget(self.wt_audio_widget)

        self.compile_tabs.addTab(self.audio_tab_wt, "")
        self.audio_tab_gh3 = QWidget()
        self.audio_tab_gh3.setObjectName(u"audio_tab_gh3")
        self.audio_tab_gh3.setEnabled(True)
        sizePolicy1.setHeightForWidth(self.audio_tab_gh3.sizePolicy().hasHeightForWidth())
        self.audio_tab_gh3.setSizePolicy(sizePolicy1)
        self.audio_tab_gh3.setLocale(QLocale(QLocale.English, QLocale.Netherlands))
        self.verticalLayout_5 = QVBoxLayout(self.audio_tab_gh3)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gh3_audio_widget = QWidget(self.audio_tab_gh3)
        self.gh3_audio_widget.setObjectName(u"gh3_audio_widget")
        self.verticalLayout_10 = QVBoxLayout(self.gh3_audio_widget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.gh3_stems_layout = QGridLayout()
        self.gh3_stems_layout.setObjectName(u"gh3_stems_layout")
        self.line_9 = QFrame(self.gh3_audio_widget)
        self.line_9.setObjectName(u"line_9")
        self.line_9.setFrameShape(QFrame.HLine)
        self.line_9.setFrameShadow(QFrame.Sunken)

        self.gh3_stems_layout.addWidget(self.line_9, 11, 0, 1, 3)

        self.guitar_label_gh3 = QLabel(self.gh3_audio_widget)
        self.guitar_label_gh3.setObjectName(u"guitar_label_gh3")
        self.guitar_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.guitar_label_gh3, 1, 0, 1, 1)

        self.track_label_2 = QLabel(self.gh3_audio_widget)
        self.track_label_2.setObjectName(u"track_label_2")
        sizePolicy2.setHeightForWidth(self.track_label_2.sizePolicy().hasHeightForWidth())
        self.track_label_2.setSizePolicy(sizePolicy2)
        self.track_label_2.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.track_label_2, 0, 0, 1, 1)

        self.guitar_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.guitar_select_gh3.setObjectName(u"guitar_select_gh3")
        self.guitar_select_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.guitar_select_gh3, 1, 2, 1, 1)

        self.coop_guitar_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.coop_guitar_input_gh3.setObjectName(u"coop_guitar_input_gh3")
        self.coop_guitar_input_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_guitar_input_gh3, 7, 1, 1, 1)

        self.rhythm_label_gh3 = QLabel(self.gh3_audio_widget)
        self.rhythm_label_gh3.setObjectName(u"rhythm_label_gh3")
        self.rhythm_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.rhythm_label_gh3, 2, 0, 1, 1)

        self.crowd_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.crowd_input_gh3.setObjectName(u"crowd_input_gh3")
        self.crowd_input_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.crowd_input_gh3, 12, 1, 1, 1)

        self.backing_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.backing_select_gh3.setObjectName(u"backing_select_gh3")
        self.backing_select_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.backing_select_gh3, 3, 2, 1, 1)

        self.coop_backing_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.coop_backing_select_gh3.setObjectName(u"coop_backing_select_gh3")
        self.coop_backing_select_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_backing_select_gh3, 10, 2, 1, 1)

        self.gh3_file_path_label = QLabel(self.gh3_audio_widget)
        self.gh3_file_path_label.setObjectName(u"gh3_file_path_label")
        sizePolicy2.setHeightForWidth(self.gh3_file_path_label.sizePolicy().hasHeightForWidth())
        self.gh3_file_path_label.setSizePolicy(sizePolicy2)
        self.gh3_file_path_label.setAlignment(Qt.AlignCenter)

        self.gh3_stems_layout.addWidget(self.gh3_file_path_label, 0, 1, 1, 1)

        self.guitar_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.guitar_input_gh3.setObjectName(u"guitar_input_gh3")
        self.guitar_input_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.guitar_input_gh3, 1, 1, 1, 1)

        self.backing_label_gh3 = QLabel(self.gh3_audio_widget)
        self.backing_label_gh3.setObjectName(u"backing_label_gh3")
        self.backing_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.backing_label_gh3, 3, 0, 1, 1)

        self.crowd_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.crowd_select_gh3.setObjectName(u"crowd_select_gh3")
        self.crowd_select_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.crowd_select_gh3, 12, 2, 1, 1)

        self.rhythm_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.rhythm_select_gh3.setObjectName(u"rhythm_select_gh3")
        self.rhythm_select_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.rhythm_select_gh3, 2, 2, 1, 1)

        self.coop_backing_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.coop_backing_input_gh3.setObjectName(u"coop_backing_input_gh3")
        self.coop_backing_input_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_backing_input_gh3, 10, 1, 1, 1)

        self.backing_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.backing_input_gh3.setObjectName(u"backing_input_gh3")
        self.backing_input_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.backing_input_gh3, 3, 1, 1, 1)

        self.coop_guitar_label_gh3 = QLabel(self.gh3_audio_widget)
        self.coop_guitar_label_gh3.setObjectName(u"coop_guitar_label_gh3")
        self.coop_guitar_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.coop_guitar_label_gh3, 7, 0, 1, 1)

        self.rhythm_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.rhythm_input_gh3.setObjectName(u"rhythm_input_gh3")
        self.rhythm_input_gh3.setEnabled(True)

        self.gh3_stems_layout.addWidget(self.rhythm_input_gh3, 2, 1, 1, 1)

        self.coop_rhythm_label_gh3 = QLabel(self.gh3_audio_widget)
        self.coop_rhythm_label_gh3.setObjectName(u"coop_rhythm_label_gh3")
        self.coop_rhythm_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.coop_rhythm_label_gh3, 9, 0, 1, 1)

        self.coop_rhythm_input_gh3 = QLineEdit(self.gh3_audio_widget)
        self.coop_rhythm_input_gh3.setObjectName(u"coop_rhythm_input_gh3")
        self.coop_rhythm_input_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_rhythm_input_gh3, 9, 1, 1, 1)

        self.crowd_label_gh3 = QLabel(self.gh3_audio_widget)
        self.crowd_label_gh3.setObjectName(u"crowd_label_gh3")
        self.crowd_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.crowd_label_gh3, 12, 0, 1, 1)

        self.coop_rhythm_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.coop_rhythm_select_gh3.setObjectName(u"coop_rhythm_select_gh3")
        self.coop_rhythm_select_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_rhythm_select_gh3, 9, 2, 1, 1)

        self.coop_guitar_select_gh3 = QToolButton(self.gh3_audio_widget)
        self.coop_guitar_select_gh3.setObjectName(u"coop_guitar_select_gh3")
        self.coop_guitar_select_gh3.setEnabled(False)

        self.gh3_stems_layout.addWidget(self.coop_guitar_select_gh3, 7, 2, 1, 1)

        self.coop_backing_label_gh3 = QLabel(self.gh3_audio_widget)
        self.coop_backing_label_gh3.setObjectName(u"coop_backing_label_gh3")
        self.coop_backing_label_gh3.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gh3_stems_layout.addWidget(self.coop_backing_label_gh3, 10, 0, 1, 1)

        self.gh3_audio_options = QHBoxLayout()
        self.gh3_audio_options.setObjectName(u"gh3_audio_options")
        self.p2_rhythm_check = QCheckBox(self.gh3_audio_widget)
        self.p2_rhythm_check.setObjectName(u"p2_rhythm_check")

        self.gh3_audio_options.addWidget(self.p2_rhythm_check)

        self.coop_audio_check = QCheckBox(self.gh3_audio_widget)
        self.coop_audio_check.setObjectName(u"coop_audio_check")
        self.coop_audio_check.setEnabled(False)

        self.gh3_audio_options.addWidget(self.coop_audio_check)


        self.gh3_stems_layout.addLayout(self.gh3_audio_options, 5, 1, 1, 1)


        self.verticalLayout_10.addLayout(self.gh3_stems_layout)

        self.gh3_preview_layout = QHBoxLayout()
        self.gh3_preview_layout.setObjectName(u"gh3_preview_layout")
        self.preview_label_2 = QLabel(self.gh3_audio_widget)
        self.preview_label_2.setObjectName(u"preview_label_2")

        self.gh3_preview_layout.addWidget(self.preview_label_2)

        self.preview_minutes_gh3 = QSpinBox(self.gh3_audio_widget)
        self.preview_minutes_gh3.setObjectName(u"preview_minutes_gh3")

        self.gh3_preview_layout.addWidget(self.preview_minutes_gh3)

        self.preview_seconds_gh3 = QSpinBox(self.gh3_audio_widget)
        self.preview_seconds_gh3.setObjectName(u"preview_seconds_gh3")
        self.preview_seconds_gh3.setMaximum(59)
        self.preview_seconds_gh3.setValue(45)

        self.gh3_preview_layout.addWidget(self.preview_seconds_gh3)

        self.preview_mills_gh3 = QSpinBox(self.gh3_audio_widget)
        self.preview_mills_gh3.setObjectName(u"preview_mills_gh3")
        self.preview_mills_gh3.setMaximum(999)

        self.gh3_preview_layout.addWidget(self.preview_mills_gh3)

        self.length_label_2 = QLabel(self.gh3_audio_widget)
        self.length_label_2.setObjectName(u"length_label_2")

        self.gh3_preview_layout.addWidget(self.length_label_2)

        self.length_minutes_gh3 = QSpinBox(self.gh3_audio_widget)
        self.length_minutes_gh3.setObjectName(u"length_minutes_gh3")

        self.gh3_preview_layout.addWidget(self.length_minutes_gh3)

        self.length_seconds_gh3 = QSpinBox(self.gh3_audio_widget)
        self.length_seconds_gh3.setObjectName(u"length_seconds_gh3")
        self.length_seconds_gh3.setValue(30)

        self.gh3_preview_layout.addWidget(self.length_seconds_gh3)

        self.length_mills_gh3 = QSpinBox(self.gh3_audio_widget)
        self.length_mills_gh3.setObjectName(u"length_mills_gh3")
        self.length_mills_gh3.setMaximum(999)

        self.gh3_preview_layout.addWidget(self.length_mills_gh3)


        self.verticalLayout_10.addLayout(self.gh3_preview_layout)


        self.verticalLayout_5.addWidget(self.gh3_audio_widget, 0, Qt.AlignTop)

        self.compile_tabs.addTab(self.audio_tab_gh3, "")
        self.song_data_tab_wt = QWidget()
        self.song_data_tab_wt.setObjectName(u"song_data_tab_wt")
        self.verticalLayout = QVBoxLayout(self.song_data_tab_wt)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.wt_song_data_widget = QWidget(self.song_data_tab_wt)
        self.wt_song_data_widget.setObjectName(u"wt_song_data_widget")
        self.verticalLayout_13 = QVBoxLayout(self.wt_song_data_widget)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.ghwt_midi_file_select = QToolButton(self.wt_song_data_widget)
        self.ghwt_midi_file_select.setObjectName(u"ghwt_midi_file_select")

        self.gridLayout_3.addWidget(self.ghwt_midi_file_select, 0, 2, 1, 1)

        self.ghwt_ska_files_input = QLineEdit(self.wt_song_data_widget)
        self.ghwt_ska_files_input.setObjectName(u"ghwt_ska_files_input")

        self.gridLayout_3.addWidget(self.ghwt_ska_files_input, 2, 1, 1, 1)

        self.vocal_scroll_speed_input = QDoubleSpinBox(self.wt_song_data_widget)
        self.vocal_scroll_speed_input.setObjectName(u"vocal_scroll_speed_input")
        self.vocal_scroll_speed_input.setValue(1.000000000000000)

        self.gridLayout_3.addWidget(self.vocal_scroll_speed_input, 8, 1, 1, 1)

        self.ghwt_midi_file_label = QLabel(self.wt_song_data_widget)
        self.ghwt_midi_file_label.setObjectName(u"ghwt_midi_file_label")

        self.gridLayout_3.addWidget(self.ghwt_midi_file_label, 0, 0, 1, 1)

        self.ghwt_midi_file_input = QLineEdit(self.wt_song_data_widget)
        self.ghwt_midi_file_input.setObjectName(u"ghwt_midi_file_input")

        self.gridLayout_3.addWidget(self.ghwt_midi_file_input, 0, 1, 1, 1)

        self.ghwt_ska_files_label = QLabel(self.wt_song_data_widget)
        self.ghwt_ska_files_label.setObjectName(u"ghwt_ska_files_label")

        self.gridLayout_3.addWidget(self.ghwt_ska_files_label, 2, 0, 1, 1)

        self.ghwt_perf_override_label = QLabel(self.wt_song_data_widget)
        self.ghwt_perf_override_label.setObjectName(u"ghwt_perf_override_label")

        self.gridLayout_3.addWidget(self.ghwt_perf_override_label, 1, 0, 1, 1)

        self.ghwt_drumkit_label = QLabel(self.wt_song_data_widget)
        self.ghwt_drumkit_label.setObjectName(u"ghwt_drumkit_label")

        self.gridLayout_3.addWidget(self.ghwt_drumkit_label, 6, 0, 1, 1)

        self.label_3 = QLabel(self.wt_song_data_widget)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 13, 0, 1, 1)

        self.ghwt_vocal_gender_label = QLabel(self.wt_song_data_widget)
        self.ghwt_vocal_gender_label.setObjectName(u"ghwt_vocal_gender_label")

        self.gridLayout_3.addWidget(self.ghwt_vocal_gender_label, 7, 0, 1, 1)

        self.line_10 = QFrame(self.wt_song_data_widget)
        self.line_10.setObjectName(u"line_10")
        self.line_10.setFrameShape(QFrame.HLine)
        self.line_10.setFrameShadow(QFrame.Sunken)

        self.gridLayout_3.addWidget(self.line_10, 11, 0, 1, 3)

        self.ghwt_countoff_select = QComboBox(self.wt_song_data_widget)
        self.ghwt_countoff_select.addItem(u"Hihat01")
        self.ghwt_countoff_select.addItem(u"Hihat02")
        self.ghwt_countoff_select.addItem(u"Hihat03")
        self.ghwt_countoff_select.addItem(u"Sticks_Huge")
        self.ghwt_countoff_select.addItem(u"Sticks_Normal")
        self.ghwt_countoff_select.addItem(u"Sticks_Tiny")
        self.ghwt_countoff_select.setObjectName(u"ghwt_countoff_select")

        self.gridLayout_3.addWidget(self.ghwt_countoff_select, 4, 1, 1, 1)

        self.ghwt_perf_override_input = QLineEdit(self.wt_song_data_widget)
        self.ghwt_perf_override_input.setObjectName(u"ghwt_perf_override_input")

        self.gridLayout_3.addWidget(self.ghwt_perf_override_input, 1, 1, 1, 1)

        self.skeleton_types_label = QLabel(self.wt_song_data_widget)
        self.skeleton_types_label.setObjectName(u"skeleton_types_label")

        self.gridLayout_3.addWidget(self.skeleton_types_label, 14, 0, 1, 1)

        self.ghwt_drumkit_select = QComboBox(self.wt_song_data_widget)
        self.ghwt_drumkit_select.setObjectName(u"ghwt_drumkit_select")

        self.gridLayout_3.addWidget(self.ghwt_drumkit_select, 6, 1, 1, 1)

        self.ghwt_perf_override_select = QToolButton(self.wt_song_data_widget)
        self.ghwt_perf_override_select.setObjectName(u"ghwt_perf_override_select")

        self.gridLayout_3.addWidget(self.ghwt_perf_override_select, 1, 2, 1, 1)

        self.label_2 = QLabel(self.wt_song_data_widget)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 12, 0, 1, 3, Qt.AlignHCenter)

        self.label_7 = QLabel(self.wt_song_data_widget)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_3.addWidget(self.label_7, 15, 0, 1, 1)

        self.ghwt_countoff_label = QLabel(self.wt_song_data_widget)
        self.ghwt_countoff_label.setObjectName(u"ghwt_countoff_label")

        self.gridLayout_3.addWidget(self.ghwt_countoff_label, 4, 0, 1, 1)

        self.tiers_label = QLabel(self.wt_song_data_widget)
        self.tiers_label.setObjectName(u"tiers_label")

        self.gridLayout_3.addWidget(self.tiers_label, 10, 0, 1, 1)

        self.tiers_layout = QGridLayout()
        self.tiers_layout.setObjectName(u"tiers_layout")
        self.band_tier_label = QLabel(self.wt_song_data_widget)
        self.band_tier_label.setObjectName(u"band_tier_label")

        self.tiers_layout.addWidget(self.band_tier_label, 4, 0, 1, 1)

        self.vocal_tier_label = QLabel(self.wt_song_data_widget)
        self.vocal_tier_label.setObjectName(u"vocal_tier_label")

        self.tiers_layout.addWidget(self.vocal_tier_label, 3, 0, 1, 1)

        self.drums_tier_label = QLabel(self.wt_song_data_widget)
        self.drums_tier_label.setObjectName(u"drums_tier_label")

        self.tiers_layout.addWidget(self.drums_tier_label, 1, 0, 1, 1)

        self.guitar_tier_label = QLabel(self.wt_song_data_widget)
        self.guitar_tier_label.setObjectName(u"guitar_tier_label")

        self.tiers_layout.addWidget(self.guitar_tier_label, 2, 0, 1, 1)

        self.bass_tier_label = QLabel(self.wt_song_data_widget)
        self.bass_tier_label.setObjectName(u"bass_tier_label")

        self.tiers_layout.addWidget(self.bass_tier_label, 0, 0, 1, 1)

        self.bass_tier_value = QSpinBox(self.wt_song_data_widget)
        self.bass_tier_value.setObjectName(u"bass_tier_value")
        sizePolicy4 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.bass_tier_value.sizePolicy().hasHeightForWidth())
        self.bass_tier_value.setSizePolicy(sizePolicy4)
        self.bass_tier_value.setMaximum(10)

        self.tiers_layout.addWidget(self.bass_tier_value, 0, 1, 1, 1)

        self.drums_tier_value = QSpinBox(self.wt_song_data_widget)
        self.drums_tier_value.setObjectName(u"drums_tier_value")
        sizePolicy4.setHeightForWidth(self.drums_tier_value.sizePolicy().hasHeightForWidth())
        self.drums_tier_value.setSizePolicy(sizePolicy4)
        self.drums_tier_value.setMaximum(10)

        self.tiers_layout.addWidget(self.drums_tier_value, 1, 1, 1, 1)

        self.guitar_tier_value = QSpinBox(self.wt_song_data_widget)
        self.guitar_tier_value.setObjectName(u"guitar_tier_value")
        sizePolicy4.setHeightForWidth(self.guitar_tier_value.sizePolicy().hasHeightForWidth())
        self.guitar_tier_value.setSizePolicy(sizePolicy4)
        self.guitar_tier_value.setMaximum(10)

        self.tiers_layout.addWidget(self.guitar_tier_value, 2, 1, 1, 1)

        self.vocals_tier_value = QSpinBox(self.wt_song_data_widget)
        self.vocals_tier_value.setObjectName(u"vocals_tier_value")
        sizePolicy4.setHeightForWidth(self.vocals_tier_value.sizePolicy().hasHeightForWidth())
        self.vocals_tier_value.setSizePolicy(sizePolicy4)
        self.vocals_tier_value.setMaximum(10)

        self.tiers_layout.addWidget(self.vocals_tier_value, 3, 1, 1, 1)

        self.band_tier_value = QSpinBox(self.wt_song_data_widget)
        self.band_tier_value.setObjectName(u"band_tier_value")
        sizePolicy4.setHeightForWidth(self.band_tier_value.sizePolicy().hasHeightForWidth())
        self.band_tier_value.setSizePolicy(sizePolicy4)
        self.band_tier_value.setMaximum(10)

        self.tiers_layout.addWidget(self.band_tier_value, 4, 1, 1, 1)


        self.gridLayout_3.addLayout(self.tiers_layout, 10, 1, 1, 1)

        self.ghwt_band_vol = QDoubleSpinBox(self.wt_song_data_widget)
        self.ghwt_band_vol.setObjectName(u"ghwt_band_vol")
        self.ghwt_band_vol.setMinimum(-10.000000000000000)
        self.ghwt_band_vol.setMaximum(5.000000000000000)
        self.ghwt_band_vol.setSingleStep(0.500000000000000)

        self.gridLayout_3.addWidget(self.ghwt_band_vol, 9, 1, 1, 1)

        self.ghwt_band_vol_label = QLabel(self.wt_song_data_widget)
        self.ghwt_band_vol_label.setObjectName(u"ghwt_band_vol_label")

        self.gridLayout_3.addWidget(self.ghwt_band_vol_label, 9, 0, 1, 1)

        self.ghwt_ska_files_select = QToolButton(self.wt_song_data_widget)
        self.ghwt_ska_files_select.setObjectName(u"ghwt_ska_files_select")

        self.gridLayout_3.addWidget(self.ghwt_ska_files_select, 2, 2, 1, 1)

        self.vocal_speed_label = QLabel(self.wt_song_data_widget)
        self.vocal_speed_label.setObjectName(u"vocal_speed_label")

        self.gridLayout_3.addWidget(self.vocal_speed_label, 8, 0, 1, 1)

        self.ghwt_vocal_gender_select = QComboBox(self.wt_song_data_widget)
        self.ghwt_vocal_gender_select.addItem("")
        self.ghwt_vocal_gender_select.addItem("")
        self.ghwt_vocal_gender_select.addItem("")
        self.ghwt_vocal_gender_select.setObjectName(u"ghwt_vocal_gender_select")

        self.gridLayout_3.addWidget(self.ghwt_vocal_gender_select, 7, 1, 1, 1)

        self.ghwt_song_script_label = QLabel(self.wt_song_data_widget)
        self.ghwt_song_script_label.setObjectName(u"ghwt_song_script_label")

        self.gridLayout_3.addWidget(self.ghwt_song_script_label, 3, 0, 1, 1)

        self.ghwt_song_script_input = QLineEdit(self.wt_song_data_widget)
        self.ghwt_song_script_input.setObjectName(u"ghwt_song_script_input")

        self.gridLayout_3.addWidget(self.ghwt_song_script_input, 3, 1, 1, 1)

        self.ghwt_song_script_select = QToolButton(self.wt_song_data_widget)
        self.ghwt_song_script_select.setObjectName(u"ghwt_song_script_select")

        self.gridLayout_3.addWidget(self.ghwt_song_script_select, 3, 2, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.game_icon_label = QLabel(self.wt_song_data_widget)
        self.game_icon_label.setObjectName(u"game_icon_label")

        self.horizontalLayout_10.addWidget(self.game_icon_label)

        self.game_icon_input = QLineEdit(self.wt_song_data_widget)
        self.game_icon_input.setObjectName(u"game_icon_input")

        self.horizontalLayout_10.addWidget(self.game_icon_input)

        self.game_category_label = QLabel(self.wt_song_data_widget)
        self.game_category_label.setObjectName(u"game_category_label")

        self.horizontalLayout_10.addWidget(self.game_category_label)

        self.game_category_input = QLineEdit(self.wt_song_data_widget)
        self.game_category_input.setObjectName(u"game_category_input")

        self.horizontalLayout_10.addWidget(self.game_category_input)

        self.band_label = QLabel(self.wt_song_data_widget)
        self.band_label.setObjectName(u"band_label")

        self.horizontalLayout_10.addWidget(self.band_label)

        self.band_input = QLineEdit(self.wt_song_data_widget)
        self.band_input.setObjectName(u"band_input")

        self.horizontalLayout_10.addWidget(self.band_input)


        self.gridLayout_3.addLayout(self.horizontalLayout_10, 13, 1, 1, 2)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.skeleton_type_g_label = QLabel(self.wt_song_data_widget)
        self.skeleton_type_g_label.setObjectName(u"skeleton_type_g_label")

        self.horizontalLayout_8.addWidget(self.skeleton_type_g_label)

        self.skeleton_type_g_select = QComboBox(self.wt_song_data_widget)
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.addItem("")
        self.skeleton_type_g_select.setObjectName(u"skeleton_type_g_select")

        self.horizontalLayout_8.addWidget(self.skeleton_type_g_select)

        self.skeleton_type_b_label = QLabel(self.wt_song_data_widget)
        self.skeleton_type_b_label.setObjectName(u"skeleton_type_b_label")

        self.horizontalLayout_8.addWidget(self.skeleton_type_b_label)

        self.skeleton_type_b_select = QComboBox(self.wt_song_data_widget)
        self.skeleton_type_b_select.setObjectName(u"skeleton_type_b_select")

        self.horizontalLayout_8.addWidget(self.skeleton_type_b_select)

        self.skeleton_type_d_label = QLabel(self.wt_song_data_widget)
        self.skeleton_type_d_label.setObjectName(u"skeleton_type_d_label")

        self.horizontalLayout_8.addWidget(self.skeleton_type_d_label)

        self.skeleton_type_d_select = QComboBox(self.wt_song_data_widget)
        self.skeleton_type_d_select.setObjectName(u"skeleton_type_d_select")

        self.horizontalLayout_8.addWidget(self.skeleton_type_d_select)

        self.skeleton_type_v_label = QLabel(self.wt_song_data_widget)
        self.skeleton_type_v_label.setObjectName(u"skeleton_type_v_label")

        self.horizontalLayout_8.addWidget(self.skeleton_type_v_label)

        self.skeleton_type_v_select = QComboBox(self.wt_song_data_widget)
        self.skeleton_type_v_select.setObjectName(u"skeleton_type_v_select")

        self.horizontalLayout_8.addWidget(self.skeleton_type_v_select)


        self.gridLayout_3.addLayout(self.horizontalLayout_8, 14, 1, 1, 2)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.guitar_mic_check = QCheckBox(self.wt_song_data_widget)
        self.guitar_mic_check.setObjectName(u"guitar_mic_check")

        self.horizontalLayout_9.addWidget(self.guitar_mic_check)

        self.bass_mic_check = QCheckBox(self.wt_song_data_widget)
        self.bass_mic_check.setObjectName(u"bass_mic_check")

        self.horizontalLayout_9.addWidget(self.bass_mic_check)

        self.use_new_clips_check = QCheckBox(self.wt_song_data_widget)
        self.use_new_clips_check.setObjectName(u"use_new_clips_check")

        self.horizontalLayout_9.addWidget(self.use_new_clips_check)


        self.gridLayout_3.addLayout(self.horizontalLayout_9, 15, 1, 1, 2)


        self.verticalLayout_13.addLayout(self.gridLayout_3)


        self.verticalLayout.addWidget(self.wt_song_data_widget)

        self.compile_tabs.addTab(self.song_data_tab_wt, "")
        self.song_data_tab_gh3 = QWidget()
        self.song_data_tab_gh3.setObjectName(u"song_data_tab_gh3")
        self.verticalLayout_12 = QVBoxLayout(self.song_data_tab_gh3)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.gh3_song_data_widget = QWidget(self.song_data_tab_gh3)
        self.gh3_song_data_widget.setObjectName(u"gh3_song_data_widget")
        self.verticalLayout_7 = QVBoxLayout(self.gh3_song_data_widget)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.gh3_gtr_vol_label = QLabel(self.gh3_song_data_widget)
        self.gh3_gtr_vol_label.setObjectName(u"gh3_gtr_vol_label")

        self.horizontalLayout_7.addWidget(self.gh3_gtr_vol_label)

        self.gh3_gtr_vol = QDoubleSpinBox(self.gh3_song_data_widget)
        self.gh3_gtr_vol.setObjectName(u"gh3_gtr_vol")
        self.gh3_gtr_vol.setMinimum(-5.000000000000000)
        self.gh3_gtr_vol.setMaximum(5.000000000000000)
        self.gh3_gtr_vol.setSingleStep(0.050000000000000)
        self.gh3_gtr_vol.setValue(0.000000000000000)

        self.horizontalLayout_7.addWidget(self.gh3_gtr_vol)

        self.gh3_band_vol_label = QLabel(self.gh3_song_data_widget)
        self.gh3_band_vol_label.setObjectName(u"gh3_band_vol_label")

        self.horizontalLayout_7.addWidget(self.gh3_band_vol_label)

        self.gh3_band_vol = QDoubleSpinBox(self.gh3_song_data_widget)
        self.gh3_band_vol.setObjectName(u"gh3_band_vol")
        self.gh3_band_vol.setMinimum(-5.000000000000000)
        self.gh3_band_vol.setMaximum(5.000000000000000)
        self.gh3_band_vol.setSingleStep(0.050000000000000)
        self.gh3_band_vol.setValue(0.000000000000000)

        self.horizontalLayout_7.addWidget(self.gh3_band_vol)


        self.gridLayout_5.addLayout(self.horizontalLayout_7, 7, 1, 1, 1)

        self.gh3_perf_override_label = QLabel(self.gh3_song_data_widget)
        self.gh3_perf_override_label.setObjectName(u"gh3_perf_override_label")

        self.gridLayout_5.addWidget(self.gh3_perf_override_label, 1, 0, 1, 1)

        self.gh3_countoff_label = QLabel(self.gh3_song_data_widget)
        self.gh3_countoff_label.setObjectName(u"gh3_countoff_label")

        self.gridLayout_5.addWidget(self.gh3_countoff_label, 2, 0, 1, 1)

        self.gh3_countoff_select = QComboBox(self.gh3_song_data_widget)
        self.gh3_countoff_select.addItem(u"Hihat01")
        self.gh3_countoff_select.addItem(u"Hihat02")
        self.gh3_countoff_select.addItem(u"Hihat03")
        self.gh3_countoff_select.addItem(u"Sticks_Huge")
        self.gh3_countoff_select.addItem(u"Sticks_Normal")
        self.gh3_countoff_select.addItem(u"Sticks_Tiny")
        self.gh3_countoff_select.setObjectName(u"gh3_countoff_select")

        self.gridLayout_5.addWidget(self.gh3_countoff_select, 2, 1, 1, 1)

        self.gh3_vocal_gender_select = QComboBox(self.gh3_song_data_widget)
        self.gh3_vocal_gender_select.addItem("")
        self.gh3_vocal_gender_select.addItem("")
        self.gh3_vocal_gender_select.addItem("")
        self.gh3_vocal_gender_select.addItem("")
        self.gh3_vocal_gender_select.setObjectName(u"gh3_vocal_gender_select")

        self.gridLayout_5.addWidget(self.gh3_vocal_gender_select, 4, 1, 1, 1)

        self.gh3_bassist_select_label = QLabel(self.gh3_song_data_widget)
        self.gh3_bassist_select_label.setObjectName(u"gh3_bassist_select_label")

        self.gridLayout_5.addWidget(self.gh3_bassist_select_label, 5, 0, 1, 1)

        self.gh3_midi_file_input = QLineEdit(self.gh3_song_data_widget)
        self.gh3_midi_file_input.setObjectName(u"gh3_midi_file_input")

        self.gridLayout_5.addWidget(self.gh3_midi_file_input, 0, 1, 1, 1)

        self.gh3_midi_file_label = QLabel(self.gh3_song_data_widget)
        self.gh3_midi_file_label.setObjectName(u"gh3_midi_file_label")

        self.gridLayout_5.addWidget(self.gh3_midi_file_label, 0, 0, 1, 1)

        self.gh3_perf_override_select = QToolButton(self.gh3_song_data_widget)
        self.gh3_perf_override_select.setObjectName(u"gh3_perf_override_select")

        self.gridLayout_5.addWidget(self.gh3_perf_override_select, 1, 2, 1, 1)

        self.gh3_bassist_select = QComboBox(self.gh3_song_data_widget)
        self.gh3_bassist_select.setObjectName(u"gh3_bassist_select")

        self.gridLayout_5.addWidget(self.gh3_bassist_select, 5, 1, 1, 1)

        self.gh3_midi_file_select = QToolButton(self.gh3_song_data_widget)
        self.gh3_midi_file_select.setObjectName(u"gh3_midi_file_select")

        self.gridLayout_5.addWidget(self.gh3_midi_file_select, 0, 2, 1, 1)

        self.gh3_perf_override_input = QLineEdit(self.gh3_song_data_widget)
        self.gh3_perf_override_input.setObjectName(u"gh3_perf_override_input")

        self.gridLayout_5.addWidget(self.gh3_perf_override_input, 1, 1, 1, 1)

        self.gh3_volume_label = QLabel(self.gh3_song_data_widget)
        self.gh3_volume_label.setObjectName(u"gh3_volume_label")

        self.gridLayout_5.addWidget(self.gh3_volume_label, 7, 0, 1, 1)

        self.gh3_vocal_gender_label = QLabel(self.gh3_song_data_widget)
        self.gh3_vocal_gender_label.setObjectName(u"gh3_vocal_gender_label")

        self.gridLayout_5.addWidget(self.gh3_vocal_gender_label, 4, 0, 1, 1)

        self.line = QFrame(self.gh3_song_data_widget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.gridLayout_5.addWidget(self.line, 6, 0, 1, 3)


        self.verticalLayout_7.addLayout(self.gridLayout_5)


        self.verticalLayout_12.addWidget(self.gh3_song_data_widget, 0, Qt.AlignTop)

        self.compile_tabs.addTab(self.song_data_tab_gh3, "")
        self.compile_tab = QWidget()
        self.compile_tab.setObjectName(u"compile_tab")
        self.verticalLayout_14 = QVBoxLayout(self.compile_tab)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.compile_widget = QWidget(self.compile_tab)
        self.compile_widget.setObjectName(u"compile_widget")
        self.verticalLayout_16 = QVBoxLayout(self.compile_widget)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.compile_settings = QGroupBox(self.compile_widget)
        self.compile_settings.setObjectName(u"compile_settings")
        self.verticalLayout_15 = QVBoxLayout(self.compile_settings)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.beat_16th_low_input = QSpinBox(self.compile_settings)
        self.beat_16th_low_input.setObjectName(u"beat_16th_low_input")
        self.beat_16th_low_input.setEnabled(False)
        self.beat_16th_low_input.setMinimum(1)
        self.beat_16th_low_input.setMaximum(300)

        self.gridLayout_6.addWidget(self.beat_16th_low_input, 3, 3, 1, 1)

        self.beat_8th_high_label = QLabel(self.compile_settings)
        self.beat_8th_high_label.setObjectName(u"beat_8th_high_label")

        self.gridLayout_6.addWidget(self.beat_8th_high_label, 2, 4, 1, 1)

        self.beat_8th_low_input = QSpinBox(self.compile_settings)
        self.beat_8th_low_input.setObjectName(u"beat_8th_low_input")
        self.beat_8th_low_input.setEnabled(False)
        self.beat_8th_low_input.setMinimum(1)
        self.beat_8th_low_input.setMaximum(300)

        self.gridLayout_6.addWidget(self.beat_8th_low_input, 2, 3, 1, 1)

        self.beat_16th_low_label = QLabel(self.compile_settings)
        self.beat_16th_low_label.setObjectName(u"beat_16th_low_label")

        self.gridLayout_6.addWidget(self.beat_16th_low_label, 3, 2, 1, 1)

        self.beat_16th_high_label = QLabel(self.compile_settings)
        self.beat_16th_high_label.setObjectName(u"beat_16th_high_label")

        self.gridLayout_6.addWidget(self.beat_16th_high_label, 3, 4, 1, 1)

        self.beat_8th_label = QLabel(self.compile_settings)
        self.beat_8th_label.setObjectName(u"beat_8th_label")

        self.gridLayout_6.addWidget(self.beat_8th_label, 2, 1, 1, 1, Qt.AlignRight)

        self.beat_16th_label = QLabel(self.compile_settings)
        self.beat_16th_label.setObjectName(u"beat_16th_label")

        self.gridLayout_6.addWidget(self.beat_16th_label, 3, 1, 1, 1, Qt.AlignRight)

        self.horizontalLayout_11 = QHBoxLayout()
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.hmx_hopo_label = QLabel(self.compile_settings)
        self.hmx_hopo_label.setObjectName(u"hmx_hopo_label")

        self.horizontalLayout_11.addWidget(self.hmx_hopo_label)

        self.hmx_hopo_value = QSpinBox(self.compile_settings)
        self.hmx_hopo_value.setObjectName(u"hmx_hopo_value")
        self.hmx_hopo_value.setMaximum(1920)
        self.hmx_hopo_value.setSingleStep(10)
        self.hmx_hopo_value.setValue(170)

        self.horizontalLayout_11.addWidget(self.hmx_hopo_value)

        self.ns_hopo_label = QLabel(self.compile_settings)
        self.ns_hopo_label.setObjectName(u"ns_hopo_label")

        self.horizontalLayout_11.addWidget(self.ns_hopo_label)

        self.ns_hopo_value = QLineEdit(self.compile_settings)
        self.ns_hopo_value.setObjectName(u"ns_hopo_value")
        self.ns_hopo_value.setEnabled(True)
        self.ns_hopo_value.setReadOnly(True)

        self.horizontalLayout_11.addWidget(self.ns_hopo_value)


        self.gridLayout_6.addLayout(self.horizontalLayout_11, 0, 1, 1, 5)

        self.beatlines_check = QCheckBox(self.compile_settings)
        self.beatlines_check.setObjectName(u"beatlines_check")

        self.gridLayout_6.addWidget(self.beatlines_check, 2, 0, 2, 1)

        self.hopo_label = QLabel(self.compile_settings)
        self.hopo_label.setObjectName(u"hopo_label")

        self.gridLayout_6.addWidget(self.hopo_label, 0, 0, 1, 1)

        self.beat_8th_low_label = QLabel(self.compile_settings)
        self.beat_8th_low_label.setObjectName(u"beat_8th_low_label")

        self.gridLayout_6.addWidget(self.beat_8th_low_label, 2, 2, 1, 1)

        self.beat_16th_high_input = QSpinBox(self.compile_settings)
        self.beat_16th_high_input.setObjectName(u"beat_16th_high_input")
        self.beat_16th_high_input.setEnabled(False)
        self.beat_16th_high_input.setMinimum(1)
        self.beat_16th_high_input.setMaximum(300)
        self.beat_16th_high_input.setValue(120)

        self.gridLayout_6.addWidget(self.beat_16th_high_input, 3, 5, 1, 1)

        self.beat_8th_high_input = QSpinBox(self.compile_settings)
        self.beat_8th_high_input.setObjectName(u"beat_8th_high_input")
        self.beat_8th_high_input.setEnabled(False)
        self.beat_8th_high_input.setMinimum(1)
        self.beat_8th_high_input.setMaximum(300)
        self.beat_8th_high_input.setValue(180)

        self.gridLayout_6.addWidget(self.beat_8th_high_input, 2, 5, 1, 1)

        self.hopo_mode_label = QLabel(self.compile_settings)
        self.hopo_mode_label.setObjectName(u"hopo_mode_label")

        self.gridLayout_6.addWidget(self.hopo_mode_label, 1, 0, 1, 1)

        self.hopo_mode_select = QComboBox(self.compile_settings)
        self.hopo_mode_select.addItem("")
        self.hopo_mode_select.addItem("")
        self.hopo_mode_select.addItem("")
        self.hopo_mode_select.addItem("")
        self.hopo_mode_select.setObjectName(u"hopo_mode_select")

        self.gridLayout_6.addWidget(self.hopo_mode_select, 1, 1, 1, 2)


        self.verticalLayout_15.addLayout(self.gridLayout_6)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.platform_label = QLabel(self.compile_settings)
        self.platform_label.setObjectName(u"platform_label")

        self.horizontalLayout_5.addWidget(self.platform_label)

        self.platform_pc = QRadioButton(self.compile_settings)
        self.platform_button_group = QButtonGroup(Form)
        self.platform_button_group.setObjectName(u"platform_button_group")
        self.platform_button_group.addButton(self.platform_pc)
        self.platform_pc.setObjectName(u"platform_pc")
        self.platform_pc.setChecked(True)

        self.horizontalLayout_5.addWidget(self.platform_pc)

        self.platform_360 = QRadioButton(self.compile_settings)
        self.platform_button_group.addButton(self.platform_360)
        self.platform_360.setObjectName(u"platform_360")
        self.platform_360.setEnabled(False)

        self.horizontalLayout_5.addWidget(self.platform_360)


        self.verticalLayout_15.addLayout(self.horizontalLayout_5)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.compile_input_label = QLabel(self.compile_settings)
        self.compile_input_label.setObjectName(u"compile_input_label")

        self.horizontalLayout_3.addWidget(self.compile_input_label)

        self.compile_input = QLineEdit(self.compile_settings)
        self.compile_input.setObjectName(u"compile_input")

        self.horizontalLayout_3.addWidget(self.compile_input)

        self.compile_select = QToolButton(self.compile_settings)
        self.compile_select.setObjectName(u"compile_select")

        self.horizontalLayout_3.addWidget(self.compile_select)


        self.verticalLayout_15.addLayout(self.horizontalLayout_3)

        self.verticalLayout_17 = QVBoxLayout()
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.project_file_label = QLabel(self.compile_settings)
        self.project_file_label.setObjectName(u"project_file_label")

        self.horizontalLayout_4.addWidget(self.project_file_label)

        self.project_file_path = QLineEdit(self.compile_settings)
        self.project_file_path.setObjectName(u"project_file_path")

        self.horizontalLayout_4.addWidget(self.project_file_path)


        self.verticalLayout_17.addLayout(self.horizontalLayout_4)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.project_file_open = QPushButton(self.compile_settings)
        self.project_file_open.setObjectName(u"project_file_open")

        self.horizontalLayout_6.addWidget(self.project_file_open)

        self.project_file_save = QPushButton(self.compile_settings)
        self.project_file_save.setObjectName(u"project_file_save")

        self.horizontalLayout_6.addWidget(self.project_file_save)

        self.project_file_saveas = QPushButton(self.compile_settings)
        self.project_file_saveas.setObjectName(u"project_file_saveas")

        self.horizontalLayout_6.addWidget(self.project_file_saveas)


        self.verticalLayout_17.addLayout(self.horizontalLayout_6)


        self.verticalLayout_15.addLayout(self.verticalLayout_17)

        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.compile_button = QPushButton(self.compile_settings)
        self.compile_button.setObjectName(u"compile_button")

        self.horizontalLayout_12.addWidget(self.compile_button)

        self.force_ffmpeg_check = QCheckBox(self.compile_settings)
        self.force_ffmpeg_check.setObjectName(u"force_ffmpeg_check")

        self.horizontalLayout_12.addWidget(self.force_ffmpeg_check)

        self.compile_pak_button = QPushButton(self.compile_settings)
        self.compile_pak_button.setObjectName(u"compile_pak_button")

        self.horizontalLayout_12.addWidget(self.compile_pak_button)


        self.verticalLayout_15.addLayout(self.horizontalLayout_12)


        self.verticalLayout_16.addWidget(self.compile_settings)


        self.verticalLayout_14.addWidget(self.compile_widget)

        self.compile_tabs.addTab(self.compile_tab, "")

        self.verticalLayout_4.addWidget(self.compile_tabs)


        self.verticalLayout_11.addLayout(self.verticalLayout_4)


        self.retranslateUi(Form)
        self.cover_checkbox.toggled.connect(self.cover_year_input.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_guitar_input_gh3.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_guitar_select_gh3.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_rhythm_input_gh3.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_rhythm_select_gh3.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_backing_input_gh3.setEnabled)
        self.coop_audio_check.toggled.connect(self.coop_backing_select_gh3.setEnabled)
        self.cover_checkbox.toggled.connect(self.cover_artist_input.setEnabled)
        self.beatlines_check.toggled.connect(self.beat_8th_low_input.setEnabled)
        self.beatlines_check.toggled.connect(self.beat_8th_high_input.setEnabled)
        self.beatlines_check.toggled.connect(self.beat_16th_low_input.setEnabled)
        self.beatlines_check.toggled.connect(self.beat_16th_high_input.setEnabled)
        self.p2_rhythm_check.toggled.connect(self.coop_audio_check.setEnabled)

        self.compile_tabs.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Compile Song Package", None))
#if QT_CONFIG(tooltip)
        Form.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.game_select.setTitle(QCoreApplication.translate("Form", u"Game", None))
        self.gha.setText(QCoreApplication.translate("Form", u"GHA", None))
        self.artist_text_label.setText(QCoreApplication.translate("Form", u"Artist Text:", None))
        self.cover_year_label.setText(QCoreApplication.translate("Form", u"Year:", None))
        self.genre_label.setText(QCoreApplication.translate("Form", u"Genre:", None))
        self.cover_checkbox.setText(QCoreApplication.translate("Form", u"Cover", None))
        self.year_label.setText(QCoreApplication.translate("Form", u"Year:", None))
        self.author_label.setText(QCoreApplication.translate("Form", u"Chart Author", None))
        self.title_label.setText(QCoreApplication.translate("Form", u"Title:", None))
        self.checksum_label.setText(QCoreApplication.translate("Form", u"Checksum", None))
        self.artist_text_select.setItemText(0, QCoreApplication.translate("Form", u"By", None))
        self.artist_text_select.setItemText(1, QCoreApplication.translate("Form", u"As Made Famous By", None))
        self.artist_text_select.setItemText(2, QCoreApplication.translate("Form", u"Other", None))

        self.artist_label.setText(QCoreApplication.translate("Form", u"Artist:", None))
        self.cover_artist_label.setText(QCoreApplication.translate("Form", u"Cover Artist:", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.metadata_tab), QCoreApplication.translate("Form", u"Metadata", None))
        self.backing_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.cymbals_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.bass_label.setText(QCoreApplication.translate("Form", u"Bass", None))
        self.snare_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.kick_label.setText(QCoreApplication.translate("Form", u"Kick", None))
        self.crowd_label.setText(QCoreApplication.translate("Form", u"Crowd", None))
        self.snare_label.setText(QCoreApplication.translate("Form", u"Snare", None))
        self.bass_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.guitar_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.vocals_label.setText(QCoreApplication.translate("Form", u"Vocals", None))
        self.toms_label.setText(QCoreApplication.translate("Form", u"Toms", None))
        self.toms_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.guitar_label.setText(QCoreApplication.translate("Form", u"Guitar", None))
        self.crowd_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.cymbals_label.setText(QCoreApplication.translate("Form", u"Cymbals", None))
        self.label.setText(QCoreApplication.translate("Form", u"Audio File Path", None))
        self.track_label.setText(QCoreApplication.translate("Form", u"Track", None))
        self.vocals_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.kick_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.backing_label.setText(QCoreApplication.translate("Form", u"Backing", None))
        self.encrypt_audio.setText(QCoreApplication.translate("Form", u"Encrypt Audio", None))
        self.preview_label.setText(QCoreApplication.translate("Form", u"Preview Start:", None))
        self.length_label.setText(QCoreApplication.translate("Form", u"Length:", None))
        self.ghwt_set_end.setText(QCoreApplication.translate("Form", u"Set End Time", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.audio_tab_wt), QCoreApplication.translate("Form", u"Audio (WT)", None))
        self.guitar_label_gh3.setText(QCoreApplication.translate("Form", u"Guitar", None))
        self.track_label_2.setText(QCoreApplication.translate("Form", u"Track", None))
        self.guitar_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.rhythm_label_gh3.setText(QCoreApplication.translate("Form", u"Bass", None))
        self.backing_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.coop_backing_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.gh3_file_path_label.setText(QCoreApplication.translate("Form", u"Audio File Path", None))
        self.backing_label_gh3.setText(QCoreApplication.translate("Form", u"Backing", None))
        self.crowd_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.rhythm_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.coop_guitar_label_gh3.setText(QCoreApplication.translate("Form", u"Guitar", None))
        self.coop_rhythm_label_gh3.setText(QCoreApplication.translate("Form", u"Rhythm", None))
        self.crowd_label_gh3.setText(QCoreApplication.translate("Form", u"Crowd", None))
        self.coop_rhythm_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.coop_guitar_select_gh3.setText(QCoreApplication.translate("Form", u"...", None))
        self.coop_backing_label_gh3.setText(QCoreApplication.translate("Form", u"Backing", None))
        self.p2_rhythm_check.setText(QCoreApplication.translate("Form", u"P2 is Rhythm", None))
        self.coop_audio_check.setText(QCoreApplication.translate("Form", u"Separate Co-op Audio", None))
        self.preview_label_2.setText(QCoreApplication.translate("Form", u"Song Preview:", None))
        self.length_label_2.setText(QCoreApplication.translate("Form", u"Length:", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.audio_tab_gh3), QCoreApplication.translate("Form", u"Audio (GH3)", None))
        self.ghwt_midi_file_select.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.ghwt_ska_files_input.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>A folder containing all SKA files used. Gets ignored if it's blank or doesn't exist</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.ghwt_midi_file_label.setText(QCoreApplication.translate("Form", u"MIDI File:", None))
        self.ghwt_ska_files_label.setText(QCoreApplication.translate("Form", u"SKA Files:", None))
        self.ghwt_perf_override_label.setText(QCoreApplication.translate("Form", u"Perf Override:", None))
        self.ghwt_drumkit_label.setText(QCoreApplication.translate("Form", u"Drum Kit:", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"In-game Settings", None))
        self.ghwt_vocal_gender_label.setText(QCoreApplication.translate("Form", u"Vocal Gender:", None))

#if QT_CONFIG(tooltip)
        self.ghwt_perf_override_input.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Select a file with a performance array to override the generated performance array.</p><p>Can be a text file compatible with the toolkit, or an already compiled qb file.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.skeleton_types_label.setText(QCoreApplication.translate("Form", u"Skeleton Types", None))
        self.ghwt_perf_override_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"World Tour Definitive Edition Settings", None))
        self.label_7.setText(QCoreApplication.translate("Form", u"Other", None))
        self.ghwt_countoff_label.setText(QCoreApplication.translate("Form", u"Count Off:", None))
        self.tiers_label.setText(QCoreApplication.translate("Form", u"Tiers", None))
        self.band_tier_label.setText(QCoreApplication.translate("Form", u"Band", None))
        self.vocal_tier_label.setText(QCoreApplication.translate("Form", u"Vocals", None))
        self.drums_tier_label.setText(QCoreApplication.translate("Form", u"Drums", None))
        self.guitar_tier_label.setText(QCoreApplication.translate("Form", u"Guitar", None))
        self.bass_tier_label.setText(QCoreApplication.translate("Form", u"Bass", None))
        self.ghwt_band_vol_label.setText(QCoreApplication.translate("Form", u"Overall Volume:", None))
        self.ghwt_ska_files_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.vocal_speed_label.setText(QCoreApplication.translate("Form", u"Vocal Scroll Speed:", None))
        self.ghwt_vocal_gender_select.setItemText(0, QCoreApplication.translate("Form", u"Male", None))
        self.ghwt_vocal_gender_select.setItemText(1, QCoreApplication.translate("Form", u"Female", None))
        self.ghwt_vocal_gender_select.setItemText(2, QCoreApplication.translate("Form", u"None", None))

        self.ghwt_song_script_label.setText(QCoreApplication.translate("Form", u"Song Script:", None))
        self.ghwt_song_script_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.game_icon_label.setText(QCoreApplication.translate("Form", u"Game Icon", None))
        self.game_category_label.setText(QCoreApplication.translate("Form", u"Game Category", None))
        self.band_label.setText(QCoreApplication.translate("Form", u"Band", None))
        self.skeleton_type_g_label.setText(QCoreApplication.translate("Form", u"G", None))
        self.skeleton_type_g_select.setItemText(0, QCoreApplication.translate("Form", u"Default", None))
        self.skeleton_type_g_select.setItemText(1, QCoreApplication.translate("Form", u"Alex", None))
        self.skeleton_type_g_select.setItemText(2, QCoreApplication.translate("Form", u"Angled", None))
        self.skeleton_type_g_select.setItemText(3, QCoreApplication.translate("Form", u"GH3Singer", None))
        self.skeleton_type_g_select.setItemText(4, QCoreApplication.translate("Form", u"GH5Drums", None))
        self.skeleton_type_g_select.setItemText(5, QCoreApplication.translate("Form", u"Lars", None))
        self.skeleton_type_g_select.setItemText(6, QCoreApplication.translate("Form", u"Lemmy", None))

        self.skeleton_type_b_label.setText(QCoreApplication.translate("Form", u"B", None))
        self.skeleton_type_d_label.setText(QCoreApplication.translate("Form", u"D", None))
        self.skeleton_type_v_label.setText(QCoreApplication.translate("Form", u"V", None))
        self.guitar_mic_check.setText(QCoreApplication.translate("Form", u"Guitar Mic", None))
        self.bass_mic_check.setText(QCoreApplication.translate("Form", u"Bass Mic", None))
        self.use_new_clips_check.setText(QCoreApplication.translate("Form", u"Use New Clips", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.song_data_tab_wt), QCoreApplication.translate("Form", u"Song Data (WT)", None))
        self.gh3_gtr_vol_label.setText(QCoreApplication.translate("Form", u"Guitar:", None))
        self.gh3_band_vol_label.setText(QCoreApplication.translate("Form", u"Band:", None))
        self.gh3_perf_override_label.setText(QCoreApplication.translate("Form", u"Perf Override", None))
        self.gh3_countoff_label.setText(QCoreApplication.translate("Form", u"Count Off:", None))

        self.gh3_vocal_gender_select.setItemText(0, QCoreApplication.translate("Form", u"Male", None))
        self.gh3_vocal_gender_select.setItemText(1, QCoreApplication.translate("Form", u"Female", None))
        self.gh3_vocal_gender_select.setItemText(2, QCoreApplication.translate("Form", u"Bret Michaels", None))
        self.gh3_vocal_gender_select.setItemText(3, QCoreApplication.translate("Form", u"None", None))

        self.gh3_bassist_select_label.setText(QCoreApplication.translate("Form", u"Bassist:", None))
        self.gh3_midi_file_label.setText(QCoreApplication.translate("Form", u"MIDI File", None))
        self.gh3_perf_override_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.gh3_midi_file_select.setText(QCoreApplication.translate("Form", u"...", None))
#if QT_CONFIG(tooltip)
        self.gh3_perf_override_input.setToolTip(QCoreApplication.translate("Form", u"Select a qb file with a performance array to override the generated performance array.", None))
#endif // QT_CONFIG(tooltip)
        self.gh3_volume_label.setText(QCoreApplication.translate("Form", u"Volume:", None))
        self.gh3_vocal_gender_label.setText(QCoreApplication.translate("Form", u"Vocal Gender:", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.song_data_tab_gh3), QCoreApplication.translate("Form", u"Song Data (GH3)", None))
        self.compile_settings.setTitle(QCoreApplication.translate("Form", u"Compile Settings", None))
        self.beat_8th_high_label.setText(QCoreApplication.translate("Form", u"High:", None))
        self.beat_16th_low_label.setText(QCoreApplication.translate("Form", u"Low:", None))
        self.beat_16th_high_label.setText(QCoreApplication.translate("Form", u"High:", None))
        self.beat_8th_label.setText(QCoreApplication.translate("Form", u"8th Notes", None))
        self.beat_16th_label.setText(QCoreApplication.translate("Form", u"16th Notes", None))
        self.hmx_hopo_label.setText(QCoreApplication.translate("Form", u"HMX Value", None))
        self.ns_hopo_label.setText(QCoreApplication.translate("Form", u"NS Value", None))
        self.beatlines_check.setText(QCoreApplication.translate("Form", u"Beat Lines BPM:", None))
        self.hopo_label.setText(QCoreApplication.translate("Form", u"HOPO Threshold:", None))
        self.beat_8th_low_label.setText(QCoreApplication.translate("Form", u"Low:", None))
        self.hopo_mode_label.setText(QCoreApplication.translate("Form", u"HOPO Mode", None))
        self.hopo_mode_select.setItemText(0, QCoreApplication.translate("Form", u"Rock Band", None))
        self.hopo_mode_select.setItemText(1, QCoreApplication.translate("Form", u"HMX/NS Hybrid", None))
        self.hopo_mode_select.setItemText(2, QCoreApplication.translate("Form", u"Guitar Hero 3", None))
        self.hopo_mode_select.setItemText(3, QCoreApplication.translate("Form", u"Guitar Hero World Tour+", None))

#if QT_CONFIG(tooltip)
        self.hopo_mode_select.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>The mode to use for Hammer Ons and Pull Offs. Each mode changes the logic of compilation slightly. Rock Band mode should be the default for most MIDIs you find or make, but if you are converting a song, it may be useful to change this setting.</p><p>Rock Band - This mode will calculate HOPOs based on the distance between each note, and then apply forcings, either on or off. If a chord and a single note follows containing the lowest note of the chord and it's within the HOPO threshold, this will NOT be a HOPO unless forced.</p><p>HMX/NS Hybrid - This mode will calculate HOPOs based on the distance between each note, and then apply forcings, either on or off. If a chord and a single note follows containing the lowest note of the chord and it's within the HOPO threshold, this will be a HOPO unless forced off (this mode is not based on any game's logic, it's a combo of RB and GH3).</p><p>Guitar Hero 3 - This mode will calculate HOPOs based on the distance between each note. If a &quot;force o"
                        "n&quot; note exists on a note in the MIDI, it swaps the HOPO status. If a chord and a single note follows containing the lowest note of the chord, this will be a HOPO unless swapped.</p><p>Guitar Hero World Tour+ - This mode will NOT calculate HOPOs based on the distance between each note. Only notes that are forced will become HOPOs.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.platform_label.setText(QCoreApplication.translate("Form", u"Platform:", None))
        self.platform_pc.setText(QCoreApplication.translate("Form", u"PC", None))
        self.platform_360.setText(QCoreApplication.translate("Form", u"Xbox 360", None))
        self.compile_input_label.setText(QCoreApplication.translate("Form", u"Compile Folder:", None))
        self.compile_select.setText(QCoreApplication.translate("Form", u"...", None))
        self.project_file_label.setText(QCoreApplication.translate("Form", u"Project File:", None))
        self.project_file_open.setText(QCoreApplication.translate("Form", u"Open", None))
        self.project_file_save.setText(QCoreApplication.translate("Form", u"Save", None))
        self.project_file_saveas.setText(QCoreApplication.translate("Form", u"Save As", None))
        self.compile_button.setText(QCoreApplication.translate("Form", u"Compile Full Song", None))
#if QT_CONFIG(tooltip)
        self.force_ffmpeg_check.setToolTip(QCoreApplication.translate("Form", u"<html><head/><body><p>Force the use of FFmpeg (default is SoX). Only needed if both SoX and FFmpeg are installed and you want to use FFmpeg over SoX.</p><p><br/></p><p>FFmpeg is faster, but is also implemented in this program a bit hackier than SoX. SoX is recommended for a cleaner compile.</p><p><br/></p><p>If this is checked and FFmpeg is not installed on your system, the compilation will fail.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.force_ffmpeg_check.setText(QCoreApplication.translate("Form", u"Force FFmpeg", None))
        self.compile_pak_button.setText(QCoreApplication.translate("Form", u"Compile PAK Only", None))
        self.compile_tabs.setTabText(self.compile_tabs.indexOf(self.compile_tab), QCoreApplication.translate("Form", u"Compile", None))
    # retranslateUi

