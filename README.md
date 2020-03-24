[![ko-fi](https://www.ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/h4ckninja)

Twitter Video Downloader
========================

A simple, approach to downloading videos from Twitter. Twitter presents these video files as streams, so as to make it (un)intentionally difficult to just download videos.


Installation
============

Python3 is a **must**.

`pip install -r requirements.txt`.

You will also need [ffmpeg](https://ffmpeg.org/). Install for your operating system of choice. If you use the supplied Vagrant box, this will be taken care of for you.

Usage
=====

`twitter-dl.py [-hdow] VIDEO_URL`

`-d` or `--debug`: This will enable debugging output. Additional `-d` flags (up to 2) will increase debugging.

`-o` or `--output`: Change the output directory. The default is `output/`

`-w` or `--target_width`: In pixels. Download only the video resolution closest to this value. e.g. `-w 500`

`-h`: Help.

Vagrant
=======

Included is a `Vagrantfile` that will spin up a VM, pre-configured, to run the script. Outside of bugs for my `Vagrantfile`, no support is offered for vagrant.

Access the box and python will be available at `python3`.

### To get your files out

I like to use `python -m http.server`, or in this case, `python3 -m http.server`. I've opened up port 8000 on the box for this purpose.

Output
======

A directory named `output` (by default) will be created, with the twitter username, followed by the tweet ID.

From there, the script will attempt to parse out the streams and download them. You'll end up with a new .mp4 file for each resolution found.
