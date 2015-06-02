from PIL import Image, ImageDraw, ImageStat
import urllib, urllib2, json, base64, cStringIO

config = json.loads(open('config.json', 'r').read())
WIDTH = 640
HEIGHT = 480

state = json.loads(urllib2.urlopen(config['server_url']+'/get_config').read())

print state

im = Image.open("thai.png")
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
	result.append( (data[0] + data[1] + data[2]) / 3 )

im = im.resize((WIDTH, HEIGHT))

jpeg_image_buffer = cStringIO.StringIO()
im.save(jpeg_image_buffer, format="PNG")
image_string = base64.b64encode(jpeg_image_buffer.getvalue())

print result

post_data = {
	'image_data': result,
	'image_string': image_string,
}

urllib2.urlopen(config['server_url']+'/add_report', urllib.urlencode(post_data)).read()
