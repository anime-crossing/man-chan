from typing import Any

from yt_dlp import YoutubeDL

from models import Song
from urllib.parse import parse_qs, urlsplit, urlunsplit


class YoutubeApi:
    YDL_OPTIONS = {"format": "bestaudio", "noplaylist": "True" ,'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],}

    @classmethod
    def search(cls, query: str, limit=1) -> list[Song]:
        parsed_search = urlsplit(query)
        if (all([parsed_search.scheme, parsed_search.netloc])):
            queries = parse_qs(parsed_search.query)
            queries.pop('t', None)
            queries_url = "&".join(["{}={}".format(key, value[0]) for key, value in queries.items()])
            parsed_search = urlunsplit((parsed_search.scheme, parsed_search.netloc, parsed_search.path, queries_url, parsed_search.fragment))
        else:
            parsed_search = urlunsplit(parsed_search)
        results: Any = YoutubeDL(cls.YDL_OPTIONS).extract_info(
            "ytsearch%d:%s" % (limit, parsed_search), download=False
        )
        songs = []
        for entry in results["entries"]:
            song = Song(
                entry["title"], entry["url"], entry["thumbnail"], entry["webpage_url"]
            )
            songs.append(song)
        return songs
