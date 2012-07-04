#encoding: utf-8
'''
Created on Jun 28, 2012

@author: Geert
'''
from Tkinter import *
from ttk import *
import tkMessageBox
import tkSimpleDialog

from Parser import Parser
from Scrob import Scrob as Scrobbler
from pylast import WSError

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
    def __init__(self, parser, scrobbler, master=None):
        '''
        Constructor
        '''
        self.p = parser
        self.ts = scrobbler
        
        Frame.__init__(self, master)
        self.grid(sticky=N+S+E+W)
        self.master.iconbitmap("favicon.ico")
        self.bind_class("Text","<Control-a>", self.select_all)
        
        self.createLoginForm()
        self.createFormatOptions()
        self.createImage()
        self.createTextArea()
        self.createButtonsToolbar()
        self.addResizingWeights()
        
        self.parsed = False
    
    def select_all(self, event):
        event.widget.tag_add("sel","1.0","end")
    
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
    
    def createImage(self):
        self.logo = PhotoImage(file="audioscrobbler_small.gif")
        picture = Label(self, image=self.logo)
        picture.grid(row=2, column=0, pady=15, sticky=S)
    
    def createFormatOptions(self):
        self.options = Frame(self)
        self.podcast = StringVar()
        
        Label(self.options, text="Please select the correct podcast below:", font="Cambria").grid(pady=5)
        
        supportedPodcasts = self.p.get_supported_podcasts()
        for name in supportedPodcasts:
            Radiobutton(self.options, text=name, value=name, variable=self.podcast).grid(sticky=N+W, padx=5)
        self.options.grid(row=1, column=0, padx=20, sticky=N)

    def addResizingWeights(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=10)
        self.columnconfigure(1, weight=1)

    def createTextArea(self):
        self.textarea = Text(self, height=35, width=100, padx=5, pady=5)
        self.textarea.insert("end", "Please paste your tracklist here\n\nOnly use one line per track!")
        self.textarea.grid(row=1, column=1, rowspan=2, columnspan=2, sticky=N+S+E+W)
        
        sb = AutoScrollbar(self)
        sb.grid(row=1, column=3, sticky=N+S, rowspan=2)
        self.textarea.config(yscrollcommand=sb.set)


    def createButtonsToolbar(self):
        self.scrobbleButton = Button(self, text="Scrobble", command=self.scrobble, width=30)
        self.parseButton = Button(self, text="Parse", command=self.parse, width=30)
        self.quitButton = Button(self, text="Quit", command=self.quit)
        
        self.scrobbleButton.grid(row=7, column=0, sticky=S, padx=5, pady=5)
        self.parseButton.grid(row=7, column=1, sticky=S, padx=5, pady=5)
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
    
    def getTextAreaContents(self):
        '''
        Get the contents of the textarea as a list, after filtering for blank lines
        '''
        return filter(None, self.textarea.get(1.0, END).split("\n"))
    
    def parse(self):
        trackFormat = self.podcast.get()
        invoer = self.textarea.get(1.0, END)
        if not trackFormat:
            tkMessageBox.showerror("Format not specified", "You forgot to select a podcast type to parse. " + 
                                   "Without this, the parser cannot parse the tracks properly. " + 
                                   "Please select a podcast type and try again.")
            return
        
        # Split on end-of-lines and filter all blank lines
        invoer = invoer.split("\n")
        contents = filter(None, invoer)
        
        if not contents:
            tkMessageBox.showerror("No data", "You have not entered a tracklist. Please provide a tracklist before pressing the Scrobble button.")
        else:
            self.hours_ago = tkSimpleDialog.askinteger("Listen time", "How long ago did you listen to this podcast (in hours)? Enter 0 for 'just now'", initialvalue="0")
            self.lastfmdata, results = self.p.parse_tracklist(contents, self.podcast.get(), self.hours_ago)
        
            if results:
                self.textarea.delete(1.0, END)
                for track in results:
                    self.textarea.insert(INSERT, track + "\n")
                self.parsed = True
                tkMessageBox.showinfo("Please check the parsed tracks", "The tracks that were parsed have been written to the text field. Please correct any wrong tracks. " + 
                                                           "When you feel it is correct, you may press 'Scrobble' to scrobble the tracks to Last.fm")
            else:
                tkMessageBox.showerror("No results", "The tracklist you provided could not be parsed into valid tracks. Please correct the tracklist if you can.")
    
    def scrobble(self):
        '''
        Scrobble the tracklist to Last.fm
        '''
        if self.parsed:
            user = self.getUser()
            pw = self.getPassword()
            self.lastfmdata = self.p.parse_user_modifications(self.getTextAreaContents(), self.podcast, self.hours_ago)
            if user and pw:
                try:
                    self.ts.login(user, pw)
                except WSError, wse:
                    tkMessageBox.showerror("Authentication failed", "Something went wrong during authentication. Last.fm responded:\n\"%s\"" % wse.details)
                else:
                    result = self.ts.scrobble(self.lastfmdata)
                    tkMessageBox.showinfo("Scrobbled successfully", "Scrobbled the following to Last.fm: " + str(result))
            else:
                tkMessageBox.showerror("Authentication error", "One of the login fields is empty. Please fix it before continuing.")
        else:
            tkMessageBox.showerror("Not parsed yet", "This tracklist has to be parsed before it can be scrobbled. Please press 'Parse' and then try scrobbling again.")