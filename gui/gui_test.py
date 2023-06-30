import tkinter as tk
from tkinter import filedialog

class DragDropGUI:
    def __init__(self, master):
        self.master = master
        master.title("Drag and Drop")

        self.path_text = tk.StringVar()
        self.path_text.set("Drag and drop a file here")

        self.path_entry = tk.Entry(master, textvariable=self.path_text)
        self.path_entry.grid(row=0, column=0)

        # Enable drag-and-drop
        self.path_entry.bind("<Button-1>", self.select_file)
        self.path_entry.bind("<B1-Motion>", self.do_nothing)

    def select_file(self, event):
        file_path = filedialog.askopenfilename()
        self.path_text.set(file_path)

    def do_nothing(self, event):
        pass

if __name__ == "__main__":
    root = tk.Tk()
    gui = DragDropGUI(root)
    root.mainloop()