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
var markedUtils = [];

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
    var util = {
        position : [activeMarker.position['F'], activeMarker.position['A']],
        type : activeType
    }
    $.post("/api/add", {"longitude" : util['position'][0], "latitude" : util['position'][1], "type" : util['type']})
        .done(function(data) {
	    console.log(data);
	    //getPosition(SHOW);
	    markUtil(util);
	    activeMarker.setMap(null);
	    activeMarker = false;
	    $('input[type="button"]')[0].value = 'Utility Spotted';
	    Materialize.toast('Location marked', 3000);
   	});
    markedUtils.push(util);
}

function getNearbyUtils(lati,longi) {
    console.log("getting utilities");
    //gets data of format: {1:["bench", 40.324342, 29.432423], 2: ["bathroom", 40.324564, 29.432948], etc...} and marks them
    //UNSURE OF FORMAT RETURNED BY DB QUERY
    $.post("/api/get", {"longitude" : longi, "latitude" : lati})
        .done(function(data) {
	    utilList = eval(data); // TODO Should be JSON data
            console.log("getNearbyUtils data: ");
	    for (var i = 0; i < utilList.length; ++i) {markUtil(utilList[i]);};
	});
}

function markUtil(util) {
    console.log("markutil util: " + util);
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
	infowindow.setContent(getUtilInfo(util));
	infowindow.open(map, marker);
    });
    markedUtils.push(marker);
    console.log('UTILITY MARKED');
}

function getUtilInfo(util) {
    console.log(util);
    utilType = util['type'];
    utilPositionZero = util['position'][0];
    utilPositionOne = util['position'][1];
    $(".utilImage")[0].src = UTILITY_TYPES[utilType];
    $(".utilImage")[0].height = "100";
    $(".utilImage")[0].width = "2000";
    $(".utilTitle")[0].innerHTML = utilType + " Info";
    $(".utilTitle")[1].innerHTML = utilType + " Info";
    inFavorites(util, utilType, utilPositionZero, utilPositionOne)
    return $('#infoWindow')[0].innerHTML;
}

function getReviews(placeType, locationX, locationY) {
    $.post("/api/getreviews", {"placeType": placeType
			     , "locationX": locationX
			     , "locationY": locationY
			      })
	.done(function(data) {
	    _data = eval(data);
	    _data = _data ? _data[0] : null;
	    console.log("data" + data);
	    console.log("data" + data);
	    console.log(_data);
	    console.log($("#reviews"));
	    $("#reviews")[0].innerHTML = data;
	});
}

function addReview(placeType, locationX, locationY) {
    review = $("#review").val();
    rating = $("#rating").val();
    $.post("/api/addreview", {"review" : review
			 , "placeType": placeType
			 , "locationX": locationX
			 , "locationY": locationY
			 , "rating": rating
			  })
        .done(function(data) {
	    console.log(data);
	});
}

function addFavorite(placeType, locationX, locationY) {
    $.post("/api/addfavorite", {"placeType": placeType
			      , "locationX": locationX
			      , "locationY": locationY
			       })
	.done(function(data) {
	    $("#favoritesButton").html("Remove from My Places");
	    $("#favoritesButton").attr("onclick", "removeFavorite('" + placeType + "', " + locationX + ", " + locationY + ")");
	    Materialize.toast(data, 4000);
	});
}

function removeFavorite(placeType, locationX, locationY) {
    $.post("/api/removefavorite", {"placeType": placeType
	   		         , "locationX": locationX
			         , "locationY": locationY
			       })
	.done(function(data) {
	    $("#favoritesButton").html("Add to My Places");
	    $("#favoritesButton").attr("onclick", "addFavorite('" + placeType + "', " + locationX + ", " + locationY + ")");
	    Materialize.toast(data, 4000);
	});
}

function inFavorites(util, placeType, locationX, locationY) {
    $.post("/api/infavorites",  {"placeType": placeType
			      , "locationX": locationX
			      , "locationY": locationY
			       })
	.done(function(data) {
	    console.log(data);
	    if (new String(data).valueOf()===new String("False").valueOf()) {
		favoritesButton = "<button id='favoritesButton' onclick='addFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Add to My Places</button>";
	    }
	    else {
		favoritesButton = "<button id='favoritesButton' onclick='removeFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Remove from My Places</button>";
	    }
	    $(".utilDescription")[0].innerHTML =
		"Here are the reviews for this " + util['type'] + 
		"<div id='reviews'></div>" +
		"<input type='text' id='review' name='review' placeholder='Review'><br><input type='text' id='rating' name='rating' placeholder='Rating/5'><br><button onclick='addReview(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] +")'>Add Review</button>" + favoritesButton;
	    moocow = $('#infoWindow')[0].innerHTML;
	    getReviews(util['type'], util['position'][0], util['position'][1]);
	});
}

function toggleView(type) {
    var btnName = '#'+type+'Toggle'
    var name= $(btnName)[0].value;
    if (name[0] == 'S') {
	var newName = 'Hide '+name.charAt(5).toUpperCase()+name.slice(6);
	$(btnName)[0].value = newName;
    }
    else {
	var newName = 'Show '+name.charAt(5).toUpperCase()+name.slice(6);
	$(btnName)[0].value = newName;
    }
    console.log(name);
    type = UTILITY_TYPES[type];
    for(var i = 0; i < markedUtils.length; i++) {
	if (markedUtils[i].icon == type) {
	    markedUtils[i].setVisible(!markedUtils[i].getVisible());
	}
    }
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
