#encoding: utf-8
'''
Created on Jul 1, 2012

@author: Geert
'''
import time
import re

class Parser(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''        
        self.UNKNOWN = "ID"
        self.USRMOD = "User Modified"
        
        self.ASOT = "Armin van Buuren - A State of Trance"
        self.TATW = "Above & Beyond - Trance Around The World"
        self.GDJB = "Markus Schulz - Global DJ Broadcast"
        self.TGEP = "Gareth Emery - The Gareth Emery Podcast"
        self.CC = "Ferry Corsten - Corsten's Countdown"
        self.AMMM = "Andy Moor - Moor Music"
        self.TCLP = "Tiësto - Club Life Podcast"
        self.DVTD = "3voor12 Draait"
        self.TAP = "Arnej - The Arnej Podcast"
        self.JOCS = "John O'Callaghan - Subculture"
        self.MWMM = "Marcel Woods - Musical Madness"
        
        self.longShows = [self.ASOT, self.TATW, self.GDJB]
        self.mediumShows = [self.TAP]
        self.shortShows = [self.TGEP, self.CC, self.AMMM, self.DVTD, self.TCLP, self.JOCS, self.MWMM]
    
    def get_supported_podcasts(self):
        '''
        Get a list of podcasts that are supported by the parser.
        '''
        return self.longShows + self.mediumShows + self.shortShows
    
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

    def find_label(self, formatting, title):
        '''
        Parse a record label if present in the title
        '''
        label = ""
        if formatting == self.TATW or formatting == self.TGEP or formatting == self.ASOT or formatting == self.AMMM:
            pattern = re.compile("\(.*?\)" if formatting == self.TATW else "\[.*?\]", flags=re.I)
            match = pattern.search(title)
            if match:
                label = title[match.start() + 1:match.end() - 1]
                title = title[:match.start()].strip()
        return title, label

    def find_remix(self, formatting, title):
        '''
        Parse a remix if present in the title
        '''
        # To parse a remix or mashup we take everything between the brackets, either round or square
        pattern = re.compile("\[.*?\]" if formatting == self.TATW else "\(.*?\)", flags=re.I)
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
        pattern = re.compile("""[\(\[].*[from].*[album].*['"].*['"].*[\)\]]""", flags=re.I)
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
        illegalCharacters = ["’", "‘", "’", "–"]
        replacementCharacters = ["'", "'", "'", "-"]
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
    
    

    
    
    
    def calculate_timestamps(self, tracklist, duration, hours_ago):
        '''
        Calculate timestamps to use when scrobbling multiple tracks
        '''
        try:
            totalLength = int(duration * 3600)
        except ValueError:
            totalLength = 0
        except TypeError:
            totalLength = 0
        finally:
            try:
                offset = hours_ago * 3600
            except ValueError:
                offset = 0
            except TypeError:
                offset = 0
            numberOfTracks = len(tracklist)
            
            try:
                trackDuration = totalLength / numberOfTracks
            except ZeroDivisionError:
                return
            else:
                trackNumber = 1
                for track in tracklist:
                    if trackNumber <= numberOfTracks:
                        track['timestamp'] = int(time.time() - offset - totalLength + trackDuration * trackNumber)
                        trackNumber += 1
                
        
        return tracklist
    
    def parse_line(self, line, podcast):
        '''
        Parses a given line into a series of variables to be used in a format_tracks
        These variables include artist, title, record label and remix
        '''
        album, remix, label = "", "", ""
        trackToScrobble = {}
        
        # Clean up the line before parsing
        line = line.strip()
        line = self.replace_illegal_characters(line)
        line = self.remove_special_track_info(line)
        
        # Check if the line was blank
        if not line:
            return trackToScrobble
        
        if not podcast == self.USRMOD:
            separators = ['"', '–', '-']
            
            # Split the line into the artist (head) and into the title, album and label (tail)
            for sep in separators:
                triple = line.partition(sep)
                head, _, tail = triple
                # if we have split, tail is non-empty and we should break the loop
                if tail:
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
            
            # 3 Voor 12 Draait doesn't add album, remix and label information to their tracklist, so don't try to parse it
            if not podcast == self.DVTD:
                title, label = self.find_label(podcast, title)
                title, album = self.find_album(title)
                title, remix = self.find_remix(podcast, title)
                title = title.strip('"')
            
            #mashupTrack = self.parse_line(mashup)
        else:
            #TODO: Parse tracks that are already close to the wanted format
            artist, _, title = line.partition("-")
            return []
        
        # Finally add all the gathered information to the track we want to format_tracks
        trackToScrobble['artist'] = artist
        trackToScrobble['featured'] = featured
        trackToScrobble['title'] = title
        trackToScrobble['remix']= remix
        trackToScrobble['label'] = label
        trackToScrobble['presents'] = presents
        trackToScrobble['album'] = album
    
        # Prevent adding ID's of any kind by zeroing out any track that contains an ID
        for text in trackToScrobble.values():
            if text == self.UNKNOWN or text.find('?') != -1:
                return {}
        
        return trackToScrobble
    
    def parse_tracklist(self, tracks, podcast, hours_ago):
        listOfTracks = tracks 
        tracklist = []
        for line in listOfTracks:
            track = self.parse_line(line, podcast)
            # Test for empty result
            if track:
                tracklist.append(track)
        
        if podcast in self.longShows:
            duration = 2
        elif podcast in self.mediumShows:
            duration = 1.5
        else:
            duration = 1
        tracklist = self.calculate_timestamps(tracklist, duration, hours_ago)
        
        try:
            self.forLastFM, self.forGUI = self.format_tracks(tracklist)
        except TypeError:
            return [], []
        
        return self.forLastFM, self.forGUI
    
    def parse_user_modifications(self, listOfTracks, podcast, hours_ago):
        '''
        Check if the user has made modifications to the tracks we parsed and create new Last.fm data from it
        '''
        if listOfTracks == self.forGUI:
            return self.forLastFM
        else:    
            data = []
            if podcast in self.longShows:
                duration = 2
            elif podcast in self.mediumShows:
                duration = 1.5
            else:
                duration = 1
                
            for line in listOfTracks:
                track = self.parse_line(line, self.USRMOD)
                if track:
                    data.append(track)
                        
            data = self.calculate_timestamps(data, duration, hours_ago)
            
            forLastFM, _ = self.format_tracks(data)
            
            return forLastFM
    
    def format_tracks(self, tracklist):
        '''
        Correctly format the track for the GUI and for scrobbling
        '''
        forGUI, forLastFM = [], []
        if tracklist:
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
                
                # Determine the time the track was played to use in writing to the interface
                (_, _, _, hour, mins, sec, _, _, _) = time.localtime(tracktime)
                formattedtime = "%02d:%02d:%02d" % (hour, mins, sec)
                parsedTrack = "%s.  %s - %s" % (formattedtime, artist, title)
                parsedTrack += (" [%s]" % album) if album else "" 
                
                forGUI.append(parsedTrack)
                forLastFM.append(trackToScrobble)
        
        return forLastFM, forGUI