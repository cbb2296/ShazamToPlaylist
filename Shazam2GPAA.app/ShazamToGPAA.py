__version__ = "0.0.1"
#For use with Python 2.7, as gmusicapi has no support for 3.0
#will eventually make 
from gmusicapi import Mobileclient
from bs4 import BeautifulSoup
import argparse
import os.path
import Tkinter
import os.path
from Tkinter import *
api = Mobileclient()

email = ""
password = ""
filePath = ""
#playlist search
#returns "0" if nothing found
def searchforsong(title, artist):
	if len(artist) < 1 or len(title) < 1:
		#print "Bad artist or song name"
		return "0"
	title = title.lower()
	artist = artist.lower()
	if artist == "various artists":
                if title == "unknown":
                        #print 'Unknown Title and artist'
                        return "0"
                #print "Various Artists is just a placeholder, skipping over song: " + title
                return "0"
	s1 = api.search_all_access(title + " " + artist, 10)
	for song in s1["song_hits"]:
		if (song["track"]["title"].lower() == title) and \
		(song["track"]["artist"].lower() == artist):
			return song["track"]["nid"]
	#attempt 2
	#Removes "feat" from artist and title
	aa = artist
	try:
		artist = artist.split("feat")[0]
	except:
		artist = aa
	tt = title
	try:
		title = title.split("feat")[0]
	except:
		title = tt
	s2 = api.search_all_access(title + " " + artist, 10)
	for song in s2["song_hits"]:
		if ((song["track"]["title"].lower() == title) and \
		(song["track"]["artist"].lower() == artist)) or \
		song["score"] > 100:
			return song["track"]["nid"]
	#attempt #3
	#removes, "edit", "remix" and parentheses
	artist = artist.replace("(", "").replace(")", "").replace("edit", "").replace("remix", "")
	title = title.replace("(", "").replace(")", "").replace("edit", "").replace("remix", "")
	s3 = api.search_all_access(title + " " + artist, 10)
	for song in s3["song_hits"]:
		if ((song["track"]["title"].lower() == title) and \
		(song["track"]["artist"].lower() == artist)) or \
		song["score"] > 100:
			return song["track"]["nid"]
	#print "Couldn't find " + title + " by " + artist
	return "0"

def main(email, password, filePath):
        loginresult = api.login(email, password, Mobileclient.FROM_MAC_ADDRESS)
        
        shazamFile = open(filePath, 'r')
        
        #print(email + " " + password)
        if not loginresult:
                #print "Bad username or password"
                return
        shazamhtml = shazamFile
        htmltree = shazamhtml.read()
        soup = BeautifulSoup(htmltree, 'html.parser')
        table = soup.find('table')
        table_rows = table.findAll('tr')
        data = []
        for row in table_rows:
                #Empty row may break, catch exception
                try:
                        cols = row.find_all('td')
                        d = {}
                        d["Title"] = cols[0].text.strip()
                        d["TrackID"] = ""
                        d["Artist"] = cols[1].text
                        if not(d in data):
                                data.append(d)
                except Exception as ex:
                        print "Error parsing table row: " + ex.message
                        
        #now that we have everything
        playlists = api.get_all_user_playlist_contents()
        slist = 0
        shazamplaylist = ""
        isnew = False
        for i in range (0, len(playlists)-1):
                if playlists[i]["name"] == "Tagged by Shazam":
                        shazamplaylist = playlists[i]["id"]
                        slist = i
                        #print "Found existing playlist"
                        break
        if shazamplaylist == "":
                shazamplaylist = api.create_playlist("Tagged by Shazam", "Songs tagged by Shazam", public = False)
                #print "Creating new Playlist"
                isnew = True
        #Get all song id's
        songs = []
        for i in range (0, len(data)):
                try:
                        song = data[i]
                except Exception as ex:
                        #print "Error at i = " + str(i) + ":" + ex.message
                        continue
                nid = searchforsong(song["Title"], song["Artist"])
                if nid == "0":
                        data.pop(i)
                else:
                        songs.append(nid)
        #Check for preexising songs
        if not isnew:
                xlists = playlists[slist]["tracks"]
                for track in xlists:
                        if track["trackId"] in songs:
                                songs.remove(track["trackId"])
                songs = filter(None, songs)
        #add songs to playlist
        #print "Adding " + str(len(songs)) + " to playlist"
        response = api.add_songs_to_playlist(shazamplaylist, songs) 


def startGUI():
	top = Tkinter.Tk()
	message = "code by /u/vibbix. gui by /u/theblandyman"

	def submitData():
		email = emailForm.get()
		password = passwordForm.get()
		filePath = filePathForm.get()
		if(not os.path.isfile(filePath)):
			filePathForm.delete(0, END)
			filePathForm.insert(0, "file not found ")
		main(email, password, filePath)
		

	topMessage = Label(top, text="Shazam History > GPAA")

	emailForm = Entry(top)
	emailForm.focus_set()
	emailFormMessage = Label(top, text="Email:")
	
	passwordForm = Entry(top, show="*")
	passwordFormMessage = Label(top, text="Password:")

	filePathForm = Entry(top)
	filePathForm.insert(0,"Downloads/myshazam-history.html")
	fileFormMessage = Label(top, text="Path to file")

	submit = Tkinter.Button(top, text="submit", command = submitData)

	bottomMessage = Label(top, text=message)	

	topMessage.pack()
	emailFormMessage.pack()
	emailForm.pack()
	passwordFormMessage.pack()
	passwordForm.pack()
	fileFormMessage.pack()
	filePathForm.pack()
	submit.pack()
	bottomMessage.pack()

	top.mainloop()
	
startGUI()