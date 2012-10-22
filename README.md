### Tracklist Scrobbler is an application that allows you to scrobble a podcast's tracklist to last.fm.

**Please bear in mind that this is in no way finished or stable. I am only working on this in my spare time, which is very limited in the coming months.**

It currently is able to parse the following podcasts' tracklists:
* Armin van Buuren - A State of Trance
* Above & Beyond - Trance Around The World
* Markus Schulz - Global DJ Broadcast
* Gareth Emery - The Gareth Emery Podcast
* Ferry Corsten - Corsten's Countdown
* Andy Moor - Moor Music
* Tiësto - Club Life Podcast
* 3voor12 Draait
* Arnej - The Arnej Podcast
* John O'Callaghan - Subculture

# Current bugs:
- When an artist contains a dash (-) the parser assumes everything after the first dash is the title, when instead it is still part of the artist
- album parsing is very limited right now

# Future ideas:
- Retrieve a podcast's tracklist from the internet automatically before parsing
- Implement a better statusbar
- Remove more info about special tracks (World Premiere, Global Selection Winner, Future Favorite, Web Vote Winner, etc.)