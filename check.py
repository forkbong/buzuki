#!/usr/bin/env python3

import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import click
import requests
import youtube_dl
from mutagen.id3 import COMM, ID3

from buzuki import create_app
from buzuki.songs import Song
from buzuki.utils import unaccented

app = create_app("development")

EXECUTOR = ThreadPoolExecutor(max_workers=5)


def clear_metadata(filename):
    audio = ID3(filename)
    keys = list(audio.keys())
    if keys:
        for key in keys:
            audio.delall(key)
        audio.save()


def set_comment(filename, comment):
    audio = ID3(filename)
    audio.add(COMM(encoding=3, text=comment))
    audio.save()


def get_comment(filename):
    audio = ID3(filename)
    comments = audio.getall("COMM")
    if not comments:
        return
    return comments[0].text[0]


async def download(song):
    """Download `song`'s YouTube video and convert to mp3."""
    loop = asyncio.get_event_loop()

    filename = ""

    def download_hook(d):
        nonlocal filename
        if d["status"] == "finished":
            filename = d["filename"]
            print("Done downloading, now converting...")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "progress_hooks": [download_hook],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            await loop.run_in_executor(EXECUTOR, ydl.download, [song.link])
        except youtube_dl.DownloadError as e:
            print(click.style(f"Couldn't download {song.name}: {e}", fg="red"))
            return

    path = Path(filename).with_suffix(".mp3")
    path.rename(song.audio_path)
    set_comment(song.audio_path, song.youtube_id)


async def check_link(song):
    """Return whether `song`'s YouTube link is still valid."""
    loop = asyncio.get_event_loop()

    url = f"http://img.youtube.com/vi/{song.youtube_id}/mqdefault.jpg"
    try:
        future = loop.run_in_executor(EXECUTOR, requests.get, url)
        response = await future
        # response = requests.get(url)
    except requests.ConnectionError as e:
        sys.exit(e)
    if response.status_code != 200:
        return False
    return True


async def check_song(song):
    print(f"Checking song {song.name}")
    if song.youtube_id:
        if not await check_link(song):
            assert song.audio_path.is_file()
            print(click.style(f"{song.name} has invalid youtube id", fg="red"))
        elif song.audio_path.is_file():
            youtube_id = get_comment(song.audio_path)
            if song.youtube_id != youtube_id:
                print(f"{song.youtube_id} != {youtube_id}")
                if click.confirm("Replace?"):
                    song.audio_path.unlink()
                    print(f"Downloading {song.name}...")
                    await download(song)
                    print(f"Done downloading {song.name}")
            else:
                print(song.name, "is OK")
        else:
            print(f"Downloading {song.name}...")
            await download(song)
            print(f"Done downloading {song.name}")
    # else:
    #     assert song.audio_path.is_file()
    #     print(song.name, "has no youtube id but audio is downloaded")
    #     clear_metadata(song.audio_path)


async def check():
    """Check and fix audio files."""
    directory: Path = app.config["DIR"] / "songs"
    songs = [Song.get(path.name) for path in directory.iterdir()]
    songs.sort(key=lambda song: unaccented(song.name))
    num = len(songs)
    futures = []
    for i, song in enumerate(songs, start=1):
        print(f"{i}/{num}", end="\t")
        futures.append(check_song(song))

    await asyncio.gather(*futures)


if __name__ == "__main__":
    with app.app_context():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(check())
