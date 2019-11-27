#!/usr/bin/python

import requests
import string
import random
import pathlib
import urllib.parse
from pycmus import remote
import json
from bs4 import BeautifulSoup


def get_soup(url, header):
	try:
		r = requests.get(url=url, headers=header).content.decode('latin-1')
		return BeautifulSoup(r, 'html.parser')
	except Exception:
		return None


def random_string(string_length=10):
	"""Generate a random string of fixed length """
	letters = string.ascii_letters
	return ''.join(random.choice(letters) for i in range(string_length))


cmus = remote.PyCmus()
status = cmus.get_status_dict()

cache_folder = pathlib.PosixPath("~/.music_art").expanduser().resolve()
cache_file = cache_folder / 'cache.json'

with open(str(cache_file), 'r') as f:
	cache = json.load(f)

if status['file'] in cache:
	print(cache[status['file']])
	exit()

albumImage = False
if 'tag' in status:
	tag = status['tag']
	if 'artist' in tag and 'title' in tag:
		artist = tag['artist']
		if 'album' in tag:
			album = tag['album']
			if album.lower() != 'collection':
				# Lets go download album art bois
				title = artist + ' ' + album + ' cover'
				albumImage = True
			else:
				title = artist + ' ' + tag['title']
		else:
			title = artist + ' ' + tag['title']
	else:
		if 'title' in tag:
			title = tag['title']
		else:
			title = None
else:
	title = None

if title is None:
	exit()

image_type = "Action"
query = urllib.parse.quote(title)
url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
header = {
	'User-Agent':
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
}
soup = get_soup(url, header)

if soup is None:
	exit()

ActualImages = []  # contains the link for Large original images, type of  image
for a in soup.find_all("div", {"class": "rg_meta"}):
	link, Type = json.loads(a.text)["ou"], json.loads(a.text)["ity"]
	ActualImages.append((link, Type))

for i, (img, Type) in enumerate(ActualImages[0:1]):
	img_data = requests.get(img, headers=header).content
	if albumImage:
		img_file = pathlib.Path(status['file']).parent / ('downloaded_cover.' + Type)
		with open(img_file, 'wb') as f:
			f.write(img_data)
		print(img_file)
	else:
		name = str(cache_folder / (random_string() + '.' + Type))
		with open(name, 'wb') as f:
			f.write(img_data)
		cache[status['file']] = name
		with open(str(cache_file), 'w') as f:
			json.dump(cache, f)
		print(name)
