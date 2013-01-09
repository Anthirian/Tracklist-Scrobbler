### Tracklist Scrobbler is an application that allows you to scrobble a podcast's tracklist to [Last.fm](http://www.last.fm).

**Please bear in mind that this is in no way finished or stable. I am only working on this in my spare time, which is very limited in the coming months.**

# Supported Podcasts
* 3voor12 Draait
* Above & Beyond - Group Therapy
* Aly & Fila - Future Sound of Egypt
* Andy Moor - Moor Music
* Armin van Buuren - A State of Trance
* Arnej - The Arnej Podcast
* Ferry Corsten - Corsten's Countdown
* Markus Schulz - Global DJ Broadcast
* Gareth Emery - The Gareth Emery Podcast
* Greg Downey - Global Code
* John O'Callaghan - Subculture
* M.I.K.E. - Club Elite Sessions
* Marcel Woods - Musical Madness
* Paul Oakenfold - Planet Perfecto
* Tiësto - Club Life Podcast

# Current bugs
- When an artist contains a dash (-) the parser assumes everything after the first dash is the title, when instead it is still part of the artist
- album parsing is very limited right now
- Armin van Buuren - A State of Trance tracklisting doesn't use dashes but newlines. At the moment this yields issues.

# Future ideas
- Retrieve a podcast's tracklist from the internet automatically before parsing
- Implement a better statusbar
- Remove more info about special tracks (World Premiere, Global Selection Winner, Future Favorite, Web Vote Winner, etc.)
- Remember user credentials