
# -*- coding: utf-8 -*-
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread
import clib

config = json.loads(open('config/config.json', 'r').read())

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
	lat, lon, exif_date = clib.getLatLonDate(file)
	image_data, image_string = clib.getRegionsData(file, state['regions'])
	print image_data

	post_data = {
		'image_data': image_data,
		'image_string': image_string,
		'date': exif_date,
		'lat': str(lat),
		'lon': str(lon),
		'deviceId': deviceId,
	}

	urllib2.urlopen(config['local_server_url']+'/add_report', urllib.urlencode(post_data)).read()
