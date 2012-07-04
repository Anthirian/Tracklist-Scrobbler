from Scrob import Scrob as Scrobbler
from Parser import Parser
from Interface import Interface

if __name__ == "__main__":
    s = Scrobbler()
    p = Parser()
    gui = Interface(p, s)
    gui.master.title("Tracklist Scrobbler")
    gui.mainloop() 