from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO, os, sys, time
import SendKeys

config = json.loads(open('config.json', 'r').read())
WIDTH = 640
HEIGHT = 480

state = json.loads(urllib2.urlopen(config['server_url']+'/get_config').read())
print state

SendKeys.SendKeys('^l')
time.sleep(10)

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

def getCoordinate(x, y):
	x = int(x * im.size[0] / WIDTH)
	y = int(y * im.size[1] / HEIGHT)
	return (x, y)

for r in state['regions']:
	mask = Image.new('1', im.size)
	draw = ImageDraw.Draw(mask)
	r = {'x': int(r['x']), 'y': int(r['y']), 'w': int(r['w']), 'h': int(r['h'])}
	draw.rectangle([
		getCoordinate(r['x'], r['y']), 
		getCoordinate(r['x']+r['w'], r['y']+r['h'])
	], fill=255)

	data = ImageStat.Stat(im, mask).mean
	result.append( data[0] )

im = im.resize((WIDTH, HEIGHT))

jpeg_image_buffer = cStringIO.StringIO()
#im.save(jpeg_image_buffer, format="PNG")
im.save(jpeg_image_buffer, format="JPEG")
image_string = base64.b64encode(jpeg_image_buffer.getvalue())

print result

post_data = {
	'image_data': result,
	'image_string': image_string,
}

urllib2.urlopen(config['server_url']+'/add_report', urllib.urlencode(post_data)).read()
