#!/usr/bin/python
'''
	Fork of ...
	By Vitaly.Burkut
	Move to Python3
	remove cv2
	add ffmpeg through child process

'''
#import cv2
import os
import ffmpeg

from PIL import Image
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer, ThreadingHTTPServer
from socketserver import ThreadingMixIn
#import StringIO
import time

ffmpeg_prc = None


import os
import ffmpeg

from memory_tempfile import MemoryTempfile
global tempfile


 
tempfile = MemoryTempfile().NamedTemporaryFile()


class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('.mjpg'):
			global ffmpeg_prc
			if 	not ffmpeg_prc or ffmpeg_prc.poll() != None:
				#yuyv422
				#mjpeg
				ffmpeg_prc =  (ffmpeg.input('/dev/video0', loglevel="error", format="v4l2", input_format="yuyv422", s='{}x{}'.format(1280, 960))
					.output( tempfile.name,  format="image2", r = "20",  qscale = "10", update="1").overwrite_output()
					#vf="fps=fps=25",
					.run_async())
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=jpgboundary')
			self.end_headers()
          

			while True:
				try:
					
					fd = None
					with open(tempfile.name, 'rb') as memFile:
						fd=memFile.read()

					#jpg = Image.fromarray(fd)



					self.wfile.write(b"\r\n--jpgboundary\r\n")
					self.send_header('Content-type','image/jpeg')
					self.send_header('Content-length',str(len(fd)))
					self.end_headers()
					self.wfile.write(fd)
					time.sleep(0.05)
				except KeyboardInterrupt:					
					break
					if ffmpeg_prc.is_alive():
						ffmpeg_prc.terminate()
						
			return
		if self.path.endswith('.html'):
			self.send_response(200)
			self.send_header('Content-type','text/html')
			self.end_headers()
			self.wfile.write(b'<html><head></head><body>')
			self.wfile.write(b'<img src="/cam.mjpg"/>')
			self.wfile.write(b'</body></html>')
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global capture
	#capture = cv2.VideoCapture(0)
	global img
	global ffmpeg_prc

	try:
		server = ThreadedHTTPServer(('0.0.0.0', 8090), CamHandler)
		print ("server started")
		server.serve_forever()
	except KeyboardInterrupt:
		#capture.release()
		server.socket.close()
		ffmpeg_prc.terminate()

if __name__ == '__main__':
	main()