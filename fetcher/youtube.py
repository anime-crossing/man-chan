from typing import Any

from yt_dlp import YoutubeDL

from models import Song


class YoutubeApi:
    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True" ,'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],}

    @classmethod
    def search(cls, query: str, limit=1) -> list[Song]:
        results: Any = YoutubeDL(cls.YDL_OPTIONS).extract_info(
            "ytsearch%d:%s" % (limit, query), download=False
        )
        songs = []
        for entry in results["entries"]:
            song = Song(
                entry["title"], entry["url"], entry["thumbnail"], entry["webpage_url"]
            )
            songs.append(song)
        return songs
