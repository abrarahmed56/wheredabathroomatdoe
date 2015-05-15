var map, err, button, utilList;

var SHOW = true;
var MARK = false;

function initialize() {
    err = $('flashed_messages');
    $('select').material_select();
    getPosition(SHOW);
}

function getPosition(show) {
    if (navigator.geolocation) {
        if (show) {
            console.log("page loaded");
            navigator.geolocation.getCurrentPosition(function(position) {
                var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.latitude);
                var mapOptions = {
                    zoom: 15,
                    center: myLatlng
                }
                map = new google.maps.Map($('#map-canvas')[0], mapOptions);
		getNearbyUtils();
            }, showError);
	    
        }
        else {
            console.log("button pressed");
            navigator.geolocation.getCurrentPosition(function(position) {
                var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.latitude);
		var img = document.getElementById('utilType').value;
		if (img != 'NONE') {
                    var marker = new google.maps.Marker({
			position: myLatlng,
			map: map,
			icon: img
                    });
		}
            }, showError);
        }
    } 
    else {
        err.innerHTML = "Geolocation is not supported by this browser.";
    }
}

function getNearbyUtils() {
    //gets data of format: {1:["bench", 40.324342, 29.432423], 2: ["bathroom", 40.324564, 29.432948], etc...} and marks them
    utilList = {1:{type:"bench", position:[40.334, 29.432]}, 2: {type:"bathroom", position:[40.324, 29.412]}, 3:{type:"fountain", position:[40.365, 29.468]}}
    for (util in utilList) {
	markUtil(utilList[util]);
    }
}

function markUtil(util) {
    //marks utility. format of util: {type:"bench", position:[40.324342, 29.432423]}
    var latlng = new google.maps.LatLng(util['position'][0], util['position'][1]);
    var marker = new google.maps.Marker({
	position: latlng,
	map: map,
	icon:"static/img/"+util['type']+".gif"});
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            err.innerHTML = "User denied the request for Geolocation.";
        case error.POSITION_UNAVAILABLE:
            err.innerHTML = "Location information is unavailable.";
        case error.TIMEOUT:
            err.innerHTML = "The request to get user location timed out.";
        case error.UNKNOWN_ERROR:
            err.innerHTML = "An unknown error occurred.";
    }
}

google.maps.event.addDomListener(window, 'load', initialize);
