import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QFileDialog, QLabel
from PySide6.QtCore import QEvent
from PySide6.QtGui import QDragEnterEvent, QDropEvent

class MidiPakXenConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MIDI to PAK.XEN Converter')
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        self.midi_input_label = QLabel('MIDI Input File:', self)
        layout.addWidget(self.midi_input_label)

        self.midi_input_field = QLineEdit(self)
        self.midi_input_field.setPlaceholderText('Drag and drop MIDI file or click to browse...')
        self.midi_input_field.setAcceptDrops(True)
        self.midi_input_field.installEventFilter(self)
        layout.addWidget(self.midi_input_field)

        self.output_label = QLabel('Output File:', self)
        layout.addWidget(self.output_label)

        self.output_field = QLineEdit(self)
        self.output_field.setPlaceholderText('Output file will be automatically generated...')
        layout.addWidget(self.output_field)

        self.convert_button = QPushButton('Convert', self)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)

    def eventFilter(self, obj, event):
        if obj == self.midi_input_field and event.type() == QDragEnterEvent:
            if event.mimeData().hasUrls():
                event.accept()
            else:
                event.ignore()
        elif obj == self.midi_input_field and event.type() == QDropEvent:
            self.midi_input_field.setText(event.mimeData().urls()[0].toLocalFile())
            self.set_output_filename()
        elif obj == self.midi_input_field and event.type() == QEvent.MouseButtonPress:
            options = QFileDialog.Options()
            filename, _ = QFileDialog.getOpenFileName(self, "Open MIDI File", "", "MIDI Files (*.mid *.midi)", options=options)
            if filename:
                self.midi_input_field.setText(filename)
                self.set_output_filename()
        return False

    def set_output_filename(self):
        midi_filename = self.midi_input_field.text()
        if midi_filename.endswith(('.mid', '.midi')):
            output_filename = midi_filename[:-4] + '.pak.xen'
            self.output_field.setText(output_filename)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MidiPakXenConverter()
    main_window.show()
    sys.exit(app.exec())