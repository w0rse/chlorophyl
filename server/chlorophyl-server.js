var app = require('express')();
var server = require('http').Server(app);
var bodyParser = require('body-parser');
var io = require('socket.io')(server);

var mongoose = require('mongoose');
var models = require('./models');

var config;

app.use(bodyParser.urlencoded({'extended': true, 'limit': '10mb'}));

mongoose.connect('mongodb://localhost/chlorophyl');
var db = mongoose.connection;
db.once('open', function (callback) {
	server.listen(3333);
});

app.get('/', function (req, res) {
	res.sendFile(__dirname + '/index2.html');
});
app.get('/assets/:file', function (req, res) {
	res.sendFile(__dirname + '/assets/' + req.params.file);
});

app.get('/get_config', function (req, res) {
	models.Config.find(function(err, docs) {
		if (!docs.length) {
			var c = new models.Config();
			c.deviceId = 0;
			c.deviceName = 'Untitled';
			c.regions = [];
			c.save();
			config = [c];
		} else {
			config = docs;
		}
		res.send(config);
	});
});
app.post('/add_device', function (req, res) {
	var c = new models.Config();
	c.deviceName = req.body.name || '';
	c.regions = [];
	c.save();
	res.send(c._id);
});
app.get('/get_data', function (req, res) {
	models.Report.find({deviceId: req.query.id}, 'date values').sort('-date').limit(100).exec(function(err, doc) {
		res.send(doc);
	});
});
app.get('/get_last_pic', function (req, res) {
	models.Report.findOne({'picture': {'$ne': ''}, deviceId: req.query.id}).sort('-date').exec(function(err, doc) {
		res.send(doc);
	});
});

app.post('/add_report', function (req, res) {
	console.log(req.body.image_data);
	report = new models.Report();
	report.values = JSON.parse(req.body.image_data);
	report.picture = req.body.image_string || '';
	report.metrics = req.body.lat ? {
		lat: JSON.parse(req.body.lat.replace('/', ',')),
		long: JSON.parse(req.body.long.replace('/', ',')),
	} : {};
	report.deviceId = req.body.deviceId || '';
	if (req.body.date) {
		report.date = new Date(req.body.date);
	}
	report.save();
	io.sockets.emit('report', report);
	res.send('ok');
});

app.post('/save_regions', function (req, res) {
	models.Config.findByIdAndUpdate(req.body.id, { $set: { regions: req.body.regions }}, function (err, config) {
		if (err) {
			res.send(error);
		} else {
			res.send('ok');
		}
	});
});