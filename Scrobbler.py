# encoding: utf-8
"""
Created on Mar 27, 2012

@author: Geert
"""
from pylast import md5, LastFMNetwork, WSError


class Scrobbler(object):
    """
    classdocs
    """

    def __init__(self):
        """
        Constructor
        """
        self.API = "b7b91229e4232d9e6dfa232b3937923e"
        self.secret = "ad646ed84aad9da4f1189454a4872cd9"

        # Allow users to create a scrobbler without logging in first
        self.authenticated = False

    def login(self, username, password):
        """
        Log in using the username and password provided. Use this function before scrobbling.
        Returns error details in case of failure
        :param password:
        :param username:
        """
        password_hash = md5(password)
        try:
            self.lastfm = LastFMNetwork(self.API, self.secret, None, username, password_hash)
        except WSError:
            raise
        else:
            self.authenticated = self.lastfm.get_authenticated_user().get_name() == username

    def scrobble(self, data):
        """
        Scrobble a list of dicts that each contain a single parsed track to Last.fm
        :param data: the tracks to scrobble
        """
        if self.authenticated:
            self.lastfm.scrobble_many(data)
        else:
            raise WSError("You are not authenticated yet, please use the login function before scrobbling.")
        return data