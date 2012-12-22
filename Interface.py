"""
Created on Jun 28, 2012

@author: Geert
"""
from Scrobbler import Scrobbler
from Parser import Parser

from Tkinter import *
from ttk import *
import tkMessageBox
import tkSimpleDialog

from pylast import WSError, NetworkError, MalformedResponseError

class AutoScrollbar(Scrollbar):
    """
    A scrollbar that hides itself if it's not needed. Only works if you use the grid geometry manager.
    """
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
    """
    classdocs
    """
    def __init__(self, parser, scrobbler, master = None):
        """
        Initiate the scrobbler and parser and build the GUI
        """
        self.p = parser
        self.ts = scrobbler
        self.parsed = False
        
        Frame.__init__(self, master)
        self.grid(sticky = N + S + E + W)
        self.master.iconbitmap("images/favicon.ico")
        self.bind_class("Text", "<Control-a>", self.select_all)
        self.bind_all("<Control-w>", self.quit_application)

        self.create_notifications_area()
        self.create_login_form()
        self.create_supported_podcasts()
        self.create_branding()
        self.create_tracklist_container()
        self.create_buttons_toolbar()
        self.add_resizing_weights()

    def quit_application(self, event):
        """
        Quit the application when the provided event occurs
        """
        self.quit()

    def select_all(self, event):
        """
        Select all text inside the widget that is the source of the provided event
        """
        event.widget.tag_add("sel", "1.0", "end")
    
    def notify(self, notification_text, notification_color = "black"):
        """
        Print a notification in the status bar in the top left corner of the window
        """
        self.notification.configure(text = notification_text, foreground = notification_color)
    
    def clear_notifications(self):
        """
        Clear all notification text
        """
        self.notification.configure(text = "", foreground = "black")
    
    def create_notifications_area(self):
        self.notification = Label(self, text = "", foreground = "red", font = "Cambria", wraplength = 750)
        self.notification.grid(row = 0, column = 0, columnspan = 2, pady = 10, padx = 10, sticky = N + W)
    
    def create_login_form(self):
        """
        Create a login form in the top right corner of the application window
        """
        self.loginDetails = Frame(self)
        
        usernameLabel = Label(self.loginDetails, text = "Username:", anchor = N)
        self.usernameField = Entry(self.loginDetails)
        usernameLabel.grid(row = 0, column = 0, padx = 5)
        self.usernameField.grid(row = 0, column = 1)
        
        passwordLabel = Label(self.loginDetails, text = "Password:", anchor = N)
        self.passwordField = Entry(self.loginDetails, show = "*")
        self.passwordField.bind("<Return>", self.scrobble_using_return)
        passwordLabel.grid(row = 0, column = 3, padx = 5)
        self.passwordField.grid(row = 0, column = 4)
        
        self.loginDetails.grid(row = 0, column = 1, columnspan = 2, pady = 10, padx = 8, sticky = N + E)
    
    def create_branding(self):
        self.logo = PhotoImage(file = "images/audioscrobbler_small.gif")
        picture = Label(self, image = self.logo)
        picture.grid(row = 2, column = 0, pady = 15, sticky = S)
    
    def create_supported_podcasts(self):
        self.options = Frame(self)
        self.podcast = StringVar()
        
        Label(self.options, text = "Please select the correct podcast below:", font = "Cambria").grid(pady = 5)
        
        supportedPodcasts = sorted(self.p.get_supported_podcasts())
        for name in supportedPodcasts:
            Radiobutton(self.options, text = name, value = name, takefocus = False, variable = self.podcast).grid(sticky = N + W, padx = 5)

        self.just_listened = BooleanVar()
        Checkbutton(self.options, text = "I just finished listening to this podcast", variable = self.just_listened, onvalue = True, offvalue = False).grid(sticky = N + W, padx = 5, pady = 25)        
        
        self.options.grid(row = 1, column = 0, padx = 20, sticky = N)

    def add_resizing_weights(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight = 1)
        top.columnconfigure(0, weight = 1)
        
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 10)
        self.columnconfigure(1, weight = 1)

    def create_tracklist_container(self):
        self.textarea = Text(self, height = 35, width = 100, padx = 5, pady = 5)
        self.textarea.insert("end", "Please paste your tracklist here\n\nOnly use one line per track!")
        self.textarea.grid(row = 1, column = 1, rowspan = 2, columnspan = 2, sticky = N + S + E + W)
        
        sb = AutoScrollbar(self)
        sb.grid(row = 1, column = 3, sticky = N + S, rowspan = 2)
        self.textarea.config(yscrollcommand = sb.set)


    def create_buttons_toolbar(self):
        self.scrobbleButton = Button(self, text = "Scrobble", command = self.scrobble, width = 30, state = NORMAL if self.parsed else DISABLED)
        self.parseButton = Button(self, text = "Parse", command = self.parse, width = 30)
        self.quitButton = Button(self, text = "Quit", command = self.quit)
        
        self.scrobbleButton.grid(row = 7, column = 0, sticky = S, padx = 7, pady = 7)
        self.parseButton.grid(row = 7, column = 1, sticky = S, padx = 7, pady = 7)
        self.quitButton.grid(row = 7, column = 2, sticky = S, padx = 7, pady = 7)        
    
    def get_user(self):
        """
        Get the username from the corresponding field
        """
        return self.usernameField.get()
    
    def get_pass(self):
        """
        Get the password from the corresponding field
        """
        return self.passwordField.get()        
    
    def get_container_contents(self):
        """
        Get the contents of the textarea as a list, after filtering for blank lines
        """
        return filter(None, self.textarea.get(1.0, END).split("\n"))
    
    def parse(self):
        """
        Parse the entered tracklist into artist, featured artist, title, album, remix and record label
        """
        self.clear_notifications()
        trackFormat = self.podcast.get()
        contents = self.textarea.get(1.0, END)
        if not trackFormat:
            self.notify("Please select a podcast type and try again.", "red")
            return
        
        # Split on end-of-lines and filter all blank lines
        contents = contents.split("\n")
        contents = filter(None, contents)
        
        if not contents:
            self.notify("You have not entered a tracklist. Please provide a tracklist before pressing the Scrobble button.", "red")
        else:
            self.clear_notifications()
            if not self.just_listened.get():
                self.time_offset = tkSimpleDialog.askinteger("Please specify a time offset", "How long ago did you listen to this podcast (in hours)? Enter 0 for 'just now.'", initialvalue = "0")
            else:
                self.time_offset = 0
            self.lastfmdata, results = self.p.parse_tracklist(contents, self.podcast.get(), self.time_offset)
        
            if results:
                self.textarea.delete(1.0, END)
                for track in results:
                    self.textarea.insert(INSERT, track + "\n")
                self.parsed = True
                self.scrobbleButton.configure(state = NORMAL)
                self.notify("Parsing complete. Please correct any wrong tracks below and press Scrobble.")
            else:
                self.notify("The tracklist you provided could not be parsed into valid tracks. Please correct the tracklist and try again.", "red")

    def scrobble_using_return(self, event):
        """
        Scrobble the tracklist to last.fm when pressing Return
        (Currently only used in the password field)
        """
        self.scrobble()

    def scrobble(self):
        """
        Scrobble a previously parsed tracklist to Last.fm
        """
        self.clear_notifications()
        if self.parsed:
            user = self.get_user()
            pw = self.get_pass()
            self.lastfmdata = self.p.parse_user_modifications(self.get_container_contents(), self.podcast, self.time_offset)
            if user and pw:
                try:
                    self.ts.login(user, pw)
                except WSError, wse:
                    tkMessageBox.showerror("Authentication failed", "Something went wrong during authentication. Last.fm responded:\n\"%s\"" % wse.details)
                except MalformedResponseError, mre:
                    tkMessageBox.showerror("Malformed Response", "Something is wrong with last.fm:\n\"%s\"\nThis could indicate that the website is currently having problems." % mre)
                except NetworkError, ne:
                    tkMessageBox.showerror("Network Error", "A network error occurred:\n\"%s\"" % ne)
                else:
                    self.ts.scrobble(self.lastfmdata)
                    self.notify("Scrobbled successfully!", "black")
                    self.scrobbleButton.configure(state = DISABLED)
                    self.parsed = False
            else:
                tkMessageBox.showerror("Authentication error", "One of the login fields is empty. Please fix it before continuing.")
        else:
            self.notify("This tracklist has to be parsed before it can be scrobbled. Please press 'Parse' and then try scrobbling again.", "red")

if __name__ == "__main__":
    s = Scrobbler()
    p = Parser()
    gui = Interface(p, s)
    gui.master.title("Tracklist Scrobbler")
    gui.mainloop()
