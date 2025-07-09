import os

from discord import Intents, Client, MessageType
from discord.ext import tasks
from threading import Lock, Thread
import asyncio
from websockets.asyncio.server import serve
from websockets.exceptions import ConnectionClosed
from dotenv import load_dotenv
import json

# architecture:
# on post request, send message to bot and block until response is received
# OR store all waiting requests in hashmap with id and process as replied to

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

intents = Intents.default()
intents.message_content = True

client = Client(intents=intents)
MUTEX = Lock()

messages = dict() # map from message id to user state
questions = []

sockets = []

async def relay(websocket):
    global cnt

    try:
        async for message in websocket:
            print(f"[server] Received message: {message}")
            if not websocket in sockets:
                sockets.append(websocket)
            with MUTEX:
                questions.append((message, websocket))
    except ConnectionClosed as e:
        print("[server] Unable to process message; Connection was closed.")

async def server():
    print("[server] Starting echo server...")
    async with serve(relay, "192.168.1.28", 8765) as server:
        await server.serve_forever()

# BOT METHODS
# use bot or cog instead?

@client.event
async def on_ready():
    print(f"[bot] Logged in as {client.user}")
    channel = client.get_channel(1391275468027858997)
    await channel.send("Restarted! Session ids restart from 0.")
    poll_questions.start() # start here or elsewhere?

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.type != MessageType.reply and (message.content == "REVEAL DOG." or message.content == "REVEAL FRED."):
        for websocket in sockets:
            try:
                if message.content == "REVEAL DOG.":
                    await websocket.send(json.dumps({
                        "form": "command",
                        "message": "dog"
                    }))
                elif message.content == "REVEAL FRED.":
                    await websocket.send(json.dumps({
                        "form": "command",
                        "message": "fred"
                    }))
                print("[server] Sent reveal command.")
            except ConnectionClosed as e:
                print("[server] Unable to send message; Connection was closed.")

    if message.type == MessageType.reply and message.reference.message_id in messages:
        print("[bot] Valid reply received.")
        # with mutex, pop from messages map and process

        socket = messages[message.reference.message_id]
        try:
            await socket.send(json.dumps({
                "form": "content",
                "message": message.content
            }))
        except ConnectionClosed as e:
            print("[server] Unable to send message; Connection was closed.")
        del messages[message.reference.message_id]

@tasks.loop(seconds=5)
async def poll_questions():
    channel = client.get_channel(1391275468027858997)
    with MUTEX: # no 'async' - is this okay?
        for (q, w) in questions:
            msg = await channel.send(f"[{sockets.index(w)}] {q}")
            messages[msg.id] = w
        questions.clear()

if __name__ == '__main__':
    def bot():
        client.run(TOKEN)
    t = Thread(target=bot)
    t.start()
    
    asyncio.run(server())
    
    t.join()