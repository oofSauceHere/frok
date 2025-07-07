#!/usr/bin/env python

import sys
from websockets.sync.client import connect

def hello():
    msg = input("Enter message: ")
    with connect("ws://192.168.1.28:8765") as websocket:
        websocket.send(msg)
        message = websocket.recv()
        print(f"Received: {message}")

hello()