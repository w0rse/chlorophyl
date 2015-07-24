(function() {

var WIDTH = 640;
var HEIGHT = 480;

var regions = [];
var drawing = false;
var activeRect;
var currentImage, currentValues;

var ctx = $('canvas')[0].getContext('2d');
ctx.strokeStyle = 'white';
ctx.fillStyle = 'white';
ctx.font = '14px Arial, sans-serif';

$('#canvas').on('mousedown touchstart', function(e) {
	drawing = true;
	activeRect = {
		x: e.offsetX,
		y: e.offsetY
	};
}).on('mouseup touchend', function(e) {
	drawing = false;

	if (activeRect.w < 0) {
		activeRect.x = activeRect.x + activeRect.w;
		activeRect.w *= -1;
	}
	if (activeRect.h < 0) {
		activeRect.y = activeRect.y + activeRect.h;
		activeRect.h *= -1;
	}

	if (activeRect.w > 10 && activeRect.h > 10) {
		regions.push(activeRect);
	} else {
		removeRegionsHere({x: e.offsetX, y: e.offsetY});
	}
	currentValues = null;
	activeRect = null;
	draw();
	saveRegions();
}).on('mousemove touchmove', function(e) {
	if (drawing) {
		activeRect.w = e.offsetX - activeRect.x;
		activeRect.h = e.offsetY - activeRect.y;
		requestAnimationFrame(draw);
	}
});
$(window).on('hashchange', function() {
	if (!location.hash) {
		return;
	}
	$('article').hide();
	$(location.hash).show();
});
$(window).trigger('hashchange');

function draw () {
	ctx.clearRect(0, 0, WIDTH, HEIGHT);

	if (currentImage) {
		ctx.drawImage(currentImage, 0, 0);
	}

	ctx.strokeRect(0, 0, WIDTH, HEIGHT);
	regions.forEach(function(r, i) {
		ctx.strokeRect(r.x, r.y, r.w, r.h);
		if (currentValues) {
			ctx.fillText(currentValues[i].toFixed(2), r.x + 5, r.y + 15);
		}
	});
	if (activeRect) {
		ctx.strokeRect(activeRect.x, activeRect.y, activeRect.w, activeRect.h);
	}
}

function removeRegionsHere (pos) {
	regions = regions.filter(function(r) {
		return !(pos.x >= r.x && pos.x <= (r.x + r.w) && pos.y >= r.y && pos.y <= (r.y + r.h));
	});
}

function saveRegions () {
	regions = regions.sort(function(a, b) {
		return a.x + a.y >= b.x + b.y;
	});
	$.post('/save_regions', {regions: regions}, function() {});
}

function getConfig () {
	$.get('/get_config', function(config) {
		regions = config.regions || [];
		draw();
	});
	$.get('/get_last_pic', function(report) {
		currentValues = report.values;
		setCurrentImage(report.picture);
	});
	$.get('/get_data', function(data) {
		data.reverse().forEach(addReport);
	});
}

function setCurrentImage (pic) {
	currentImage = new Image();
	currentImage.onload = function() {
		draw();
	};
	// currentImage.src = "data:image/png;base64,"+pic;
	currentImage.src = "data:image/jpeg;base64,"+pic;
}

getConfig();

var socket = io();
socket.on('report', function (report) {
	console.log('got report', report);
	if (report.picture) {
		currentValues = report.values;
		setCurrentImage(report.picture);
		addReport(report);
	}
});

function addReport (report) {
	var values = report.values.map(function(v) {
		return v.toFixed(2);
	});
	$('<tr class="report-item">'+
		'<td class="report-date">'+new Date(report.date).toLocaleString()+'</td>'+
		'<td class="report-value">'+values.join(', ')+'</td>'+
	'</tr>').prependTo('#history-data table');
}

})();
