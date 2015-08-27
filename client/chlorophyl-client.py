# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime
import SendKeys
import win32gui

time.sleep(60)

config = json.loads(open('config.json', 'r').read())
WIDTH = 640
HEIGHT = 480
HOW_MANY = 1

def removeCamera():
	process = subprocess.Popen(['C:\devcon\devcon.exe', 'find', 'USB\VID*'], stdout=subprocess.PIPE, shell=True)
	out, err = process.communicate()
	result = out.split('\n')
	for line in result:
		if 'AW120' in line:
			print line
			parts = line.split('\\')
			device_id = (parts[0] + '\\' + parts[1]).replace('&', '^&')
			subprocess.Popen(['C:\devcon\devcon.exe', 'remove', device_id], shell=True)

def setForeground(title=''):
	toplist = []
	winlist = []
	def enum_callback(hwnd, results):
		winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
	win32gui.EnumWindows(enum_callback, toplist)
	wnd = None
	for l in winlist:
		if title in l[1]:
			wnd = l
	# use the window handle to set focus
	if wnd:
		win32gui.SetForegroundWindow(wnd[0])

removeCamera()
# close DigiCamControl
subprocess.Popen(['taskkill', '/f', '/im', 'CameraControl.exe'])

time.sleep(15)

subprocess.Popen(['C:\Program Files (x86)\digiCamControl\CameraControl.exe'])

# find any new cameras
subprocess.Popen(['C:\devcon\devcon.exe', 'rescan'], shell=True)
# now = datetime.datetime.now()
# if now.minute < 5 or now.minute > 15:
# 	SendKeys.SendKeys('^l')
# 	sys.exit(0)

time.sleep(180)

subprocess.Popen(['c:/windows/system32/rasphone.exe', '-d', 'MTS-Internet'])

time.sleep(60)

state = json.loads(urllib2.urlopen(config['server_url']+'/get_config').read())
print state

def getCoordinate(im, x, y):
	x = int(x * im.size[0] / WIDTH)
	y = int(y * im.size[1] / HEIGHT)
	return (x, y)

def getImageData():

	SendKeys.SendKeys('^l')
	time.sleep(15)

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

# we want a window with cursor for our hitkey to work
setForeground('Sublime')

for i in range(0, HOW_MANY):
	image_data = getImageData()
	post_data['image_string'] = image_data['image_string']
	post_data['image_data'] = [post_data['image_data'][j] + image_data['image_data'][j] for j in range(len(state['regions']))]

post_data['image_data'] = [x / HOW_MANY for x in post_data['image_data']]

urllib2.urlopen(config['server_url']+'/add_report', urllib.urlencode(post_data)).read()

removeCamera()

# close DigiCamControl
subprocess.Popen(['taskkill', '/f', '/im', 'CameraControl.exe'])

# Disconnect from internet
subprocess.call(['c:/windows/system32/rasphone.exe', '-h', 'MTS-Internet'])
subprocess.call(['c:/windows/system32/rasphone.exe', '-h', 'MTS-Internet'])

# go back to sleep
# subprocess.call(['rundll32.exe', 'powrprof.dll,SetSuspendState'])
