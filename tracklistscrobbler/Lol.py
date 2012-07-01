from Tkinter import *

class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"

root = Tk()

leftPanel = Frame(root)
options = Frame(leftPanel)
optionsLabel = Frame(leftPanel)

formatting = IntVar()

Label(optionsLabel, text="Which podcast does the tracklist correspond to?", pady=5, font="Calibri").grid(row=0, column=0, sticky="N")
Radiobutton(options, text="A State of Trance", font="Calibri", variable=formatting, value=1).grid(row=1, column=0, sticky="W")
Radiobutton(options, text="Trance Around The World", font="Calibri", variable=formatting, value=2).grid(row=2, column=0, sticky="W")
Radiobutton(options, text="The Gareth Emery Podcast", font="Calibri", variable=formatting, value=3).grid(row=3, column=0, sticky="W")
Radiobutton(options, text="Corsten's Countdown", font="Calibri", variable=formatting, value=4).grid(row=4, column=0, sticky="W")
Radiobutton(options, text="3Voor12 Draait", font="Calibri", variable=formatting, value=5).grid(row=5, column=0, sticky="W")

optionsLabel.grid()
options.grid()
leftPanel.grid(padx=10, pady=10, sticky="N", column=0, row=0)


rightPanel = Frame(root)

vscrollbar = AutoScrollbar(root)
vscrollbar.grid(row=0, column=1, sticky=N+S)
hscrollbar = AutoScrollbar(root, orient=HORIZONTAL)
hscrollbar.grid(row=1, column=1, sticky=E+W)

canvas = Canvas(rightPanel,
                yscrollcommand=vscrollbar.set,
                xscrollcommand=hscrollbar.set)
canvas.grid(row=0, column=0, sticky=N+S+E+W)

vscrollbar.config(command=canvas.yview)
hscrollbar.config(command=canvas.xview)

# make the canvas expandable
rightPanel.grid_rowconfigure(0, weight=1)
rightPanel.grid_columnconfigure(0, weight=1)

rightPanel.grid(column=1, row=0)

#
# create canvas contents

frame = Frame(canvas)
frame.rowconfigure(1, weight=1)
frame.columnconfigure(1, weight=1)

rows = 5
for i in range(1,rows):
    for j in range(1,10):
        button = Button(frame, padx=7, pady=7, text="[%d,%d]" % (i,j))
        button.grid(row=i, column=j, sticky='news')

canvas.create_window(0, 0, anchor=NW, window=frame)

frame.update_idletasks()

canvas.config(scrollregion=canvas.bbox("all"))

root.mainloop()