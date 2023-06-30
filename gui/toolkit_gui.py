import sys
from PySide6.QtWidgets import QApplication
from main_window import AddysToolkit

def open_gui(sys_args, proj_file = ""):
    app = QApplication(sys_args)
    gui = AddysToolkit(proj_file)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    open_gui(sys.argv)