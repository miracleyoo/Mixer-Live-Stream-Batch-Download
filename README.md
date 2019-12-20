# Mixer-Live-Stream-Batch-Download

A python script to download the first N(customizable)  live streams in batch and at the same time from site Mixer.com . Also, auto correction will be applied after the download finished.

## Features

- Live stream download in Mixer(also possible for other live site if you know some `selenium`).
- Automatic parsing for the inputed starting page, like "https://mixer.com/", "https://mixer.com/browse/games/70323/fortnite"
- Multi-thread and simultaneous download for all these extracted live stream.
- Auto correction for the downloaded live stream video files.
- Exit automatically after the end of all live streams downloading.
- Exit at any time using `Ctrl+C` and the un-corrected files will be corrected in the beginning of the next run of the script.

## Usage

Just run: `python mixer_downloader.py --url="https://mixer.com/browse/games/70323/fortnite" --max_record_num=10 --scroll_page_num=10 --quality="best"`

Please run `python mixer_downloader.py -h` for more detailed information of parameters.

## Prerequisite

- selenium
- chromedriver for selenium
- streamlink
- ffmpeg

Please install these prerequisite before you run this program.

## Basic Workflow

1. Use selenium to fully load the page of the input url, and get every streamer name for downloading.
2. Use multiprocess to start multiple thread to download these live stream video simultaneously.
3. After the end of each download process, an auto correction of the downloaded video file will be performed, since the video file may have many error due to the network environment variation or sudden stop.
4. Wait until every download thread finishes or manually stop by press `Ctrl+C`.
