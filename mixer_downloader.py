# Usage: Download live stream in Mixer under one topic in batch.
#        You can also adapt it easily to other live stream site
#        with some basic knowledge in `selenium`.
#        When a stream is finished, auto check and correction for
#        recorded video will be performed, and the corrected video
#        file will be saved in $root_path/processed.
#        Some examples of the starting url:
#        https://mixer.com/
#        https://mixer.com/browse/games/70323/fortnite
#        https://mixer.com/browse/games/14580/overwatch
# Author: Zhongyang Zhang
# E-mail: mirakuruyoo@gmail.com

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import argparse
import multiprocessing
import os
import time
import subprocess
import datetime
from pathlib2 import Path

REFRESH_TIME = 15
TIMEOUT_FIRST = 5
TIMEOUT_SCROLL = 3


class Timer(object):
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.t_start = time.time()

    def __exit__(self, type, value, traceback):
        print("==> [%s]:\t" % self.name, end="")
        self.time_elapsed = time.time() - self.t_start
        print("Elapsed Time: %s (s)" % self.time_elapsed)


def log(*snippets, end=None):
    if end is None:
        print(time.strftime("==> [%Y-%m-%d %H:%M:%S]", time.localtime()
                            ) + " " + "".join([str(s) for s in snippets]))
    else:
        print(time.strftime("==> [%Y-%m-%d %H:%M:%S]", time.localtime()) + " " + "".join([str(s) for s in snippets]),
              end=end)


def correct_rest_videos():
    video_paths = [i for i in list(
        (args.root_path/"raw").iterdir()) if i.is_file() and not i.name.startswith(".")]
    for video_path in video_paths:
        check_video(video_path)

def check_video(video_path):
    video_path = Path(video_path)
    processed_video_path = Path(
        *video_path.parts[:-2], "processed", video_path.name)
    if(os.path.exists(video_path) is True):
        try:
            with Timer(video_path.name+" check"):
                subprocess.call(["ffmpeg", '-err_detect', 'ignore_err', '-i', video_path,
                                 '-c', 'copy', processed_video_path])
                os.remove(str(video_path))
        except Exception as e:
            log(e)
    else:
        log("Skip fixing. File not found.")
    log("Fixing of video " + video_path.name +
        " is done. Going back to checking..")


def mixer_recorder(streamer_name):
    # start streamlink process
    recorded_filename = args.root_path/"raw" / \
        (streamer_name+"_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".mp4")
    with Timer(recorded_filename.name+" download"):
        subprocess.run(["streamlink", "https://mixer.com/" +
                        streamer_name, args.quality, "-o", recorded_filename])

    log("Recording stream " + recorded_filename.name +
        " is done. Fixing video file.")
    check_video(recorded_filename)
    return args.root_path/"processed"/recorded_filename.name


def analyze_mixer_page(url):
    driver = webdriver.Chrome()
    driver.get(url)
    element_present = EC.presence_of_element_located(
        (By.TAG_NAME, 'b-simple-browse-card'))
    WebDriverWait(driver, TIMEOUT_FIRST).until(element_present)
    for i in range(args.scroll_page_num):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(TIMEOUT_SCROLL)
    time.sleep(TIMEOUT_FIRST)
    elems = driver.find_elements_by_tag_name("b-simple-browse-card")
    streamer_names = [i.find_element_by_tag_name(
        "a").get_attribute("href").split("/")[-1] for i in elems]
    driver.close()
    return streamer_names


def main(url):
    correct_rest_videos()
    streamer_names = analyze_mixer_page(url)
    p = multiprocessing.Pool()
    result = p.map(mixer_recorder, streamer_names[:args.max_record_num])
    log(str(len(result)), "Videos has been successfully recorded! Thanks for using.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
      	'Welcome to mixer downloader! Please input a starting url to parse using --url')

    # String
    parser.add_argument(
        '--url',
        type=str,
        default="https://mixer.com/browse/games/70323/fortnite",
        help='The url of the starting page.')

    parser.add_argument(
        '--root_path',
        type=str,
        default="./Data/Mixer_Videos/",
        help='The root path of recorded videos.')

    parser.add_argument(
        '--quality',
        type=str,
        default="best",
        help='The quality of recorded videos.')

    # Integer
    parser.add_argument(
        '--max_record_num',
        type=int,
        default='5',
        help='The maximum value of records.')

    parser.add_argument(
        '--scroll_page_num',
        type=int,
        default='2',
        help='The number of pages you scrolls down.')

    args = parser.parse_args()
    args.root_path = Path(args.root_path)

    if not args.root_path.exists():
        os.makedirs(str(args.root_path))
    if not (args.root_path/"raw").exists():
        os.makedirs(str((args.root_path/"raw")))
    if not (args.root_path/"processed").exists():
        os.makedirs(str((args.root_path/"processed")))

    main(args.url)
