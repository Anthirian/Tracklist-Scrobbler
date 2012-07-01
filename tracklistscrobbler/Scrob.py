#encoding: utf-8
'''
Created on Mar 27, 2012

@author: Geert
'''
from pylast import md5, LastFMNetwork
from Parser import Parser

class Scrob(object):
    '''
    classdocs
    '''    
    def __init__(self, username, password):
        '''
        Constructor
        '''
        self.p = Parser()
        self.API = "b7b91229e4232d9e6dfa232b3937923e"
        self.secret = "ad646ed84aad9da4f1189454a4872cd9"
        password_hash = md5(password)
        
        self.lastfm = LastFMNetwork(self.API, self.secret, None, username, password_hash)
    
    def scrobble(self, data):
        '''
        Scrobble a list of dicts that each contain a single parsed track to Last.fm
        '''
        #self.lastfm.scrobble_many(data)
        print "scrobbling this crap", data
    
#ts = Scrobbler("geertsmelt", "GerritAdriaan")
#ts.format_tracks("tracklist.txt")