
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread
import clib

config = json.loads(open('config/config.json', 'r').read())
WIDTH = 640
HEIGHT = 480
CHANNELS = {'r': 0, 'g': 1, 'b': 2}

devices = json.loads(urllib2.urlopen(config['local_server_url']+'/get_config').read())
state = devices[int(sys.argv[1])]
deviceId = state['_id']
print state

folder = sys.argv[2]
pics = []

for dirname, subdirs, files in os.walk(folder):
	for fname in files:
		pics.append(os.path.join(dirname, fname))

for file in pics:
	if 'DS_Store' in file:
		continue

	print 'reading '+file

	f = open(file, 'rb')
	tags = exifread.process_file(f)
	f.close()

	exif_date = datetime.datetime.strftime(
		datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S'), 
		'%Y-%m-%d %H:%M:%S'
	) if 'EXIF DateTimeOriginal' in tags else datetime.datetime.now()

	exif_lat = tags['GPS GPSLatitude'] if 'GPS GPSLatitude' in tags else ''
	exif_lat_ref = tags['GPS GPSLatitudeRef'] if 'GPS GPSLatitudeRef' in tags else ''
	exif_lon = tags['GPS GPSLongitude'] if 'GPS GPSLongitude' in tags else ''
	exif_lon_ref = tags['GPS GPSLongitudeRef'] if 'GPS GPSLongitudeRef' in tags else ''

	lat, lon = clib.getLatLon(exif_lat, exif_lat_ref, exif_lon, exif_lon_ref)

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
		'lat': str(lat),
		'lon': str(lon),
		'deviceId': deviceId,
	}

	urllib2.urlopen(config['local_server_url']+'/add_report', urllib.urlencode(post_data)).read()
