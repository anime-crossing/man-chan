from fetcher.youtube import YoutubeApi

class Queue:

    def __init__(self) -> None:
        self.queue = []
        self.session_queue = []

    def add_song(self, song_name: str):
        res = YoutubeApi.search(song_name)
        self.queue.append(res[0])

    def remove_song(self):
        song = self.queue.pop(0)
        self.session_queue.append(song)

    def is_empty(self) -> bool:
        return len(self.queue) == 0
    
    def get_queue(self) -> list:
        return self.queue
    
    
