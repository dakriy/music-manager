#!/usr/bin/python

import pyautogui
import tkinter as tk
import youtube_dl
import pathlib
import eyed3
from typing import Dict


class InformationGUI:
	LABEL_INDEX = 0
	ENTRY_INDEX = 1
	TEXT_INDEX = 2

	def __init__(self, master, attributes: Dict[str, str], clippy):
		self.master = master
		master.clipboard_clear()
		if clippy:
			master.clipboard_append(clippy)
			master.update()
		master.title('Download youtube video')

		# Bindings go [label, entry, text holder]
		self.bindings = {
			'heading': [
				tk.Label(master, text='Download song from the red tubes'),
				None,
				''
			]
		}
		self.bindings['heading'][InformationGUI.LABEL_INDEX].grid(row=0, columnspan=2)
		row = 1
		for key, value in attributes.items():
			self.bindings[key] = [
				tk.Label(master, text=value),
				tk.Entry(master),
				''
			]
			self.bindings[key][InformationGUI.LABEL_INDEX].grid(row=row, column=0)
			self.bindings[key][InformationGUI.ENTRY_INDEX].grid(row=row, column=1)
			row += 1

		self.download = tk.Button(master, text='Download', command=self.download_callback)
		self.download.grid(row=row, column=0)
		self.cancel = tk.Button(master, text='Cancel', command=self.cancel_callback)
		self.cancel.grid(row=row, column=1)
		self.go = False

	def cancel_callback(self):
		self.go = False
		self.master.destroy()

	def download_callback(self):
		self.go = True
		for key, binding_arr in self.bindings.items():
			if key == 'heading':
				continue
			binding_arr[InformationGUI.TEXT_INDEX] = binding_arr[InformationGUI.ENTRY_INDEX].get()
		self.master.destroy()

	def set_attr(self, attr, text):
		self.bindings[attr][InformationGUI.ENTRY_INDEX].delete(0, tk.END)
		self.bindings[attr][InformationGUI.ENTRY_INDEX].insert(0, text)

	def get_attr(self, attr):
		return self.bindings[attr][InformationGUI.TEXT_INDEX]


# Bring up my workspace that has my youtube on it
pyautogui.hotkey('winleft', '0')
# switch to the first tab
pyautogui.hotkey('alt', '1')
# Select the URL bar
pyautogui.hotkey('ctrl', 'l')

root = tk.Tk()
root.withdraw()

# Save previous clipboard
try:
	prev_clip_board = root.clipboard_get()
except tk.TclError:
	prev_clip_board = None

# Copy url
pyautogui.hotkey('ctrl', 'c')

url = root.clipboard_get()

ydl_meta_opts = {
	'socket_timeout': 1,
	'noplaylist': 1
}
with youtube_dl.YoutubeDL(ydl_meta_opts) as ydl:
	ydl.add_default_info_extractors()
	info_dict = ydl.extract_info(url, download=False)

if 'entries' in info_dict:
	video = info_dict['entries'][0]
else:
	video = info_dict
# Now we extract the information we want
parts = video['title'].split(' - ')
if len(parts) > 1:
	artist = parts[0]
	# Don't care about things in parentheses bracket and everything after a slash
	title = parts[1].split('(')[0].strip().split('[')[0].strip().split('/')[0].strip()
else:
	artist = video['uploader']
	title = video['title']
video_id = video['id']
video_url = 'https://youtube.com/watch?v=' + video_id

gui = InformationGUI(root, {
	'artist': 'Artist',
	'title': 'Title',
	'album': 'Album',
	'album_artist': 'Album Artist',
	'track_number': 'Track Number'
}, prev_clip_board)
gui.set_attr('artist', artist)
gui.set_attr('title', title)
root.attributes('-type', 'dialog')
root.deiconify()

root.mainloop()

# Switch back to the empty tab
pyautogui.hotkey('alt', '2')

# We need these
entered_artist = gui.get_attr('artist')
entered_title = gui.get_attr('title')
if not gui.go or not entered_artist or not entered_title:
	exit()

path_prefix = pathlib.PosixPath('~/music').expanduser()
# Now determine output location
entered_album = gui.get_attr('album')
if entered_album:
	path = path_prefix / entered_artist / entered_album
else:
	path = path_prefix / entered_artist

path = path.resolve()

if not path.exists():
	path.mkdir(mode=0o750, parents=True)

file_name = entered_artist + ' - ' + entered_title

ydl_opts = {
	'format': 'bestaudio/best',
	'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
	}],
	'outtmpl': str(path) + '/' + file_name + '.%(ext)s',
	'socket_timeout': 1
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	ydl.download([video_url])

filename = str(path) + '/' + file_name + '.mp3'

# Ok now we set the tags
audio = eyed3.load(filename)
audio.tag.artist = entered_artist
audio.tag.title = entered_title
if entered_album:
	album_artist = gui.get_attr('album_artist')
	track_number = gui.get_attr('track_number')
	audio.tag.album = entered_album
	if not album_artist:
		audio.tag.album_artist = entered_artist
	else:
		audio.tag.album_artist = album_artist

	if track_number:
		audio.tag.track_num = int(track_number)

audio.tag.save()
