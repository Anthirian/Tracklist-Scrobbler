'''
Created on Jun 28, 2012

@author: Geert
'''
from Tkinter import *
from ttk import *
import tkMessageBox
import tkSimpleDialog

from Scrob import Scrob as Scrobbler

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


class Interface(Frame):
    '''
    classdocs
    '''
    def __init__(self, master=None):
        '''
        Constructor
        '''
        self.ts = Scrobbler("geertsmelt", "GerritAdriaan")
        
        Frame.__init__(self, master)
        self.grid(sticky=N+S+E+W)
        
        self.createLoginForm()
        self.createFormatOptions()
        self.createTextArea()
        self.createButtonsToolbar()
        self.addResizingWeights()

    def createLoginForm(self):
        '''
        Create a login form in the top right corner of the application window
        '''
        self.loginDetails = Frame(self)
        
        usernameLabel = Label(self.loginDetails, text="Username:")
        self.usernameField = Entry(self.loginDetails)
        usernameLabel.grid(row=0, column=0, padx=5)
        self.usernameField.grid(row=0, column=1)
        
        passwordLabel = Label(self.loginDetails, text="Password:")
        self.passwordField = Entry(self.loginDetails, show="*")
        passwordLabel.grid(row=0, column=3, padx=5)
        self.passwordField.grid(row=0, column=4)
        
        self.loginDetails.grid(row=0, column=1, columnspan=2, pady=10, padx=8, sticky=E)

    def createFormatOptions(self):
        self.options = Frame(self)
        self.keuze = StringVar()
        
        #TODO: make track format display use a predetermined list
        Label(self.options, text="Please select the correct podcast below:", font="Candara").grid(pady=5, padx=5)
        
        Radiobutton(self.options, text="A State of Trance", value="A State of Trance", variable=self.keuze).grid(sticky=N + W)
        Radiobutton(self.options, text="Trance Around The World", value="Trance Around The World", variable=self.keuze).grid(sticky=N + W)
        Radiobutton(self.options, text="The Gareth Emery Podcast", value="The Gareth Emery Podcast", variable=self.keuze).grid(sticky=N + W)
        Radiobutton(self.options, text="Moor Music", value="Moor Music", variable=self.keuze).grid(sticky=N + W)
        Radiobutton(self.options, text="Corsten's Countdown", value="Corsten's Countdown", variable=self.keuze).grid(sticky=N + W)
        Radiobutton(self.options, text="3Voor12 Draait", value="3Voor12 Draait", variable=self.keuze).grid(sticky=N + W)
        
        self.options.grid(row=1, column=0, padx=20, sticky=N)


    def addResizingWeights(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)


    def createTextArea(self):
        self.textarea = Text(self, height=35, width=100, padx=5, pady=5)
        self.textarea.insert("end", "Please paste your tracklist here\n\nOnly use one line per track!")
        self.textarea.grid(row=1, column=1, columnspan=2, sticky=N + S + E + W)


    def createButtonsToolbar(self):
        self.parseButton = Button(self, text="Parse", command=self.parse, width=30)
        self.scrobbleButton = Button(self, text="Scrobble", command=self.scrobble, width=30)
        self.quitButton = Button(self, text="Quit", command=self.quit)
        
        self.parseButton.grid(row=7, column=0, sticky=S, padx=5, pady=5)
        self.scrobbleButton.grid(row=7, column=1, sticky=S, padx=5, pady=5)
        self.quitButton.grid(row=7, column=2, sticky=S, padx=5, pady=5)        
    
    def getUser(self):
        '''
        Get the username from the corresponding field
        '''
        return self.usernameField.get()
    
    def getPassword(self):
        '''
        Get the password from the corresponding field
        '''
        return self.passwordField.get()        
    
    def parse(self):
        trackFormat = self.keuze.get()
        invoer = self.textarea.get(1.0, END)
        if not trackFormat:
            tkMessageBox.showerror("Format not specified", "You forgot to select a podcast type to parse. " + 
                                   "Without this, the parser cannot parse the tracks properly. " + 
                                   "Please select a podcast type and try again.")
            return
        invoer = invoer.split("\n")
        
        # Filter all blank lines
        contents = filter(None, invoer)
        
        if not contents:
            tkMessageBox.showerror("No data", "You have not entered a tracklist. Please provide a tracklist before pressing the Scrobble button.")
        else:
            duration = tkSimpleDialog.askinteger("Podcast duration", "What is the duration of the podcast (in hours)?", parent=self)
            hours_ago = tkSimpleDialog.askinteger("Listen time", "How long ago did you listen to this podcast (in hours)? Leave blank for 'just now'", initialvalue=000)
            self.lastfmdata, results = self.ts.parse_tracklist(contents, duration, hours_ago)
        
            if results:
                self.textarea.delete(1.0, END)
                for track in results:
                    self.textarea.insert(INSERT, track + "\n")
                readyToScrobble = tkMessageBox.showinfo("Please check the parsed tracks", "The tracks that were parsed have been written to the text field. Please check if they are correct. " + 
                                                           "When you feel it is correct, you may press the Scrobble button to scrobble the tracks to Last.fm")
                print readyToScrobble
                if readyToScrobble == "yes":
                    try:
                        self.ts.scrobble(self.lastfmdata)#, self.getUser(), self.getPassword())
                    except:
                        raise
                    else:
                        tkMessageBox.showinfo("Success!", "All tracks were correctly scrobbled to Last.fm.")
            else:
                tkMessageBox.showerror("No results", "The tracklist you provided could not be parsed into valid tracks. Please correct the tracklist if you can.")
        
        #ts.format_tracks("tracks", self.formatting.get())
        
        #if tkMessageBox.askyesno("Test", "Test twee"):
        #    print "Test parseButton"
    
    def scrobble(self):
        user = self.getUser()
        pw = self.getPassword()
        if user and pw:
            self.textarea.delete(1.0, END) 
            self.textarea.insert(INSERT, "You entered the following credentials:\nUsername:\t%s\nPassword:\t%s" % (user, pw))
        else:
            tkMessageBox.showerror("Authentication error", "One of the login fields is empty. Please fix it before continuing.")
            
gui = Interface()
gui.master.title("Tracklist Scrobbler")
gui.mainloop() 