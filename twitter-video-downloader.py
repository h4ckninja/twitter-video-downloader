#!/usr/bin/env python


import argparse
import shutil

import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import m3u8
from pathlib import Path
import re


def download(video_url):
	video_player_url_prefix = 'https://twitter.com/i/videos/tweet/'
	video_host = ''
	output_dir = './output'

	# Parse the tweet ID
	tweet_user = video_url.split('/')[3]
	tweet_id = video_url.split('/')[5]
	tweet_dir = Path(output_dir + '/' + tweet_user + '/' + tweet_id)
	Path.mkdir(tweet_dir, parents = True, exist_ok = True)

	# Grab the video client HTML
	video_player_url = video_player_url_prefix + tweet_id
	video_player_response = requests.get(video_player_url)

	# Get the JS file with the Bearer token to talk to the API.
	# Twitter really changed things up.
	js_file_soup = BeautifulSoup(video_player_response.text, 'html.parser')
	js_file_url = js_file_soup.find('script')['src']
	js_file_response = requests.get(js_file_url)

	# Pull the bearer token out
	bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
	bearer_token = bearer_token_pattern.search(js_file_response.text)
	bearer_token = bearer_token.group(0)

	# Talk to the API to get the m3u8 URL
	player_config = requests.get('https://api.twitter.com/1.1/videos/tweet/config/' + tweet_id + '.json', headers={'Authorization': bearer_token})
	m3u8_url_get = json.loads(player_config.text)
	m3u8_url_get = m3u8_url_get['track']['playbackUrl']

	# Get m3u8
	m3u8_response = requests.get(m3u8_url_get, headers = {'Authorization': bearer_token})

	m3u8_url_parse = urllib.parse.urlparse(m3u8_url_get)
	video_host = m3u8_url_parse.scheme + '://' + m3u8_url_parse.hostname

	m3u8_parse = m3u8.loads(m3u8_response.text)

	if m3u8_parse.is_variant:
		print('Multiple resolutions found. Slurping all resolutions.')

		for playlist in m3u8_parse.playlists:
			resolution = str(playlist.stream_info.resolution[0]) + 'x' + str(playlist.stream_info.resolution[1])
			resolution_dir = Path(tweet_dir) / Path(resolution)
			Path.mkdir(resolution_dir, parents = True, exist_ok = True)

			playlist_url = video_host + playlist.uri

			ts_m3u8_response = requests.get(playlist_url)
			ts_m3u8_parse = m3u8.loads(ts_m3u8_response.text)

			ts_list = []

			for ts_uri in ts_m3u8_parse.segments.uri:
				print('[+] Downloading ' + resolution)

				ts_file = requests.get(video_host + ts_uri)
				fname = ts_uri.split('/')[-1]
				ts_path = resolution_dir / Path(fname)
				ts_list.append(ts_path)

				ts_path.write_bytes(ts_file.content)


			ts_full_file = Path(resolution_dir) / Path(resolution + '.ts')

			# Shamelessly taken from https://stackoverflow.com/questions/13613336/python-concatenate-text-files/27077437#27077437
			with open(str(ts_full_file), 'wb') as wfd:
				for f in ts_list:
					with open(f, 'rb') as fd:
						shutil.copyfileobj(fd, wfd, 1024 * 1024 * 10)


if __name__ == '__main__':
	import sys

	if sys.version_info[0] == 2:
		print('Python3 is required.')
		sys.exit(1)

	parser = argparse.ArgumentParser()
	parser.add_argument('-v', '--video', dest='video_url', help='The video URL on Twitter (https://twitter.com/<user>/status/<id>).', required=True)

	args = parser.parse_args()

	download(args.video_url)
