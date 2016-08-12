#!/usr/bin/python
import numpy as np
import socket, time, threading, sys
import subprocess

import argparse


class VideoClient( threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.done = False

    def setVideoPramaters(self, server, port):
        self.server, self.port = server, port

    def setDone (self) :
        self.done = True

        
    def run (self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.server, self.port))
        connection = clientSocket.makefile('rb')
        
        try:
            cmdline = [ 'mplayer', '-benchmark', '-fps' , '31', '-cache' , '1024','-' ]
            player = subprocess.Popen(cmdline, stdin= subprocess.PIPE )
            while not self.done :
                data = connection.read(1024)
                if not data:
                    break
                player.stdin.write(data)
        finally:
            connection.close()
            clientSocket.close()
            player.terminate()

  




