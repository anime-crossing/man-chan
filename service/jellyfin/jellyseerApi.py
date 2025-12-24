import requests 
from dataclasses import dataclass
from enum import Enum
from urllib.parse import quote

class Quality(Enum):
    ANY = 1
    SD = 2
    HD720 = 3
    HD1080 = 4
    ULTRAHD = 5
    HD720_1080 = 6


@dataclass
class Result:
    id: int
    mediaType: str
    posterPath: str
    overview: str


@dataclass
class MovieResult(Result):
   title:  str
   releaseDate: str
        
@dataclass
class TvResult(Result):
   name:  str
   firstAirDate: str

class JellySeerApi:




    # api_key = "MTc2MjkyNDM0NzcxOWQzNTlmOTVjLTVlYmQtNDhhZC05YTE1LTAwMjg2NDJkZTA5Zg=="
    # api_key = 
    # jellyfin_base_url = "https://jellyseer.manuelgavino.com"
    # root_folder_movie = "/data/media/Movies"
    # root_folder_tv = "/data/media/Shows"

    def __init__(self, api_key: str, base_url: str, root_folder_movie: str, root_folder_tv: str):
        self.api_key = api_key
        self.jellyfin_base_url = base_url
        self.root_folder_movie = root_folder_movie
        self.root_folder_tv = root_folder_tv

        self.headers = {
            "X-Api-Key": f"{self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def search(self, query: str) -> list[Result]:
        params = {"query": quote(query), "page": "1", "language": "en"}
        response = requests.get(f"{self.jellyfin_base_url}/api/v1/search", headers=self.headers, params=params)
        a =  response.json()
        results: list = []
        for c in a["results"]:
            if c["mediaType"] == "movie":
                movie = MovieResult(c["id"], c["mediaType"], f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{c['posterPath']}",c["overview"], c["title"], c["releaseDate"])
                results.append(movie)
            if c["mediaType"] == "tv":
                tv = TvResult(c["id"], c["mediaType"],f"https://image.tmdb.org/t/p/w600_and_h900_bestv2/{c['posterPath']}",c["overview"], c["name"], c["firstAirDate"])
                results.append(tv)
        return results
    
    def printResult(self, res: Result):
        if(isinstance(res, MovieResult)):
            print(f"{res.id}. {res.title} - {res.releaseDate} - Movie")
        if(isinstance(res, TvResult)):
            print(f"{res.id}. {res.name} - {res.firstAirDate} - Tv")

    def createRequest(self, res: Result):
        # params = {"query": query, "page": "1", "language": "en"}
        folder = self.root_folder_movie if isinstance(res, MovieResult) else self.root_folder_tv
        params = {
            "mediaId": res.id,
            "mediaType": "movie",
            "profileId": Quality.HD720_1080.value,
            "rootFolder": folder,
            "userId":1
        }
        response = requests.post(f"{self.jellyfin_base_url}/api/v1/request", headers=self.headers, json=params)
        return response.status_code 
