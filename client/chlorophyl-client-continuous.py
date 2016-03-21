
# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime

time.sleep(30)

config = json.loads(open('config.json', 'r').read())
WIDTH = 640
HEIGHT = 480
HOW_MANY = 1

# find any new cameras
subprocess.Popen(['C:\devcon\devcon.exe', 'rescan'], shell=True)

time.sleep(20)

state = json.loads(urllib2.urlopen(config['server_url']+'/get_config').read())
print state

def getCoordinate(im, x, y):
	x = int(x * im.size[0] / WIDTH)
	y = int(y * im.size[1] / HEIGHT)
	return (x, y)

def getImageData():

	subprocess.call(['C:\Program Files (x86)\digiCamControl\CameraControlCmd.exe', '/capture'])
	time.sleep(5)

	max_mtime = 0
	for dirname, subdirs, files in os.walk("../pictures"):
		for fname in files:
			full_path = os.path.join(dirname, fname)
			mtime = os.stat(full_path).st_mtime
			if mtime > max_mtime:
				max_mtime = mtime
				max_file = full_path

	print 'reading '+max_file
	im = Image.open(max_file)
	result = []

	for r in state['regions']:
		mask = Image.new('1', im.size)
		draw = ImageDraw.Draw(mask)
		r = {'x': int(r['x']), 'y': int(r['y']), 'w': int(r['w']), 'h': int(r['h'])}
		draw.rectangle([
			getCoordinate(im, r['x'], r['y']), 
			getCoordinate(im, r['x']+r['w'], r['y']+r['h'])
		], fill=255)

		data = ImageStat.Stat(im, mask).mean
		# take only red channel
		result.append( data[0] )

	im = im.resize((WIDTH, HEIGHT))

	jpeg_image_buffer = cStringIO.StringIO()
	#im.save(jpeg_image_buffer, format="PNG")
	im.save(jpeg_image_buffer, format="JPEG")
	image_string = base64.b64encode(jpeg_image_buffer.getvalue())

	print result

	return {
		'image_data': result,
		'image_string': image_string,
	}


post_data = {
	'image_data': [0] * len(state['regions'])
}

for i in range(0, HOW_MANY):
	image_data = getImageData()
	post_data['image_string'] = image_data['image_string']
	post_data['image_data'] = [post_data['image_data'][j] + image_data['image_data'][j] for j in range(len(state['regions']))]

post_data['image_data'] = [x / HOW_MANY for x in post_data['image_data']]

urllib2.urlopen(config['server_url']+'/add_report', urllib.urlencode(post_data)).read()
