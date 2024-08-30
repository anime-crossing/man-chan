from fetcher.youtube import YoutubeApi
from models import Song


class Queue:
    def __init__(self) -> None:
        self.queue: list[Song] = []
        self.session_history: list[Song] = []

    def add_song(self, song_name: str) -> None:
        songs = YoutubeApi.search(song_name)
        self.queue.append(songs[0])

    def remove_song(self) -> None:
        song = self.queue.pop(0)
        self.session_history.append(song)

    def is_queue_empty(self) -> bool:
        return len(self.queue) == 0

    def is_history_empty(self) -> bool:
        return len(self.session_history) == 0

    def queue_to_string(self) -> str:
        songs = ""
        for song in self.queue:
            songs += song.title + "\n"
        return songs

    def history_to_string(self) -> str:
        return "\n".join(map(lambda x: x.title, self.session_history))
