var map, err, button, utilList, activeType;
var activeMarker = false;
var SHOW = true;
var MARK = false;
var UTILITY_TYPES = {
    "fountain" : "static/img/fountain.gif",
    "bathroom" : "static/img/bathroom.gif",
    "bench"    : "static/img/bench.gif"
}
var infowindow = new google.maps.InfoWindow();

function getUtilityName(name) {
    return (_.invert(UTILITY_TYPES))[name];
}

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
                var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
                var mapOptions = {
                    zoom: 15,
                    center: myLatlng
                }
                map = new google.maps.Map($('#map-canvas')[0], mapOptions);
		getNearbyUtils(position.coords.latitude,position.coords.longitude);
            }, showError);
        }
        else if (activeMarker) {
	    markActiveUtil();
	    activeMarker.draggable = false;
	    activeMarker = false;
	    $('input[type="button"]')[0].value = 'Utility Spotted';
	}
	else {
            console.log("button pressed");
            navigator.geolocation.getCurrentPosition(function(position) {
                activeType = $('#utilType')[0].value;
		if (activeType != 'NONE') {
		    Materialize.toast('Drag icon to confirm location', 4000);
		    var latlng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
                    activeMarker = new google.maps.Marker({
			position: latlng,
			map: map,
			icon: UTILITY_TYPES[activeType],//change color
			draggable: true
		    });
		    $('input[type="button"]')[0].value = 'Mark Location';
		}
            }, showError);
        }
    }
    else {
        err.innerHTML = "Geolocation is not supported by this browser.";//flash
    }
}

function markActiveUtil() {
    console.log(activeMarker.position['F']);
    $.post("/api/add", {"longitude" : activeMarker.position['F'], "latitude" : activeMarker.position['A'], "type" : activeType})
        .done(function(data) {
	    console.log(data);
	    Materialize.toast('Location marked', 3000);
   	});
}

function getNearbyUtils(lati,longi) {
    console.log("getting utilities");
    //gets data of format: {1:["bench", 40.324342, 29.432423], 2: ["bathroom", 40.324564, 29.432948], etc...} and marks them
    //UNSURE OF FORMAT RETURNED BY DB QUERY
    $.post("/api/get", {"longitude" : longi, "latitude" : lati})
        .done(function(data) {
	    utilList = eval(data); // TODO Should be JSON data
            console.log(data);
	    for (var i = 0; i < utilList.length; ++i) {markUtil(utilList[i]);};
	});
}

function markUtil(util) {
    //marks utility. format of util: {type:"bench", position:[40.324342, 29.432423]}
    var latlng = new google.maps.LatLng(util['position'][1], util['position'][0]);
    var img = UTILITY_TYPES[util['type']];
    var marker = new google.maps.Marker({
	position: latlng,
	map: map,
	icon: img});
    google.maps.event.addListener(marker, 'click', function() {
	console.log('util clicked'); 
	infowindow.close();
/*	infowindow = new google.maps.InfoWindow({
	    map: map,
	    position: latlng,
	    content: getUtilInfo(util)
	});*/
	infowindow.setContent(getUtilInfo(util));
	infowindow.open(map, marker);
    });
    console.log('UTILITY MARKED');
}

function getUtilInfo(util) {
    console.log(util);
    $(".utilImage")[0].src = UTILITY_TYPES[util['type']];
    $(".utilImage")[0].height = "100";
    $(".utilImage")[0].width = "2000";
    $(".utilTitle")[0].innerHTML = util['type'] + " Info";
    $(".utilTitle")[1].innerHTML = util['type'] + " Info";
    $(".utilDescription")[0].innerHTML =
	"Here are the reviews about this " + util['type'] +
	"<input type='text' id='review' name='review' placeholder='Review'><br><input type='text' id='rating' name='rating' placeholder='Rating/5'><br><button onclick='addReview(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] +")'>Add Review</button>";
    moocow = $('#infoWindow')[0].innerHTML;
    return $('#infoWindow')[0].innerHTML;
}

function addReview(placeType, locationX, locationY) {
    console.log("method called");
    console.log("placetype: " + placeType);
    console.log("locationx: " + locationX);
    review = $("#review").val();
    rating = $("#rating").val();
    $.post("/api/review", {"review" : review
			 , "placeType": placeType
			 , "locationX": locationX
			 , "locationY": locationY
			 , "rating": rating
			  })
        .done(function(data) {
	    console.log(data);
	});
    console.log("add review");
    console.log($("#review"));
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
