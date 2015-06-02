var mongoose = require('mongoose');
var Schema = mongoose.Schema;

var reportSchema = new Schema({
	date: { type: Date, default: Date.now, index: true },
	values: [Number],
	metrics: {},
	picture: String,
});
reportSchema.index({date: -1});

var configSchema = new Schema({
	modified: { type: Date, default: Date.now, index: true },
	regions: [{x: Number, y:Number, w:Number, h:Number}],
	interval: Number,
	getPicture: Boolean,
});

module.exports = {
	Report : mongoose.model('Report', reportSchema),
	Config : mongoose.model('Config', configSchema),
};