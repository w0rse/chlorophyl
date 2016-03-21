(function() {


var WIDTH = 640;
var HEIGHT = 480;
var regions = [];
var currentValues;
var selectedRegion;
var previewImage = $('#preview').get(0);
var $dataTable = $('#history-data table');
var $channelSelect = $('select[name="region-channel"]');
var $deviceSelect = $('select[name="device-select"]');
var config = [];
var currentDevice = localStorage.getItem('currentDevice') || '';

var $regionsContainer = $('#regions');

getConfig();

function getConfig () {
	$.get('/get_config', function(data) {
		config = data;
		initDevices();
		selectDevice();
	});
	$.get('/get_last_pic', function(report) {
		currentValues = report.values;
		setCurrentImage(report.picture);
	});
	$.get('/get_data', function(data) {
		data.reverse().forEach(addReport);
	});
}

function initDevices () {
	config.forEach(function(c) {
		$deviceSelect.append('<option value="' + c._id + '">' + c.deviceName + '</option>');
	});
}

function selectDevice () {
	var id = $deviceSelect.val();
	currentDevice = id;
	localStorage.setItem('currentDevice', id);

	removeRegions();

	var deviceConfig = config.find(function(e) { return e._id === id; });
	deviceConfig.regions.forEach(addRegion);
}

function addReport (report) {
	var values = report.values.map(function(v) {
		return v.toFixed(2);
	});
	$('<tr class="report-item">'+
		'<td class="report-date">'+new Date(report.date).toLocaleString()+'</td>'+
		'<td class="report-value">'+values.join(', ')+'</td>'+
	'</tr>').prependTo($dataTable);
}

function setCurrentImage (pic) {
	previewImage.src = "data:image/jpeg;base64,"+pic;
}

function addRegion (region) {
	var id = regions.length;
	var newRegion = !region;
	region = region || {x: 10, y: 20, w: 100, h: 100};
	region.channel = region.channel || 'r';
	// region.deviceId = region.deviceId || '0';
	region.id = id;

	var $r = $('<div class="region ' + region.channel + '" id="region' + id + '">').css({
		left: region.x,
		top: region.y,
		width: region.w,
		height: region.h,
	}).draggable({ 
		containment: 'parent',
		stop: function(e, ui) {
			region.x = ui.position.left;
			region.y = ui.position.top;
			saveConfig();
		}
	}).resizable({
		containment: 'parent',
		stop: function(e, ui) {
			region.w = ui.size.width;
			region.h = ui.size.height;
			saveConfig();
		}
	}).data('id', id).appendTo($regionsContainer);

	regions.push(region);

	if (newRegion) {
		saveConfig();
	}
}

function removeRegions () {
	$('.region').remove();
	$channelSelect.attr('disabled', true);
	selectedRegion = null;
	regions = [];
}

function selectRegion (id) {
	$('.region').removeClass('active');
	$('#region' + id).addClass('active');
	selectedRegion = regions[id];

	$channelSelect.attr('disabled', false).val(selectedRegion.channel);
}

function selectChannel () {
	var channel = $channelSelect.val();
	selectedRegion.channel = channel;
	$('#region' + selectedRegion.id).removeClass('r g b').addClass(channel);

	saveConfig();
}

function saveConfig () {
	$.post('/save_regions', {regions: regions, id: currentDevice}, function() {});
}



$('#add-region-button').click(addRegion.bind(null, null));
$channelSelect.on('change', selectChannel);
$deviceSelect.on('change', selectDevice);

$regionsContainer.on('click', '.region', function(e) {
	var $target = $(e.currentTarget);
	selectRegion($target.data('id'));
});






$(window).on('hashchange', function() {
	if (!location.hash) {
		return;
	}
	$('article').hide();
	$(location.hash).show();
});
$(window).trigger('hashchange');


var socket = io();
socket.on('report', function (report) {
	console.log('got report', report);
	if (report.picture) {
		currentValues = report.values;
		setCurrentImage(report.picture);
		addReport(report);
	}
});



})();