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
	models.Config.findOne(function(err, doc) {
		if (!doc) {
			config = new models.Config();
			config.regions = [];
			config.interval = 5;
			config.save();
		} else {
			config = doc;
		}
	});
});

app.get('/', function (req, res) {
	res.sendFile(__dirname + '/index.html');
});
app.get('/assets/:file', function (req, res) {
	res.sendFile(__dirname + '/assets/' + req.params.file);
});

app.get('/get_config', function (req, res) {
	res.send(config);
});
app.get('/get_data', function (req, res) {
	models.Report.find({}, 'date values').sort('-date').exec(function(err, doc) {
		res.send(doc);
	});
});
app.get('/get_last_pic', function (req, res) {
	models.Report.findOne({'picture': {'$ne': ''}}).sort('-date').exec(function(err, doc) {
		res.send(doc);
	});
});

app.post('/add_report', function (req, res) {
	console.log(req.body.image_data);
	report = new models.Report();
	report.values = JSON.parse(req.body.image_data);
	report.picture = req.body.image_string || '';
	report.metrics = {};
	report.save();
	io.sockets.emit('report', report);
	res.send('ok');
});

app.post('/save_regions', function (req, res) {
	config.regions = req.body.regions;
	config.modified = new Date();
	config.save();
	res.send('ok');
});