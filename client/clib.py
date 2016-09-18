from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time, subprocess, datetime, exifread
import serial
from serial.tools import list_ports

WIDTH = 640
HEIGHT = 480
CHANNELS = {'r': 0, 'g': 1, 'b': 2}

def shoot():
	try:
		subprocess.call(['C:\Program Files\digiCamControl\CameraControlCmd.exe', '/capture', '/folder', 'c:\chlorophyll\pictures'])
	except:
		try:
			subprocess.call(['C:\Program Files (x86)\digiCamControl\CameraControlCmd.exe', '/capture', '/folder', 'c:\chlorophyll\pictures'])
		except:
			pass
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

def getRegionsData (file, regions, delete=False):
	im = Image.open(file)
	result = []

	for r in regions:
		mask = Image.new('1', im.size)
		draw = ImageDraw.Draw(mask)
		channel = CHANNELS[ r['channel'] ]
		r = {'x': int(r['x']), 'y': int(r['y']), 'w': int(r['w']), 'h': int(r['h'])}
		draw.rectangle([
			getCoordinate(im, r['x'], r['y']),
			getCoordinate(im, r['x']+r['w'], r['y']+r['h'])
		], fill=255)

		data = ImageStat.Stat(im, mask).mean
		# select channel
		result.append( data[channel] )

	im = im.resize((WIDTH, HEIGHT))

	jpeg_image_buffer = cStringIO.StringIO()
	#im.save(jpeg_image_buffer, format="PNG")
	im.save(jpeg_image_buffer, format="JPEG")
	image_string = base64.b64encode(jpeg_image_buffer.getvalue())

	if delete:
		os.remove(file)

	return result, image_string

def getLatLonDate (file):
	f = open(file, 'rb')
	tags = exifread.process_file(f)
	f.close()

	date = datetime.datetime.strftime(
		datetime.datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S'),
		'%Y-%m-%d %H:%M:%S'
	) if 'EXIF DateTimeOriginal' in tags else datetime.datetime.now()

	gps_latitude = tags['GPS GPSLatitude'] if 'GPS GPSLatitude' in tags else ''
	gps_latitude_ref = tags['GPS GPSLatitudeRef'] if 'GPS GPSLatitudeRef' in tags else ''
	gps_longitude = tags['GPS GPSLongitude'] if 'GPS GPSLongitude' in tags else ''
	gps_longitude_ref = tags['GPS GPSLongitudeRef'] if 'GPS GPSLongitudeRef' in tags else ''

	if not gps_latitude:
		return '', '', date

	try:
		lat = _convert_to_degress(gps_latitude)
		if gps_latitude_ref.values[0] != "N":
			lat = 0 - lat

		lon = _convert_to_degress(gps_longitude)
		if gps_longitude_ref.values[0] != "E":
			lon = 0 - lon

		return lat, lon, date
	except:
		return '', '', date


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

def sendDataToSerialPorts(data):
	for port in list_ports.comports():
		print 'Sending data to serial port ' + port.device
		ser = serial.Serial(port.device)
		ser.write(data)
		time.sleep(1)
		ser.close()
