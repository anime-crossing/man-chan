from re import L
from discord import Client
import json

class MainClient(Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message):
        print(f"Message from {message.author}: {message.content}")


configs = json.load(open("./configs.json"))

client = MainClient()
client.run(configs["token"])
