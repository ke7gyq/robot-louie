#!/usr/bin/python
import numpy as np
import cv2 
import socket, time, threading, sys
import subprocess

import argparse


class VideoClient( threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def setVideoPramaters(self, server, port):
        self.server, self.port = server, port
        
    def run (self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((self.server, self.port))
        connection = clientSocket.makefile('rb')
        
        try:
            cmdline = [ 'mplayer', '-benchmark', '-fps' , '31', '-cache' , '1024','-' ]
            player = subprocess.Popen(cmdline, stdin= subprocess.PIPE )
            while True:
                data = connection.read(1024)
                if not data:
                    break
                player.stdin.write(data)
        finally:
            connection.close()
            clientSocket.close()
            player.terminate()

  



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Display Video Client")
    parser.add_argument('--ipaddress', help="Robot host name", default = 'happy.local')
    parser.add_argument('--port', help = "Port Number", type=int, default ='8000')
    args = parser.parse_args()

    vc = VideoClient()
    vc.setVideoPramaters (args.ipaddress, args.port)
    vc.start()
    vc.join()




