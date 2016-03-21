
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread
import clib

config = json.loads(open('config/config-local.json', 'r').read())
WIDTH = 640
HEIGHT = 480
CHANNELS = {'r': 0, 'g': 1, 'b': 2}

devices = json.loads(urllib2.urlopen(config['server_url']+'/get_config').read())
state = devices[int(sys.argv[1])]
print state

folder = sys.argv[2]
pics = []

for dirname, subdirs, files in os.walk(folder):
	for fname in files:
		pics.append(os.path.join(dirname, fname))

for file in pics:
	print 'reading '+file

	f = open(file, 'rb')
	tags = exifread.process_file(f)
	f.close()
	exif_date = datetime.datetime.strftime(
		datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S'), 
	'%Y-%m-%d %H:%M:%S')
	exif_lat = tags['GPS GPSLatitude'] if 'GPS GPSLatitude' in tags else ''
	exif_long = tags['GPS GPSLongitude'] if 'GPS GPSLongitude' in tags else ''

	im = Image.open(file)
	result = []

	for r in state['regions']:
		mask = Image.new('1', im.size)
		draw = ImageDraw.Draw(mask)
		channel = CHANNELS[ r['channel'] ]
		r = {'x': int(r['x']), 'y': int(r['y']), 'w': int(r['w']), 'h': int(r['h'])}
		draw.rectangle([
			clib.getCoordinate(im, r['x'], r['y']), 
			clib.getCoordinate(im, r['x']+r['w'], r['y']+r['h'])
		], fill=255)

		data = ImageStat.Stat(im, mask).mean
		# select channel
		result.append( data[channel] )

	im = im.resize((WIDTH, HEIGHT))

	jpeg_image_buffer = cStringIO.StringIO()
	#im.save(jpeg_image_buffer, format="PNG")
	im.save(jpeg_image_buffer, format="JPEG")
	image_string = base64.b64encode(jpeg_image_buffer.getvalue())

	print result

	post_data = {
		'image_data': result,
		'image_string': image_string,
		'date': exif_date,
		'lat': str(exif_lat),
		'long': str(exif_long),
	}

	urllib2.urlopen(config['server_url']+'/add_report', urllib.urlencode(post_data)).read()
