var map, err, button, utilList;

var SHOW = true;
var MARK = false;
var UTILITY_TYPES = {
    "fountain" : "static/img/fountain.gif",
    "bathroom" : "static/img/bathroom.gif",
    "bench"    : "static/img/bench.gif"
}

function getUtilityName(name) {
    return (_.invert(UTILITY_TYPES))[name];
}

function initialize() {
    err = $('flashed_messages');
    $('select').material_select();
    getPosition(SHOW);
    getNearbyUtils();
}

function getPosition(show) {
    if (navigator.geolocation) {
        if (show) {
            console.log("page loaded");
            navigator.geolocation.getCurrentPosition(function(position) {
                var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
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
                var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
	        var img = document.getElementById('utilType').value;
        	if (img != 'NONE') {
            //addPlace(name, locationX, locationY)
                    /*var marker = new google.maps.Marker({
              map: map,
              icon: img
              });*/
		    $.post("/api/add", {"longitude" : position.coords.longitude, "latitude" : position.coords.latitude, "type" : img})
			.done(function(data) {
                            //alert(data);//flash data
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
    //UNSURE OF FORMAT RETURNED BY DB QUERY
    navigator.geolocation.getCurrentPosition(function(position) {
        var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
	$.post("/api/get", {"longitude" : position.coords.longitude, "latitude" : position.coords.latitude})
            .done(function(data) {
                //alert(data);
		utilList = data;
	    });
    })
    for (util in utilList) {
	console.log(util)
	markUtil(utilList[util]);
    }
}

function markUtil(util) {
    //marks utility. format of util: {type:"bench", position:[40.324342, 29.432423]}
    console.log(util);
    var latlng = new google.maps.LatLng(util['position'][0], util['position'][1]);
    var marker = new google.maps.Marker({
    position: latlng,
    map: map,
    icon: UTILITY_TYPES[util['type']]});
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
