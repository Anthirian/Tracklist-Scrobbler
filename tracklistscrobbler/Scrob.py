#encoding: utf-8
'''
Created on Mar 27, 2012

@author: Geert
'''
from pylast import md5, LastFMNetwork

class Scrob(object):
    '''
    classdocs
    '''    
    def __init__(self):
        '''
        Constructor
        '''
        self.API = "b7b91229e4232d9e6dfa232b3937923e"
        self.secret = "ad646ed84aad9da4f1189454a4872cd9"
        
        # Allow users to create a scrobbler without logging in first
        self.authenticated = False
    
    def login(self, username, password):
        '''
        Log in using the username and password provided. Use this function before scrobbling.
        '''
        password_hash = md5(password)
        self.lastfm = LastFMNetwork(self.API, self.secret, None, username, password_hash)
        #TODO: get the authenticated user and match with the username variable instead of hardcoding
        self.authenticated = True
    
    def scrobble(self, data):
        '''
        Scrobble a list of dicts that each contain a single parsed track to Last.fm
        '''
        if self.authenticated:
            #self.lastfm.scrobble_many(data)
            print "scrobbling this crap", data
        else:
            print "You are not authenticated yet, please use the login function before scrobbling."
        return data