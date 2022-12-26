#!/usr/bin/python3.9
import os, sys, json, hashlib, base64, cgi, cgitb


sys.stdout.write(b'Content-Type: application/octet-stream\r\n')
sys.stdout.write(b'Content-Disposition: attachment; filename="bigfile.mp4"\r\n')
sys.stdout.write(b'X-Sendfile: /home/basket/scottish_handshake/db/20181225_182650.ts\r\n\r\n')
