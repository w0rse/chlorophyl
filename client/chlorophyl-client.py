
# -*- coding: utf-8 -*-
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread
import clib

config = json.loads(open('config/config.json', 'r').read())
HOW_MANY = 1

# find any new cameras
# subprocess.Popen(['C:\devcon\devcon.exe', 'rescan'], shell=True)

# time.sleep(20)

devices = json.loads(urllib2.urlopen(config['local_server_url']+'/get_config').read())
state = devices[int(sys.argv[1])]
deviceName = state['deviceName']
print state

def getImageData():

	clib.shoot()

	max_mtime = 0
	for dirname, subdirs, files in os.walk("../pictures"):
		for fname in files:
			full_path = os.path.join(dirname, fname)
			mtime = os.stat(full_path).st_mtime
			if mtime > max_mtime and fname not in ['.DS_Store']:
				max_mtime = mtime
				max_file = full_path

	print 'reading '+max_file
	lat, lon, exif_date = clib.getLatLonDate(max_file)
	image_data, image_string = clib.getRegionsData(max_file, state['regions'], delete=config['delete_source_file'])
	print image_data

	return {
		'image_data': image_data,
		'image_string': image_string,
		'date': exif_date,
		'lat': str(lat),
		'lon': str(lon),
	}


post_data = {
	'image_data': [0] * len(state['regions'])
}

for i in range(0, HOW_MANY):
	image_data = getImageData()
	post_data['image_string'] = image_data['image_string']
	post_data['lat'] = image_data['lat']
	post_data['lon'] = image_data['lon']
	post_data['date'] = image_data['date']
	post_data['image_data'] = [post_data['image_data'][j] + image_data['image_data'][j] for j in range(len(state['regions']))]

post_data['image_data'] = [x / HOW_MANY for x in post_data['image_data']]
post_data['deviceName'] = deviceName

urllib2.urlopen(config['local_server_url']+'/add_report', urllib.urlencode(post_data)).read()

with open(config['local_file'], 'a') as f:
	f.write(json.dumps(post_data['image_data']) + '\n')

try:
	urllib2.urlopen(config['remote_server_url']+'/add_report', urllib.urlencode(post_data), timeout=5).read()
except:
	pass

if config['publish_to_serial']:
	del post_data['image_string']
	clib.sendDataToSerialPorts(json.dumps(post_data))


