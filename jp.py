import re
import json
import requests

with open("test_phrase.txt") as file:
    conts = file.read()

    match = re.search(r"data-wordday=(.+)data-hintmode", conts).group(1)

    match = match.strip().strip('[]"')
    match = re.sub('&quot;', '"', match)
    

    match = json.loads(match)





    print(match)

    print(f"Japanese Text: {match['text']}")
    print(f"Image: {match['image_url']}")
    print(f"Answer: {match['english']}")
    print(f"Definition: {match['meaning']}")
    print(f"Kana: {match['kana']}")
    print(f"Romanization: {match['romanization']}")


# response = requests.get("https://www.japanesepod101.com/japanese-phrases/",
#                 headers = {
#                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#                 "Accept-Encoding": "gzip, deflate, zstd",
#                 "Connection": "keep-alive",
#                 "Host": "www.japanesepod101.com",
#                 "Referer": "https://www.google.com/",
#                 "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
#                 })

# print(response.content)