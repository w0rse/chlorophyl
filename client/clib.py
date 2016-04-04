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

def getLatLon (gps_latitude='', gps_latitude_ref='', gps_longitude='', gps_longitude_ref=''):
	lat = _convert_to_degress(gps_latitude)
	if gps_latitude_ref.values[0] != "N":                     
		lat = 0 - lat

	lon = _convert_to_degress(gps_longitude)
	if gps_longitude_ref.values[0] != "E":
		lon = 0 - lon

	return lat, lon


# https://gist.github.com/snakeye/fdc372dbf11370fe29eb
def _convert_to_degress(value):
	"""
	Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
	:param value:
	:type value: exifread.utils.Ratio
	:rtype: float
	"""
	d = float(value.values[0].num) / float(value.values[0].den)
	m = float(value.values[1].num) / float(value.values[1].den)
	s = float(value.values[2].num) / float(value.values[2].den)

	return d + (m / 60.0) + (s / 3600.0)