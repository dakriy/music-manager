#!/usr/bin/python

import pyautogui
import tkinter as tk
import youtube_dl
import pathlib
import eyed3


class MyFirstGUI:
	def __init__(self, master):
		self.master = master
		master.title('Download youtube video')

		self.label = tk.Label(master, text='Download song from the red tubes')
		self.label.grid(row=0, columnspan=2)
		self.artist_lbl = tk.Label(master, text='Artist').grid(row=1)
		self.title_lbl = tk.Label(master, text='Title').grid(row=2)
		self.album_lbl = tk.Label(master, text='Album').grid(row=3)
		self.artist = tk.Entry(master)
		self.title = tk.Entry(master)
		self.album = tk.Entry(master)
		self.artist.grid(row=1, column=1)
		self.title.grid(row=2, column=1)
		self.album.grid(row=3, column=1)
		self.download = tk.Button(master, text='Download', command=self.download_callback).grid(row=4, column=0)
		self.cancel = tk.Button(master, text='Cancel', command=self.cancel_callback).grid(row=4, column=1)
		self.go = False
		self.artist_txt = ''
		self.title_txt = ''
		self.album_txt = ''

	def cancel_callback(self):
		self.go = False
		self.master.destroy()

	def download_callback(self):
		self.go = True
		self.artist_txt = self.artist.get()
		self.title_txt = self.title.get()
		self.album_txt = self.album.get()
		self.master.destroy()

	def set_artist(self, text):
		self.artist.delete(0, tk.END)
		self.artist.insert(0, text)

	def set_title(self, text):
		self.title.delete(0, tk.END)
		self.title.insert(0, text)

	def set_album(self, text):
		self.album.delete(0, tk.END)
		self.album.insert(0, text)


# class MyLogger(object):
# 	def debug(self, msg):
# 		pass
#
# 	def warning(self, msg):
# 		pass
#
# 	def error(self, msg):
# 		print('ERROR: ' + str(msg))
#
#
# def my_hook(d):
# 	if d['status'] == 'finished':
# 		print('Done downloading, now converting ...')

# Bring up my workspace that has my youtube on it
pyautogui.hotkey('winleft', '0')
# switch to the first tab
pyautogui.hotkey('alt', '1')
# Select the URL bar
pyautogui.hotkey('ctrl', 'l')

root = tk.Tk()
root.withdraw()

# Copy url
pyautogui.hotkey('ctrl', 'c')

url = root.clipboard_get()

ydl_meta_opts = {
	'socket_timeout': 1
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

gui = MyFirstGUI(root)
gui.set_artist(artist)
gui.set_title(title)
root.attributes('-type', 'dialog')
root.deiconify()

root.mainloop()

# Switch back to the empty tab
pyautogui.hotkey('alt', '2')

# We need these
if not gui.go or not gui.artist_txt or not gui.title_txt:
	exit()

path_prefix = pathlib.PosixPath('~/music').expanduser()
# Now determine output location
if gui.album_txt:
	path = path_prefix / gui.artist_txt / gui.album_txt
else:
	path = path_prefix / gui.artist_txt

path = path.resolve()

if not path.exists():
	path.mkdir(mode=0o750, parents=True)

file_name = gui.artist_txt + ' - ' + gui.title_txt

ydl_opts = {
	'format': 'bestaudio/best',
	'postprocessors': [{
		'key': 'FFmpegExtractAudio',
		'preferredcodec': 'mp3',
		'preferredquality': '192',
	}],
	'outtmpl': str(path) + '/' + file_name + '.%(ext)s',
	'socket_timeout': 1
	# 'logger': MyLogger(),
	# 'progress_hooks': [my_hook],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
	ydl.download([video_url])

filename = str(path) + '/' + file_name + '.mp3'

# Ok now we set the tags
audio = eyed3.load(filename)
audio.tag.artist = gui.artist_txt
audio.tag.title = gui.title_txt
if gui.album_txt:
	audio.tag.album = gui.album_txt
	audio.tag.album_artist = gui.artist_txt

audio.tag.save()
