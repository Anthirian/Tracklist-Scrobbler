#encoding: utf-8
'''
Created on Mar 27, 2012

@author: Geert
'''
import pylast
import re
import codecs
import time

class Scrobbler(object):
    '''
    classdocs
    '''
    UNKNOWN = "ID"
    ASOT = "A State of Trance"
    TATW = "Trance Around The World"
    GDJB = "Global DJ Broadcast"
    TGEP = "The Gareth Emery Podcast"
    CC = "Corsten's Countdown"
    MM = "Moor Music"
    DVTD = "3 Voor 12 Draait"
    
    longShows = [ASOT, TATW, GDJB]
    shortShows = [TGEP, CC, MM, DVTD]
    formats = longShows + shortShows
    
    def __init__(self, username, password):
        '''
        Constructor
        '''
        self.API = "b7b91229e4232d9e6dfa232b3937923e"
        self.secret = "ad646ed84aad9da4f1189454a4872cd9"
        password_hash = pylast.md5(password)
        
        self.lastfm = pylast.LastFMNetwork(self.API, self.secret, None, username, password_hash)
    
    def scrobble(self, filename):
        with codecs.open(filename, encoding='utf-8') as inputFile:
            tracklist = []
            for line in inputFile:
                track = self.parse_line(line)
                # Test for empty result
                if track:
                    tracklist.append(track)
                        
            tracklist = self.calculate_timestamps(tracklist)
            
            # Correctly format the track before scrobbling
            parsedTracks, scrobbleList = [], []
            for track in tracklist:
                try:
                    tracktime = track['timestamp']
                except KeyError:
                    return
                
                # Build the artist of the track
                artist = track['artist']
                
                if track['presents']:
                    artist += " pres. " + track['presents']
                
                # Build the title of the track
                title = track['title']
                if track['featured']:
                    title += " (feat. " + track['featured'] + ")"
                if track['remix']:
                    title += " (" + track['remix'] + ")"
                
                album = track['album']
                
                trackToScrobble = {"artist": artist, "title": title, "timestamp": tracktime, "album": album}
                
                # Determine the time the track was played to use in writing to the output file
                (_, _, _, hour, mins, sec, _, _, _) = time.localtime(tracktime)
                formattedtime = "%02d:%02d:%02d" % (hour, mins, sec)
                parsedTrack = "%s.  %s - %s" % (formattedtime, artist, title)
                parsedTrack += (" [%s]" % album) if album else "" 
                
                print parsedTrack
                #parsedTracks.append(parsedTrack)
                scrobbleList.append(trackToScrobble)
            
            #return parsedTracks
        
            print "\nWe have parsed the above tracks to scrobble to last.fm, is this correct?"
            scrobblingActive = raw_input("The tracks will be scrobbled after you say yes. Y(es) or N(o) ").lower() == "Y".lower()
            
            if scrobblingActive:
                self.lastfm.scrobble_many(scrobbleList)
                print "Done! All above tracks were scrobbled to last.fm."
            else:
                print "Not scrobbling to last.fm. Please correct the incorrectly parsed track in %s and try again." % filename
    
    def strip_leading_digits(self, head):
        '''
        Regex for any combination of multiple digits followed by either a . or a ) and a whitespace
        '''
        pattern = re.compile(r"\A\d+[.)] *")
        match = pattern.match(head)
        artist = head[match.end() if match else 0:].strip()
        return artist

    def find_featured_artists(self, artist):
        '''
        Find featuredArtist artists in the artists.
        The featured artist is prefixed by any of the following:
        "feat. ", "feat ", "Feat. ", "Feat ", "ft. ", "ft ", "Ft ", "Ft. "
        '''
        # To do so we match 
        pattern = re.compile(" ?f[ea]*t.?[uring]* ", flags=re.I)
        match = pattern.search(artist)
        # If the artist contains a featuredArtist artist we check which term matched our regex, add that term as featuredArtist artist and remove it from the artist itself
        featuredArtist = ""
        if match:
            featuredArtist = artist[match.start():].strip() # only keep things in front of the 'feat.'
            featText = pattern.match(featuredArtist)
            if featText:
                featuredArtist = featuredArtist[featText.end():].strip() # take everything after 'feat.'
            artist = artist[:match.start()].strip() # take everything up to the start of 'feat.'
        return artist, featuredArtist

    def find_presented_artist(self, artist):
        '''
        If the artists would like to present an alias, parse it
        '''
        pattern = re.compile(" ?pres.?[ents]* ", flags=re.I)
        match = pattern.search(artist)
        presentedArtist = ""
        if match:
            presentedArtist = artist[match.end():].strip()
            artist = artist[:match.start()].strip()
        return artist, presentedArtist

    def find_label(self, format, title):
        '''
        Parse a record label if present in the title
        '''
        # Only parse record label when in alternative mode
        label = ""
        if format is self.TATW or format is self.TGEP or format is self.ASOT:
            pattern = re.compile("\(.*?\)" if format is self.TATW else "\[.*?\]", flags=re.I)
            match = pattern.search(title)
            if match:
                label = title[match.start() + 1:match.end() - 1]
                title = title[:match.start()].strip()
        return title, label

    def find_remix(self, format, title):
        '''
        Parse a remix if present in the title
        '''
        # To parse a remix or mashup we take everything between the brackets, either round or square
        pattern = re.compile("\[.*?\]" if format is self.TATW else "\(.*?\)", flags=re.I)
        match = pattern.search(title)
        remix = ""
        if match:
            remix = title[match.start() + 1:match.end() - 1]
            title = title[:match.start()].strip()
        return title, remix
    
    def find_album(self, title):
        '''
        Parse an album mention from the title
        '''
        # TODO: better regex naming
        pattern = re.compile("""\(.*[from].*[album].*['"].*['"].*\)""", flags=re.I)
        match = pattern.search(title)
        album = ""
        if match:
            # Search for text in single or double quotes
            albumNameRegex = re.compile("""['"].*['"]""", flags=re.I)
            albumName = albumNameRegex.search(title[match.start():match.end()])
            if albumName:
                album = title[match.start() + albumName.start() + 1:match.end()-2]
                title = title[:match.start()].strip('"').strip()
        return title, album
    
    def find_mashup(self, title):
        '''
        Find an incorrectly formatted mashup and split the title into multiple tracks
        '''
        pattern = re.compile("w/")
        match = pattern.search(title)
        title1, track = title, ""
        if match:
            print "w/ gevonden!"
            title1 = title[:match.start()]
            print title1
            track = title[match.end() + 1:]
            print track
        return title1, track
        
    def replace_illegal_characters(self, line):
        '''
        Remove any illegal (unicode) characters and replace them with their ASCII counterparts
        '''
        # TODO: Add more illegal characters and make it into a dict
        illegalCharacters = ["’", "‘", "–"]
        replacementCharacters = ["'", "'", "-"]
        for x in range(len(illegalCharacters)):
            if len(illegalCharacters) == len(replacementCharacters):
                line = line.replace(illegalCharacters[x], replacementCharacters[x])
            else:
                raise IndexError("The list of illegal characters and their replacements are not equally long!")
        
        return line
    
    def remove_special_track_info(self, line):
        '''
        Remove special types indications of a track. These are indicated by a text, followed b
        Examples of this are
        - FUTURE FAVORITE:
        - ASOT RADIO CLASSIC:  
        '''
        _, _, track = line.partition(":")
        return track.strip() if track else line
    
    def calculate_timestamps(self, tracklist):
        '''
        Calculate timestamps to use when scrobbling multiple tracks
        '''
        try:
            totalLength = int(raw_input("What is the duration of the podcast (in hours)? ")) * 3600
        except ValueError:
            print "You have not entered a correct duration!"
        else:
            try:
                offset = int(raw_input("How long ago did you listen to the podcast (in hours)? Leave blank for 'just now' ")) * 3600
            except ValueError:
                offset = 0
            numberOfTracks = len(tracklist)
            #totalLength = 7200 if numberOfTracks >= 17 else 3600
            
            try:
                trackDuration = totalLength / numberOfTracks
            except ZeroDivisionError:
                raise
            else:
                trackNumber = 1
                for track in tracklist:
                    if trackNumber <= numberOfTracks:
                        track['timestamp'] = int(time.time() - offset - totalLength + trackDuration * trackNumber)
                        trackNumber += 1
                
        
        return tracklist

    def parse_line(self, line):
        '''
        Parses a given line into a series of variables to be used in a scrobble
        These variables include artist, title, record label and remix
        '''		
        trackToScrobble = {}
        format = self.ASOT
        separators = ['–', '-', '"']
        
        # Clean up the line before parsing
        line = line.strip()
        line = self.replace_illegal_characters(line)
        line = self.remove_special_track_info(line)
        
        # Check if the line was blank
        if not line:
            return trackToScrobble
        
        # Split the line into the artist (head) and into the title, album and label (tail)
        for sep in separators:
            triple = line.partition(sep)
            head, _, tail = triple
            # if we have split, tail is non-empty and we should break the loop
            if tail:
                if sep is '"':
                    format = self.TATW
                # this dash is also used on lsdb for ASOT, so don't assume it's TGEP
                #elif sep is "–":
                    #format = self.TGEP
                break
        
        # If splitting failed for all separators, assume it is not a track and return nothing
        if not tail:
            return trackToScrobble
        
        # Parse the artist and any featured or presented artists
        artist = self.strip_leading_digits(head)
        artist, featured = self.find_featured_artists(artist)
        artist, presents = self.find_presented_artist(artist)
        
        # Parse the title into title, album, record label and remix and clean up all the parts
        title = tail.strip()
        #title, mashup = self.find_mashup(title)
        title, album = self.find_album(title)
        title, label = self.find_label(format, title)
        title, remix = self.find_remix(format, title)
        title = title.strip('"')
        
        #mashupTrack = self.parse_line(mashup)
        
        # Add all the gathered information to the track we want to scrobble
        trackToScrobble['artist'] = artist
        trackToScrobble['featured'] = featured
        trackToScrobble['title'] = title
        trackToScrobble['remix']= remix
        trackToScrobble['label'] = label
        trackToScrobble['presents'] = presents
        trackToScrobble['album'] = album
    
        # Prevent adding ID's of any kind by zeroing out any track that contains an ID
        for text in trackToScrobble.values():
            if text == self.UNKNOWN:
                return {}
        
        return trackToScrobble
    
ts = Scrobbler("geertsmelt", "GerritAdriaan")
ts.scrobble("tracklist.txt")