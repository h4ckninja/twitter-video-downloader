#!/usr/bin/env python


import argparse

import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import m3u8
from pathlib import Path
import re
import ffmpeg
import shutil


class TwitterDownloader:
	"""
	tw-dl offers the ability to download videos from Twitter feeds.

	**Disclaimer** I wrote this to recover a video for which the original was lost. Consider copyright before downloading
	content you do not own.
	"""
	video_player_prefix = 'https://twitter.com/i/videos/tweet/'
	video_api = 'https://api.twitter.com/1.1/videos/tweet/config/'
	tweet_data = {}

	def __init__(self, tweet_url, output_dir = './output', debug = 0):
		self.tweet_url = tweet_url
		self.output_dir = output_dir
		self.debug = debug

		if debug > 2:
			self.debug = 2

		"""
		We split on ? to clean up the URL. Sharing tweets, for example, 
		will add ? with data about which device shared it.
		The rest is just getting the user and ID to work with.
		"""
		self.tweet_data['tweet_url'] = tweet_url.split('?', 1)[0]
		self.tweet_data['user'] = self.tweet_data['tweet_url'].split('/')[3]
		self.tweet_data['id'] = self.tweet_data['tweet_url'].split('/')[5]

		output_path = Path(output_dir)
		storage_dir = output_path / self.tweet_data['user'] / self.tweet_data['id']
		Path.mkdir(storage_dir, parents = True, exist_ok = True)
		self.storage = str(storage_dir)

		self.requests = requests.Session()

	def download(self):
		self.__debug('Tweet URL', self.tweet_data['tweet_url'])

		# Get the bearer token
		token = self.__get_bearer_token()

		# Get the M3u8 file - this is where rate limiting has been happening
		video_host, playlist = self.__get_playlist(token)

		if playlist.is_variant:
			print('[+] Multiple resolutions found. Slurping all resolutions.')

			for plist in playlist.playlists:
				resolution = str(plist.stream_info.resolution[0]) + 'x' + str(plist.stream_info.resolution[1])
				resolution_file = Path(self.storage) / Path(resolution + '.mp4')

				print('[+] Downloading ' + resolution)

				playlist_url = video_host + plist.uri

				ts_m3u8_response = self.requests.get(playlist_url, headers = {'Authorization': None})
				ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

				ts_list = []
				ts_full_file_list = []

				for ts_uri in ts_m3u8_parse.segments.uri:
					# ts_list.append(video_host + ts_uri)

					ts_file = requests.get(video_host + ts_uri)
					fname = ts_uri.split('/')[-1]
					ts_path = Path(self.storage) / Path(fname)
					ts_list.append(ts_path)

					ts_path.write_bytes(ts_file.content)

				ts_full_file = Path(self.storage) / Path(resolution + '.ts')
				ts_full_file = str(ts_full_file)
				ts_full_file_list.append(ts_full_file)

				# Shamelessly taken from https://stackoverflow.com/questions/13613336/python-concatenate-text-files/27077437#27077437
				with open(str(ts_full_file), 'wb') as wfd:
					for f in ts_list:
						with open(f, 'rb') as fd:
							shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)


				for ts in ts_full_file_list:
					print('\t[*] Doing the magic ...')
					ffmpeg\
						.input(ts)\
						.output(str(resolution_file), acodec = 'copy', vcodec = 'libx264', format = 'mp4', loglevel = 'error')\
						.overwrite_output()\
						.run()

				print('\t[+] Doing cleanup')

				for ts in ts_list:
					p = Path(ts)
					p.unlink()

				for ts in ts_full_file_list:
					p = Path(ts)
					p.unlink()

		else:
			print('[-] Sorry, single resolution video download is not yet implemented. Please submit a bug report with the link to the tweet.')


	def __get_bearer_token(self):
		video_player_url = self.video_player_prefix + self.tweet_data['id']
		video_player_response = self.requests.get(video_player_url)
		self.__debug('Video Player Body', '', video_player_response.text)

		js_file_soup = BeautifulSoup(video_player_response.text, 'html.parser')
		js_file_url = js_file_soup.find('script')['src']
		js_file_response = self.requests.get(js_file_url)
		self.__debug('JS File Body', '', js_file_response.text)

		bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
		bearer_token = bearer_token_pattern.search(js_file_response.text)
		bearer_token = bearer_token.group(0)
		self.requests.headers.update({'Authorization': bearer_token})
		self.__debug('Bearer Token', bearer_token)
		self.__get_guest_token()

		return bearer_token


	def __get_playlist(self, token):
		player_config_req = self.requests.get(self.video_api + self.tweet_data['id'] + '.json')

		player_config = json.loads(player_config_req.text)

		if 'errors' not in player_config:
			self.__debug('Player Config JSON', '', json.dumps(player_config))
			m3u8_url = player_config['track']['playbackUrl']

		else:
			self.__debug('Player Config JSON - Error', json.dumps(player_config['errors']))
			print('[-] Rate limit exceeded. Could not recover. Try again later.')
			sys.exit(1)

		# Get m3u8
		m3u8_response = self.requests.get(m3u8_url)
		self.__debug('M3U8 Response', '', m3u8_response.text)

		m3u8_url_parse = urllib.parse.urlparse(m3u8_url)
		video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname

		m3u8_parse = m3u8.loads(m3u8_response.text)

		return [video_host, m3u8_parse]


	"""
	Thanks to @devkarim for this fix: https://github.com/h4ckninja/twitter-video-downloader/issues/2#issuecomment-538773026
	"""
	def __get_guest_token(self):
		res = self.requests.post("https://api.twitter.com/1.1/guest/activate.json")
		res_json = json.loads(res.text)
		self.requests.headers.update({'x-guest-token': res_json.get('guest_token')})


	def __debug(self, msg_prefix, msg_body, msg_body_full = ''):
		if self.debug == 0:
			return

		if self.debug == 1:
			print('[Debug] ' + '[' + msg_prefix + ']' + ' ' + msg_body)

		if self.debug == 2:
			print('[Debug+] ' + '[' + msg_prefix + ']' + ' ' + msg_body + ' - ' + msg_body_full)


if __name__ == '__main__':
	import sys

	if sys.version_info[0] == 2:
		print('Python3 is required.')
		sys.exit(1)

	parser = argparse.ArgumentParser()
	parser.add_argument('tweet_url', help = 'The video URL on Twitter (https://twitter.com/<user>/status/<id>).')
	parser.add_argument('-o', '--output', dest = 'output', default = './output', help = 'The directory to output to. The structure will be: <output>/<user>/<id>.')
	parser.add_argument('-d', '--debug', default = 0, action = 'count', dest = 'debug', help = 'Debug. Add more to print out response bodies (maximum 2).')

	args = parser.parse_args()

	twitter_dl = TwitterDownloader(args.tweet_url, args.output, args.debug)
	twitter_dl.download()
