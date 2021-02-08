# HydusTagGrabber
A script I made to automatically parse tags for Hydrus Network.

This script probably won't be of much use to anyone else unless they've managed to make the same mistakes as me.

## Requirements
* Python 3+
* Requests `pip install -U requests`
* Hydrus-API `pip install -U hydrus-api`
* lxml `pip install -U lxml`

## Usage
This is a very narrow-scope script. It only supports Gelbooru, e621 and Rule34.xxx and all configuration is done within the script.  
First off, open the script in a text editor and add your api keys and make your changes.  
Make a file alongside the script matching the "hash_file" variable (default: hashes.txt) and put the sha256 hashes of all the files you want to parse in it, one per line.  
Files to be parsed need to be tagged with the name of the booru using the booru: namespace. The name must correspond to one of the entires in the parsers section of the script.

## About
Prior to making the [importer for Pocket](https://github.com/CuddleBear92/Hydrus-Presets-and-Scripts/tree/master/Downloaders/Pocket) as a catch-all file source, when I found an image I wanted to save while on my phone, I would download it, and let Hydrus Network import automatically with Syncthing. This was quick and easy, but it also left me with a lot of work when I got home. Since I use [Anime Boxes](https://www.animebox.es/), I would get a few tags to parse, but there would still be a lot missing, and all the spaces would be underscores. The only other thing I got from this format was the name of the booru, which I tagged with the 'booru' namespace.  

Getting this stuff sorted out turned out to be a huge amount of work, which I never got done until now. Today, I made this script to automate that process. It takes a list of hashes stored alongside the script in hashes.txt, pulls the booru tag, calculates the md5 of the file and finally looks up the tags to send back to the client.

I don't intend to do any more work on this script, as it's run its purpose for me.
