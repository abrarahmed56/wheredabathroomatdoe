var map, err, button;

var SHOW = true;
var MARK = false;

function initialize() {
    getPosition(SHOW);
    err = document.getElementById("error-div");//will use marionette
    //button = document.getElementById("b");
    //button.addEventListener('click',getPosition(MARK));
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
		map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
	    }, showError);
	    
	} else {
	    console.log("button pressed");
	    navigator.geolocation.getCurrentPosition(function(position) {
		var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.latitude);
		var marker = new google.maps.Marker({
		    position: myLatlng,
		    map: map
		});
	    }, showError);
	}
    } else {
        err.innerHTML = "Geolocation is not supported by this browser."
    }
}

function showError(error) {
    switch(error.code) {
    case error.PERMISSION_DENIED:
        err.innerHTML = "User denied the request for Geolocation."
    case error.POSITION_UNAVAILABLE:
        err.innerHTML = "Location information is unavailable."
    case error.TIMEOUT:
        err.innerHTML = "The request to get user location timed out."
    case error.UNKNOWN_ERROR:
        err.innerHTML = "An unknown error occurred."
    }
}

google.maps.event.addDomListener(window, 'load', initialize);