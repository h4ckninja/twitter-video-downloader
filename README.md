Twitter Video Downloader
========================


A simple, if fragile, approach to downloading videos from Twitter. Twitter presents these video files as streams, so as to make it (un)intentionally difficult to just download videos.


Installation
============

Python3 is a **must**.

`pip install -r requirements.txt`.


Usage
=====

`twitter-video-downloader.py [-h] -v VIDEO_URL`


Output
======

A directory named `output` will be created, with the twitter username, followed by the tweet ID.

From there, the script will attempt to parse out the streams and download them. They will then be used to create a final file named `<resolution>.ts`. QuickTime has no problem opening this file. YMMV.
