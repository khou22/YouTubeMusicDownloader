#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Started: February 7, 2016
# Finished: February 9, 2016
# GitHub Repository Name: MusicDownloader

# Modules:
from PIL import Image
import requests
from io import BytesIO
import webbrowser # This module can control the browser
import json # Json encoder/decoder
from bs4 import BeautifulSoup # Module to sort through HTML
import lxml # Module to prepare html for BeautifulSoup
from urllib.request import urlopen
import sys # Allow more control over printing
import string # More ways to manipulate strings
import unidecode # Decodes weird characters
import youtube_dl # For downloading YouTube videos/audio
import eyed3 # For editing ID3 tags for mp3 file
import os # More control over Mac file system

numShow = 5

# Prompt User for Keywords for Song
userSearch = input("Search for song: ") # Reads input as a string
# userSearch = input("Search for song (use quotes): ") # Reads input as raw code
# print("Searching for " + userSearch)
userSearch = userSearch.strip() # Remove extraneous white space

# Search for song in iTunes Store
# Documentation: http://www.apple.com/itunes/affiliates/resources/documentation/itunes-store-web-service-search-api.html
baseURL = "https://itunes.apple.com/search?"
searchKeys = [
    ["term", userSearch],
    ["country", "US"],
    ["media", "music"],
    ["entity", "song"],
    ["limit", "50"],
    ["lang", "en_us"],
    ["explicit", "yes"]
]
finalURL = baseURL
for i in range(0, len(searchKeys)): # len() returns length of a variable
    # print "Term: %d" % (i)
    currentKey = searchKeys[i]
    criteria = str(currentKey[1]) #Make sure it's a string
    criteria = criteria.replace(" ", "%20") # %20 represents a space
    appendStr = currentKey[0] + "=" + criteria # Build url
    # print(appendStr)
    if i < (len(searchKeys) - 1):
        appendStr += "&"
    finalURL += appendStr

# print("Final URL: " + finalURL) # Debugging
# webbrowser.open(finalURL)

# Retrieve and Save iTunes JSON Data
response = urlopen(finalURL) #Get HTML source code
html = response.read() #HTML source code
soup = BeautifulSoup(html, "lxml") # Using lxml parser
print("")
print("*********** Found iTunes data ***********")
print("")
# print(soup.prettify()) # Feedback

rawJSON = soup.find('p').text # Just the json text
rawJSON.strip() # Trim the white space

# Parse iTunes JSON Data
iTunesObj = json.loads(rawJSON) # Decode JSON
# print(iTunesObj)

results = iTunesObj['results']
b = numShow
if len(results) < numShow:
    b = len(results)

for i in range(0, b):
    sys.stdout.write("(%i) Track Name: " % i)
    sys.stdout.flush() # No line break
    print(results[i]['trackName']) # Adds a line break after
    print("    Artist: %s" % results[i]['artistName'])
    print("    Album: %s" % results[i]['collectionName'])
    print("    Genre: %s" % results[i]['primaryGenreName'])
    print("")

print("Which song is the one you were looking for?")
iTunesSearchSelection = input("Type the respective index: ")
songData = results[int(iTunesSearchSelection)]
print() # Line break
print("Selected:")
print("%s by %s" % (songData['trackName'], songData['artistName']))
print(songData)
print() # Line break


# *******************   Find song on YouTube   *******************

searchAudio = input("Search for audio video? (y/n) ") # Ask if want to search for audio on YouTube
extra = ""
if searchAudio is "y": # If only want to search for audio videos
    extra = " Audio" # add on 'audio' to search

baseURL = "https://www.youtube.com/results?search_query="
YouTubeSearch = songData['trackName'] + " " + songData['artistName'] + extra
print() # Line break

YouTubeSearch = unidecode.unidecode(YouTubeSearch) # Remove complex unicode characters
print("Searching for '%s' on YouTube" % YouTubeSearch)
print() # Line break
# out = YouTubeSearch.translate(string.maketrans("",""), string.punctuation) # Remove punctuation
YouTubeSearch = YouTubeSearch.replace(" ", "+") # Remove spaces with '+'
finalURL = baseURL + YouTubeSearch # Final URL

print(finalURL)

"""
response = urllib.urlopen(finalURL) #Get HTML source code
html = response.read() #HTML source code
soup = BeautifulSoup(html, "lxml") # Using lxml parser

links = soup.find_all("a")
print(links)

videoLinks = [] # Start empty
# videoTitleElements = soup.findAll("h3", { "class": "title-and-badge style-scope ytd-video-renderer" }) # Get video titles then get video links
videoTitleElements = soup.findAll("a", { "id": "video-title" }) # Get video titles then get video links
print(videoTitleElements)
for title in videoTitleElements:
    print("Found title %s" % title)
    link = title.findAll("a") # Get link within the title
    videoLinks.append(link[0]) # Add link to master list

videoUploaders = [] # Start empty
videoUploaderElements = soup.findAll("div", { "class": "yt-lockup-byline " }) # Get video uploader divs
for element in videoUploaderElements:
    uploader = element.findAll("a") # Extract the uploader link
    if len(uploader) is not 0:
        videoUploaders.append(uploader[0]) # Append to master list

videoTimes = soup.findAll("div", { "class": "ytd-thumbnail-overlay-time-status-renderer" }) # In case there are playlists, find the div

videos = [];
# Stores all the results on the page except for the last 3 hits on the page
upper = len(videoTimes) - 3
numPlaylists = 0
for i in range(0, upper):
    # print i
    # print(videoTimes[i])
    time = videoTimes[i].findAll("span", { "class": "video-time" }) # Find within the larger div
    if not time: # If array is empty (ie. no time found for that video)
        numPlaylists += 1
        # print "Found a playlist"
    else: # If not a playlists
        # The video must be a playlist
        time = time[0] # First result

        link = "https://www.youtube.com" + videoLinks[i].get('href')

        # print(videoLinks[i].contents[0])
        # print(link)
        # print videoUploaders[i]

        # Structure of array:
        # [name, link, uploader, length]
        videos.append(
            [
                videoLinks[i].contents[0],
                link,
                videoUploaders[i].contents[0],
                time.text
            ]
        )

# Only returns up to specified number
print "Found %s playlist(s)" % numPlaylists
for i in range(0, numShow):
    video = videos[i]
    sys.stdout.write("(%i) Video name: " % i)
    sys.stdout.flush() # No line break
    print video[0] # Adds a line break after
    print "    Link: %s" % video[1]
    print "    Uploader: %s" % video[2]
    print "    Length: %s" % video[3]
    print("")

milliseconds = songData['trackTimeMillis']
x = milliseconds / 1000
seconds = x % 60
x /= 60
minutes = x % 60

time = str(minutes) + ":" + str(seconds)

print "Which video is the one you were looking for?"
print "The iTunes version is: %s" % time
YouTubeSelection = input("Type the respective index: ")
print "" # Line break
data = videos[YouTubeSelection]
"""

# Manual link input
print("Which video is the one you were looking for?")
link = input("copy paste the link: ")
data = ['', link]

fileName = songData['artistName'] + " - " + songData['trackName'] # Declare file name
filePath = "~/Desktop/" # Declare file path

ydl_opts = { # Set options
    'format': 'bestaudio/best',
    # 'outtmpl': u'%(title)s-%(id)s.%(ext)s',
    'outtmpl': filePath + fileName + ".%(ext)s",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192' # 128, 160, 192, 210, 256
    }],
    'quiet': False
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    print(data[1])
    ydl.download([data[1]]) # Download the song

# *******************   Find Image Artwork   *******************
# print("Finding Google Image for album artwork")
# Add code here:


# *******************   Update ID3 Tags   *******************

mp3Path = os.path.expanduser(filePath + fileName + ".mp3")
year = str(songData['releaseDate'])
year = int(year[:4])

audiofile = eyed3.load(mp3Path)
audiofile.tag.title = songData['trackName']
audiofile.tag.artist = songData['artistName']
audiofile.tag.album = songData['collectionName']
audiofile.tag.album_artist = songData['artistName'] # This needs to be changed - need to be able to find album artist, not song artist
audiofile.tag.track_num = (songData['trackNumber'], songData['trackCount'])
audiofile.tag.disc_num = (songData['discNumber'], songData['discCount'])
audiofile.tag.genre = songData['primaryGenreName']
audiofile.tag.release_date = year
audiofile.tag.orig_release_date = year
audiofile.tag.recording_date = year
audiofile.tag.encoding_date = year
audiofile.tag.taggin_date = year


# Append Image
# Reference: http://tuxpool.blogspot.com/2013/02/how-to-store-images-in-mp3-files-using.html
image_url = songData['artworkUrl100'].replace('100x100', '500x500')
response = requests.get(image_url)
# img = Image.open(BytesIO(response.content).read())
# imageData = open("test.jpg", "rb").read() # Stores image data
audiofile.tag.images.set(3, BytesIO(response.content).read(), "image/jpeg", "Description") # 3 for front cover, 4 for back, 0 for other

audiofile.tag.save()

print() # Line break
print("Updated ID3 Tags")
# print "Song Year (Must Manually Add): %s" % year
print() # Line break
print("**************   Complete   **************")
