"""
This file contains the initialization of the GUI components made in QT Designer.
Each class will belong to one file and contain all the logic for the GUI.
Some logic is done with the designer (such as enabling/disabling certain widgets)
"""

from PySide6.QtWidgets import QWidget, QFileDialog, QRadioButton, QDoubleSpinBox, QCheckBox, QLineEdit, QLabel, \
    QComboBox, QSpinBox, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QMessageBox, QInputDialog
from project_files.compile_package import Ui_Form as compile_pack
from functools import partial
import json
import os
import sys
import configparser
import string
import traceback

curr_dir = os.path.dirname(__file__)
root_dir = os.path.dirname(curr_dir)

if os.path.exists(f"{curr_dir}\\create_audio"):
    audio_folder = f"{curr_dir}\\create_audio"
else:
    audio_folder = f"{root_dir}\\create_audio"
sys.path.append(audio_folder)
import audio_functions as af

midqb_folder = f"{root_dir}\\midqb_gen"
sys.path.append(midqb_folder)
import MidQbGen as mid_gen


class main_window(QWidget):
    def __init__(self):
        super().__init__()


class compile_package(QWidget, compile_pack):
    def __init__(self, ghproj=""):
        super().__init__()
        self.setupUi(self)
        self.artist_text_select.currentTextChanged.connect(self.artist_text_change)
        self.game_select_group.buttonClicked.connect(self.set_game_fields)

        self.wt_audio_fields()
        self.wt_song_data_fields()
        self.gh3_audio_fields()
        self.gh3_song_data_fields()
        self.compile_fields()

        self.first_boot()

        if ghproj:
            self.load_project_file(ghproj)

    def artist_text_change(self):
        if self.artist_text_select.currentText() == 'Other':
            self.artist_text_other.setDisabled(False)
        else:
            self.artist_text_other.setDisabled(True)

    def compile_song_package(self):
        self.project_save_path()
        if self.project_file_path.text() == '' or not os.path.exists(self.project_file_path.text()):
            print("There is no save file path!")
            return
        game = self.game_select_group.checkedButton().objectName()
        if game == "gh3":
            self.compile_gh3()
        elif game == "ghwt":
            self.compile_ghwt()
        elif game == "gh5":
            self.compile_gh5()
        elif game == "ghwor":
            self.compile_ghwor()
        return

    def compile_pak(self):
        self.project_save_path()
        if self.project_file_path.text() == '' or not os.path.exists(self.project_file_path.text()):
            print("There is no save file path!")
            return
        game = self.game_select_group.checkedButton().objectName()
        if game == "gh3":
            self.compile_gh3()
        elif game == "ghwt":
            self.compile_ghwt("skip_audio")
        elif game == "gh5":
            self.compile_gh5()
        elif game == "ghwor":
            self.compile_ghwor()
        return

    def open_file_dialog_audio(self, text_field):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Audio Files (*.flac *.mp3 *.ogg *.wav)",
                                                   options=options)

        if file_name:
            text_field.setText(file_name)

    def open_file_dialog_folder(self, text_field):
        options = QFileDialog.Options()
        folder_name = QFileDialog.getExistingDirectory(self, "Open Folder", "", options=options)

        if folder_name:
            text_field.setText(folder_name)

    def open_file_dialog_midi(self, text_field):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "MIDI Files (*.mid *.midi)", options=options)

        if file_name:
            text_field.setText(file_name)

    def open_file_dialog_qb(self, text_field):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "",
                                                   "QB or Text Files (*.txt *.qb *.qb.xen *.qb.ps3)", options=options)

        if file_name:
            text_field.setText(file_name)

    def p2_rhythm_toggle(self):
        if self.p2_rhythm_check.isChecked():
            self.rhythm_label_gh3.setText("Rhythm")
        else:
            self.rhythm_label_gh3.setText("Bass")
            if self.coop_audio_check.isChecked():
                self.coop_audio_check.setChecked(False)

    def project_save_path(self):
        if self.project_file_path.text() == '' or not os.path.exists(self.project_file_path.text()):
            self.project_saveas_path()
        else:
            self.save_project()

    def project_saveas_path(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save GH Project File", "", "GH Project Files (*.ghproj)",
                                                   options=options)

        if file_name:
            self.project_file_path.setText(file_name)
            self.save_project()

    def save_project(self):
        save_vars = {
            # Metadata
            "game": self.game_select_group.checkedButton().objectName(),
            "title_input": self.title_input.text(),
            "artist_text_select": self.artist_text_select.currentText(),
            "artist_text_other": self.artist_text_other.text(),
            "artist_input": self.artist_input.text(),
            "year_input": self.year_input.value(),
            "cover_checkbox": self.cover_checkbox.isChecked(),
            "cover_year_input": self.cover_year_input.value(),
            "cover_artist_input": self.cover_artist_input.text(),
            "genre_select": self.genre_select.currentText(),
            "checksum_input": self.checksum_input.text(),
            "author_input": self.author_input.text(),

            # WT Data
            "kick_input": self.kick_input.text(),
            "snare_input": self.snare_input.text(),
            "cymbals_input": self.cymbals_input.text(),
            "toms_input": self.toms_input.text(),

            "guitar_input": self.guitar_input.text(),
            "bass_input": self.bass_input.text(),
            "vocals_input": self.vocals_input.text(),

            "backing_input": self.backing_input.text(),
            "crowd_input": self.crowd_input.text(),

            "encrypt_audio": self.encrypt_audio.isChecked(),

            "preview_minutes": self.preview_minutes.value(),
            "preview_seconds": self.preview_seconds.value(),
            "preview_mills": self.preview_mills.value(),

            "ghwt_set_end": self.ghwt_set_end.isChecked(),
            "length_minutes": self.length_minutes.value(),
            "length_seconds": self.length_seconds.value(),
            "length_mills": self.length_mills.value(),

            "ghwt_midi_file_input": self.ghwt_midi_file_input.text(),
            "ghwt_perf_override_input": self.ghwt_perf_override_input.text(),
            "ghwt_ska_files_input": self.ghwt_ska_files_input.text(),
            "ghwt_song_script_input": self.ghwt_song_script_input.text(),
            "ghwt_countoff_select": self.ghwt_countoff_select.currentText(),
            "ghwt_drumkit_select": self.ghwt_drumkit_select.currentText(),
            "ghwt_vocal_gender_select": self.ghwt_vocal_gender_select.currentText(),
            "vocal_scroll_speed_input": self.vocal_scroll_speed_input.value(),
            "ghwt_band_vol": self.ghwt_band_vol.value(),

            "band_tier_value": self.band_tier_value.value(),
            "drums_tier_value": self.drums_tier_value.value(),
            "guitar_tier_value": self.guitar_tier_value.value(),
            "bass_tier_value": self.bass_tier_value.value(),
            "vocals_tier_value": self.vocals_tier_value.value(),

            # WTDE Settings
            "game_icon_input": self.game_icon_input.text(),
            "game_category_input": self.game_category_input.text(),
            "band_input": self.band_input.text(),
            "skeleton_type_g_select": self.skeleton_type_g_select.currentText(),
            "skeleton_type_b_select": self.skeleton_type_b_select.currentText(),
            "skeleton_type_v_select": self.skeleton_type_v_select.currentText(),
            "skeleton_type_d_select": self.skeleton_type_d_select.currentText(),
            "guitar_mic_check": self.guitar_mic_check.isChecked(),
            "bass_mic_check": self.bass_mic_check.isChecked(),
            "use_new_clips_check": self.use_new_clips_check.isChecked(),

            # GH3 Data

            "guitar_input_gh3": self.guitar_input_gh3.text(),
            "rhythm_input_gh3": self.rhythm_input_gh3.text(),
            "backing_input_gh3": self.backing_input_gh3.text(),

            "p2_rhythm_check": self.p2_rhythm_check.isChecked(),
            "coop_audio_check": self.coop_audio_check.isChecked(),

            "coop_guitar_input_gh3": self.coop_guitar_input_gh3.text(),
            "coop_rhythm_input_gh3": self.coop_rhythm_input_gh3.text(),
            "coop_backing_input_gh3": self.coop_backing_input_gh3.text(),

            "crowd_input_gh3": self.crowd_input_gh3.text(),

            "preview_minutes_gh3": self.preview_minutes_gh3.value(),
            "preview_seconds_gh3": self.preview_seconds_gh3.value(),
            "preview_mills_gh3": self.preview_mills_gh3.value(),

            "length_minutes_gh3": self.length_minutes_gh3.value(),
            "length_seconds_gh3": self.length_seconds_gh3.value(),
            "length_mills_gh3": self.length_mills_gh3.value(),

            "gh3_midi_file_input": self.gh3_midi_file_input.text(),
            "gh3_perf_override_input": self.gh3_perf_override_input.text(),
            "gh3_countoff_select": self.gh3_countoff_select.currentText(),
            "gh3_vocal_gender_select": self.gh3_vocal_gender_select.currentText(),
            "gh3_bassist_select": self.gh3_bassist_select.currentText(),

            "gh3_band_vol": self.gh3_band_vol.value(),
            "gh3_gtr_vol": self.gh3_gtr_vol.value(),

            # Compile Data
            "beat_16th_high_input": self.beat_16th_high_input.value(),
            "beat_16th_low_input": self.beat_16th_low_input.value(),
            "beat_8th_high_input": self.beat_8th_high_input.value(),
            "beat_8th_low_input": self.beat_8th_low_input.value(),
            "beatlines_check": self.beatlines_check.isChecked(),

            "hmx_hopo_value": self.hmx_hopo_value.value(),
            "hopo_mode_select": self.hopo_mode_select.currentText(),
            "platform": self.platform_button_group.checkedButton().objectName(),

            "compile_input": self.compile_input.text(),
            "project_file_path": self.project_file_path.text(),
            "force_ffmpeg_check": self.force_ffmpeg_check.isChecked(),

        }

        if not self.compile_input.text():
            self.compile_input.setText(os.path.dirname(self.project_file_path.text()))

        with open(self.project_file_path.text(), "w") as file:
            json.dump(save_vars, file, separators=(',', ':'), indent=4)

    def load_project_file(self, ghproj=""):
        if ghproj:
            open_path = ghproj
        else:
            open_path = QFileDialog.getOpenFileName(self, "Open Project File", "", "Project Files (*.ghproj)")[0]
        if not open_path or not os.path.exists(ghproj):
            return
        self.project_file_path.setText(open_path)
        with open(self.project_file_path.text(), "r") as file:
            load_vars = json.load(file)
        game_index = self.game_select.findChildren(QRadioButton)
        for i in game_index:
            if i.objectName() == load_vars["game"]:
                i.setChecked(True)
                break
        platform_index = self.platform_button_group.findChildren(QRadioButton)
        for i in platform_index:
            if i.objectName() == load_vars["platform"]:
                i.setChecked(True)
                break

        check_boxes = ["cover_checkbox", "p2_rhythm_check", "coop_audio_check", "beatlines_check", "encrypt_audio", "ghwt_set_end",
                       "guitar_mic_check", "bass_mic_check", "use_new_clips_check", "force_ffmpeg_check"]

        for x in check_boxes:
            try:
                to_set = getattr(self, x)
                to_set.setChecked(load_vars[x])
                load_vars.pop(x)
            except:
                pass

        load_vars.pop("game")
        load_vars.pop("platform")

        for key, value in load_vars.items():
            try:
                field = getattr(self, key)
                if isinstance(field, QLineEdit):
                    field.setText(value)
                elif isinstance(field, QComboBox):
                    field.setCurrentText(value)
                elif isinstance(field, QSpinBox) or isinstance(field, QDoubleSpinBox):
                    field.setValue(value)
            except:
                pass

        if not self.compile_input.text():
            self.compile_input.setText(os.path.dirname(self.project_file_path.text()))

    def set_end_time(self):
        if self.ghwt_set_end.isChecked():
            self.length_label.setText("End Time:")
        else:
            self.length_label.setText("Length:")
        self.update_prev_time_wt()

    def set_game_fields(self):
        self.setUpdatesEnabled(False)
        game = self.game_select_group.checkedButton().objectName()
        genre_base = ["Rock", "Punk", "Glam Rock", "Black Metal", "Classic Rock", "Pop"]
        genre_wt = ["Heavy Metal", "Goth"]
        genre_gh5 = ["Alternative", "Big Band", "Blues", "Blues Rock", "Country", "Dance", "Death Metal", "Disco",
                     "Electronic", "Experimental", "Funk", "Grunge", "Hard Rock", "Hardcore", "Hip Hop", "Indie Rock",
                     "Industrial", "International", "Jazz", "Metal", "Modern Rock", "New Wave", "Nu Metal", "Pop Punk",
                     "Pop Rock", "Prog Rock", "R&B", "Reggae", "Rockabilly", "Ska Punk", "Southern Rock", "Speed Metal",
                     "Surf Rock"]
        genre_wor = ["Hardcore Punk", "Heavy Metal", "Progressive Rock"]
        # Hip hop is the only one that has an underscore in its name in the game
        self.genre_select.clear()

        drum_kit_base = ["Classic Rock", "Electro", "Fusion", "Heavy Rock", "Hip Hop", "Modern Rock"]
        drum_kit_wt = drum_kit_base + ["Blip Hop", "Cheesy", "Computight", "Conga", "Dub", "Eightys", "Gunshot",
                                       "House", "India",
                                       "Jazzy", "Old School", "Orchestral", "Scratch", "Scratch_Electro"]
        drum_kit_gh5 = drum_kit_base + ["Bigroom Rock", "Dance", "Metal", "Noise", "Standard Rock"]
        self.ghwt_drumkit_select.clear()

        self.compile_tabs.removeTab(2)
        self.compile_tabs.removeTab(1)
        if any([game == "gh3", game == "gha"]):
            self.genre_select.setDisabled(True)
        elif game == "ghwt":
            self.genre_select.addItems(sorted(genre_base + genre_wt))
            self.ghwt_drumkit_select.addItems(sorted(drum_kit_wt))
        elif game == "gh5":
            self.genre_select.addItems(sorted(genre_base + genre_gh5) + ["Other"])
            self.ghwt_drumkit_select.addItems(sorted(drum_kit_gh5))
        elif game == "ghwor":
            self.genre_select.addItems(sorted(genre_gh5 + genre_wor) + ["Other"])
            self.ghwt_drumkit_select.addItems(sorted(drum_kit_gh5))

        if all([game != "gh3", game != "gha"]):
            self.genre_select.setDisabled(False)
            self.cover_checkbox.setDisabled(False)
            self.compile_tabs.insertTab(1, self.audio_tab_wt, "Audio")
            self.compile_tabs.insertTab(2, self.song_data_tab_wt, "Song Data")
        else:
            self.compile_tabs.insertTab(1, self.audio_tab_gh3, "Audio")
            self.compile_tabs.insertTab(2, self.song_data_tab_gh3, "Song Data")
            if game == "gh3":
                self.crowd_input_gh3.setDisabled(True)
                self.crowd_select_gh3.setDisabled(True)
                self.cover_checkbox.setDisabled(True)
            else:
                self.crowd_input_gh3.setDisabled(False)
                self.crowd_select_gh3.setDisabled(False)
                self.cover_checkbox.setDisabled(False)

        self.setUpdatesEnabled(True)

    def wt_audio_fields(self):
        self.kick_select.clicked.connect(partial(self.open_file_dialog_audio, self.kick_input))
        self.snare_select.clicked.connect(partial(self.open_file_dialog_audio, self.snare_input))
        self.cymbals_select.clicked.connect(partial(self.open_file_dialog_audio, self.cymbals_input))
        self.toms_select.clicked.connect(partial(self.open_file_dialog_audio, self.toms_input))

        self.guitar_select.clicked.connect(partial(self.open_file_dialog_audio, self.guitar_input))
        self.bass_select.clicked.connect(partial(self.open_file_dialog_audio, self.bass_input))
        self.vocals_select.clicked.connect(partial(self.open_file_dialog_audio, self.vocals_input))

        self.backing_select.clicked.connect(partial(self.open_file_dialog_audio, self.backing_input))
        self.crowd_select.clicked.connect(partial(self.open_file_dialog_audio, self.crowd_input))

        self.ghwt_set_end.toggled.connect(self.set_end_time)

    def wt_song_data_fields(self):
        self.ghwt_midi_file_select.clicked.connect(partial(self.open_file_dialog_midi, self.ghwt_midi_file_input))
        self.ghwt_perf_override_select.clicked.connect(partial(self.open_file_dialog_qb, self.ghwt_perf_override_input))
        self.ghwt_ska_files_select.clicked.connect(partial(self.open_file_dialog_folder, self.ghwt_ska_files_input))
        self.ghwt_song_script_select.clicked.connect(partial(self.open_file_dialog_qb, self.ghwt_song_script_input))

        for x in [self.skeleton_type_b_select, self.skeleton_type_d_select, self.skeleton_type_v_select]:
            self.combo_copy(self.skeleton_type_g_select, x)

    def gh3_audio_fields(self):
        self.guitar_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.guitar_input_gh3))
        self.rhythm_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.rhythm_input_gh3))
        self.backing_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.backing_input_gh3))
        self.crowd_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.crowd_input_gh3))

        self.coop_guitar_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.coop_guitar_input_gh3))
        self.coop_rhythm_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.coop_rhythm_input_gh3))
        self.coop_backing_select_gh3.clicked.connect(partial(self.open_file_dialog_audio, self.coop_backing_input_gh3))

        self.p2_rhythm_check.toggled.connect(self.p2_rhythm_toggle)

    def gh3_song_data_fields(self):
        self.gh3_midi_file_select.clicked.connect(partial(self.open_file_dialog_midi, self.gh3_midi_file_input))
        self.gh3_perf_override_select.clicked.connect(partial(self.open_file_dialog_qb, self.gh3_perf_override_input))
        bassists = ["Default"] + ["Axel", "Casey", "Izzy", "Judy", "Johnny", "Lars", "Midori", "Xavier", "Slash",
                                  "Tom Morello", "Lou", "God of Rock", "Grim Ripper"]
        self.gh3_bassist_select.addItems(bassists)

    def compile_fields(self):
        self.hmx_hopo_value.valueChanged.connect(self.update_ns_value)

        self.compile_select.clicked.connect(partial(self.open_file_dialog_folder, self.compile_input))

        self.project_file_save.clicked.connect(self.project_save_path)
        self.project_file_saveas.clicked.connect(self.project_saveas_path)
        self.project_file_open.clicked.connect(self.load_project_file)

        self.compile_button.clicked.connect(self.compile_song_package)
        self.compile_pak_button.clicked.connect(self.compile_pak)

    def update_ns_value(self):
        self.ns_hopo_value.setText(str(round(self.ns_value(), 5)))

    def ns_value(self):
        return 1920 / self.hmx_hopo_value.value() / 4

    def conv_to_secs(self, loc):
        if loc == "start":
            return self.preview_minutes.value() * 60 + self.preview_seconds.value() + self.preview_mills.value() / 1000
        elif loc == "end":
            return self.length_minutes.value() * 60 + self.length_seconds.value() + self.length_mills.value() / 1000

    def update_prev_time_wt(self):
        start_time = self.conv_to_secs("start")
        end_time = self.conv_to_secs("end")
        if self.ghwt_set_end.isChecked():
            end_time += start_time
        else:
            end_time -= start_time

        end_min = int(end_time // 60)
        end_sec = int(end_time % 60)
        end_mills = round(end_time % 1, 3) * 1000

        self.length_minutes.setValue(end_min)
        self.length_seconds.setValue(end_sec)
        self.length_mills.setValue(end_mills)

    def combo_copy(self, source, destination):
        for i in range(source.count()):
            item_text = source.itemText(i)
            destination.addItem(item_text)

    def midi_check(self):
        if not self.ghwt_midi_file_input.text():
            print("No MIDI file selected! Cancelling compilation")
            return 0
        elif not os.path.isfile(self.ghwt_midi_file_input.text()):
            print("MIDI file not found! Cancelling compilation")
            return 0
        return self.ghwt_midi_file_input.text()

    def wor_checksum(self):
        text, ok = QInputDialog.getText(None, "Proper DLC ID Required",
                                        "Please insert your song's dlc ID from Onyx\nNumbers only (do not include 'dlc')")
        if ok and text:
            try:
                int(text)
                self.checksum_input.setText(f"dlc{text}")
            except:
                print("Invalid DLC ID!")
                self.wor_checksum()


    def gen_checksum(self):
        game = self.game_select_group.checkedButton().objectName()
        if self.checksum_input.text() == '':
            if game == "ghwt":
                self.checksum_input.setText(
                    self.title_input.text().replace(" ", "").translate(str.maketrans('', '', string.punctuation)))
            elif game == "ghwor":
                self.wor_checksum()
        elif game == "ghwor" and not self.checksum_input.text().startswith("dlc"):
            self.wor_checksum()
        else:
            self.checksum_input.setText(
                self.checksum_input.text().replace(" ", "").translate(str.maketrans('', '', string.punctuation)))
        self.checksum_input.setText(self.checksum_input.text().lower())

    def compile_gh3(self):
        return

    def compile_ghwt(self, *args):

        midi_file = self.midi_check()
        if not midi_file:
            return

        self.gen_checksum()
        ini = configparser.ConfigParser()
        ini.optionxform = str
        ini["ModInfo"] = {
            "Name": self.checksum_input.text(),
            "Description": "Created with Addy's Toolkit",
            "Author": self.author_input.text(),
            "Version": "1"
        }
        artist_text = self.artist_text_select.currentText()
        if artist_text == "Other" or artist_text == "By":
            artist_text = "artist_text_by"
            orig_artist = 1
        else:
            artist_text = "artist_text_as_made_famous_by"
            orig_artist = 0
        ini["SongInfo"] = {
            "Checksum": self.checksum_input.text(),
            "Title": self.title_input.text(),
            "Artist": self.artist_input.text(),
            "Year": self.year_input.text(),
            "ArtistText": artist_text,
            "OriginalArtist": str(orig_artist),
            "Leaderboard": 1,
            "Singer": self.ghwt_vocal_gender_select.currentText(),
            "Genre": self.genre_select.currentText(),
            "Countoff": self.ghwt_countoff_select.currentText().lower(),
            "Drumkit": self.ghwt_drumkit_select.currentText().replace(" ", "").lower(),
            "Volume": str(self.ghwt_band_vol.value()),
        }
        if self.game_icon_input.text().replace(" ", ""):
            ini["SongInfo"]["GameIcon"] = self.game_icon_input.text()
        if self.game_category_input.text().replace(" ", ""):
            ini["SongInfo"]["GameCategory"] = self.game_category_input.text()
        if self.band_input.text().replace(" ", ""):
            ini["SongInfo"]["Band"] = self.band_input.text()
        if self.use_new_clips_check.isChecked():
            ini["SongInfo"]["UseNewClips"] = "1"
        if not self.skeleton_type_b_select.currentText() == "Default":
            ini["SongInfo"]["SkeletonTypeB"] = self.skeleton_type_b_select.currentText()
        if not self.skeleton_type_g_select.currentText() == "Default":
            ini["SongInfo"]["SkeletonTypeG"] = self.skeleton_type_g_select.currentText()
        if not self.skeleton_type_v_select.currentText() == "Default":
            ini["SongInfo"]["SkeletonTypeV"] = self.skeleton_type_v_select.currentText()
        if not self.skeleton_type_d_select.currentText() == "Default":
            ini["SongInfo"]["SkeletonTypeD"] = self.skeleton_type_d_select.currentText()
        if self.bass_mic_check.isChecked():
            ini["SongInfo"]["MicForBassist"] = "1"
        if self.guitar_mic_check.isChecked():
            ini["SongInfo"]["MicForGuitarist"] = "1"

        start_time = self.conv_to_secs("start")
        end_time = self.conv_to_secs("end")
        if not self.ghwt_set_end.isChecked():
            end_time += start_time

        song_name = self.checksum_input.text()
        song_folder = f"{self.compile_input.text()}/{song_name}"
        try:
            os.mkdir(song_folder)
        except:
            pass

        music_folder = f"{song_folder}/Content/MUSIC"
        if not os.path.isdir(music_folder):
            os.makedirs(music_folder)

        with open(f"{song_folder}/song.ini", "w") as f:
            ini.write(f, space_around_delimiters=False)

        hopo_val = self.hmx_hopo_value.value()
        compile_args = [midi_file, hopo_val, song_name, "ghwt", "wtde"]

        if self.encrypt_audio.isChecked():
            compile_args += ["encrypt"]
        perf = self.ghwt_perf_override_input.text()
        if perf:
            if os.path.isfile(perf):
                compile_args += ["replace_perf", perf]

        ska_files = self.ghwt_ska_files_input.text()
        if ska_files:
            if os.path.isdir(ska_files):
                compile_args += ["add_ska", ska_files]

        hopo_mode = self.hopo_mode_select.currentText()
        if hopo_mode == "Guitar Hero 3":
            compile_args += ["gh3_mode"]
        elif hopo_mode == "Rock Band":
            compile_args += ["rb_mode"]
        elif hopo_mode == "Guitar Hero World Tour+":
            compile_args += ["force_only"]

        if self.ghwt_song_script_input.text():
            compile_args += ["song_script", self.ghwt_song_script_input.text()]

        if self.force_ffmpeg_check.isChecked():
            compile_args += ["ffmpeg"]
        try:
            song_pak = mid_gen.make_mid(*compile_args)[0]
        except Exception as E:
            traceback.print_exc()
            return
        with open(f"{song_folder}\\Content\\a{song_name}_song.pak.xen", "wb") as f:
            f.write(song_pak)

        if not "skip_audio" in args:
            all_audio = [self.kick_input, self.snare_input, self.cymbals_input, self.toms_input, self.guitar_input,
                         self.bass_input, self.vocals_input, self.backing_input, self.crowd_input]
            all_audio_path = []
            for files in all_audio:
                if not files.text() or not os.path.isfile(files.text()):
                    if not os.path.isfile(files.text()):
                        print(f"File for {files.objectName()} does not exist. Using blank audio")
                    files.setText(f"{audio_folder}/default_audio/blank.wav")
                all_audio_path.append(files.text())
            try:
                drum, inst, other, preview = af.get_padded_audio(all_audio_path, song_name, start_time, end_time,
                                                                 *compile_args)
            except Exception as E:
                traceback.print_exc()
                print("Error compiling audio.")
                return
            for enum, x in enumerate([drum, inst, other, preview]):
                if enum != 3:
                    with open(f"{music_folder}\\{song_name}_{enum + 1}.fsb.xen", 'wb') as f:
                        f.write(x)
                else:
                    with open(f"{music_folder}\\{song_name}_preview.fsb.xen", 'wb') as f:
                        f.write(x)
        print("Complete!")
        return

    def compile_gh5(self):
        return

    def compile_ghwor(self):
        self.gen_checksum()
        return

    def first_boot(self):
        self.compile_tabs.clear()
        self.compile_tabs.addTab(self.metadata_tab, "Metadata")
        self.compile_tabs.addTab(self.audio_tab_gh3, "Audio")
        self.compile_tabs.addTab(self.song_data_tab_gh3, "Song Data")
        self.compile_tabs.addTab(self.compile_tab, "Compile")
        self.update_ns_value()
        # self.compile_tabs.addTab(self.performance_manager_tab, "Performance Manager")
        self.set_game_fields()
