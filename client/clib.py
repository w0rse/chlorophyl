import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread

WIDTH = 640
HEIGHT = 480

def shoot():
	try:
		subprocess.call(['C:\Program Files\digiCamControl\CameraControlCmd.exe', '/capture', '/folder', 'c:\chlorophyll\pictures'])
	except:
		subprocess.call(['C:\Program Files (x86)\digiCamControl\CameraControlCmd.exe', '/capture', '/folder', 'c:\chlorophyll\pictures'])
	time.sleep(5)
	
def getCoordinate(im, x, y):
	x = int(x * im.size[0] / WIDTH)
	y = int(y * im.size[1] / HEIGHT)
	return (x, y)

def removeCamera():
	process = subprocess.Popen(['C:\devcon\devcon.exe', 'find', 'USB\VID*'], stdout=subprocess.PIPE, shell=True)
	out, err = process.communicate()
	result = out.split('\n')
	for line in result:
		if 'AW120' in line or 'L840' in line:
			print line
			parts = line.split('\\')
			device_id = (parts[0] + '\\' + parts[1]).replace('&', '^&')
			subprocess.Popen(['C:\devcon\devcon.exe', 'remove', device_id], shell=True)