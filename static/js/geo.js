var map, err, button, utilList, activeType;
var activeUtil;
var activeMarker = false;
var SHOW = true;
var MARK = false;
var UTILITY_TYPES = {"fountain" : {'small' : "static/img/fountain.gif"
				  ,'card' : "static/img/fountain-card.png"
                                  ,'large' : "static/img/fountain.png"}
                    ,"bathroom" : {'small' : "static/img/bathroom.gif"
				  ,'card' : "static/img/bathroom-card.png"
                                  ,'large' : "static/img/bathroom.png"}
                    ,"bench"    : {'small' : "static/img/bench.gif"
				  ,'card' : "static/img/bench-card.png"
                                  ,'large' : "static/img/bench.png"}
                    };

var infoWindow = new google.maps.InfoWindow();
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
            navigator.geolocation.getCurrentPosition(function(position) {
                var myLatlng = new google.maps.LatLng(position.coords.latitude,
                                                      position.coords.longitude);
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
            navigator.geolocation.getCurrentPosition(function(position) {
                activeType = $('#utilType')[0].value;
                if (activeType != 'NONE') {
                    Materialize.toast("Drag icon to confirm location." +
                                      " Then click Mark Location.", 4000);
                    var latlng = new google.maps.LatLng(position.coords.latitude,
                                                        position.coords.longitude);
                    activeMarker = new google.maps.Marker({
                        position: latlng,
                        map: map,
                        icon: UTILITY_TYPES[activeType]['small'],
                        draggable: true
                    });
                    $('#addButton')[0].value = 'Mark Location';
                    $('#cancelAddButton').show();
                }
            }, showError);
        }
    }
    else {
        err.innerHTML = "Geolocation is not supported by this browser.";//flash
    }
}

function cancelAddUtil() {
    activeMarker.setMap(null);
    activeMarker = false;
    $('#addButton')[0].value = 'Utility Spotted';
    $('#cancelAddButton').hide();
}

function markActiveUtil() {
    var util = {
        position : [activeMarker.position['F'], activeMarker.position['A']],
        type : activeType
    }
    $.post("/api/add", {"longitude" : util['position'][0],
                        "latitude" : util['position'][1],
                        "type" : util['type']})
        .done(function(data) {
            var newMarker = markUtil(util);
            // Hide input form and toggle buttons
            $('#inputForm').fadeOut(700);
            $('#toggleButtons').fadeOut(700);
            // Open info window for newly created marker
            infoWindow.setContent(getUtilInfo(util, "new"));
            infoWindow.open(map, newMarker);
            activeUtil = util;
            activeMarker.setMap(null);
            activeMarker = false;
            $('#addButton')[0].value = 'Utility Spotted';
            Materialize.toast('Location marked', 3000);
            Materialize.toast('Please add a description', 5000);
        });
    markedUtils.push(util);
}

function getNearbyUtils(lati,longi) {
    $.post("/api/get", {"longitude" : longi, "latitude" : lati})
        .done(function(data) {
            utilList = eval(data); // TODO Should be JSON data
            for (var i = 0; i < utilList.length; ++i) {
                markUtil(utilList[i]);
            }
        });
}

function markUtil(util) {
    //marks utility. format of util: {type:"bench", position:[40.324342, 29.432423]}
    var latlng = new google.maps.LatLng(util['position'][1], util['position'][0]);
    var img = UTILITY_TYPES[util['type']]['small'];
    var marker = new google.maps.Marker({
        position: latlng,
        map: map,
        icon: img
    });
    google.maps.event.addListener(marker, 'click', function() {
        infoWindow.close();
        // Hide input form and toggle buttons
        $('#inputForm').fadeOut(700);
        $('#toggleButtons').fadeOut(700);
        activeUtil = util;
        infoWindow.setContent(getUtilInfo(activeUtil, "old"));
        infoWindow.open(map, marker); });
    google.maps.event.addListener(infoWindow, 'closeclick', function(){
        // Show input form and toggle buttons
        $('#inputForm').fadeIn(700);
        $('#toggleButtons').fadeIn(700);
    });
    markedUtils.push(marker);
    return marker;
}

function getUtilInfo(util, newOrOld) {
    console.log("getutilinfo");
    utilType = util['type'];
    utilPositionZero = util['position'][0];
    utilPositionOne = util['position'][1];
<<<<<<< HEAD
    $(".utilImage")[0].src = UTILITY_TYPES[utilType]['card'];
=======
    $(".utilImage")[0].src = UTILITY_TYPES[utilType]['large'];
    getDescription(util, utilType, utilPositionZero, utilPositionOne);
>>>>>>> Start getDescription for place description
    $(".utilTitle")[1].innerHTML = utilType[0].toUpperCase() + utilType.substring(1);
    cardInfo(util, utilType, utilPositionZero, utilPositionOne, newOrOld);
    return $('#infoWindow')[0].innerHTML;
}

function addDescription() {
    $.post("/api/adddescription", {"placeType": $("#placeType").val()
				   ,"locationX": $("#locationX").val()
				   ,"locationY": $("#locationY").val()
				   ,"description": $("#description").val()
    }).done(function(data) {
	Materialize.toast(data, 4000);
    });
}

function getReviews(placeType, locationX, locationY) {
    $.post("/api/getreviews", {"placeType": placeType
                              ,"locationX": locationX
                              ,"locationY": locationY
    }).done(function(data) {
        _data = eval(data);
        var reviews = "";
        if (_data.length == 0) {
            $('#descriptionHeader').html("Unfortunately there aren't any reviews for this " +
                    placeType + " yet. That means you can be the first to write one!");
        }
        else {
            $('#descriptionHeader').html("Here are the reviews for this " + placeType + ":");
            for (var i=0; i<_data.length; i++) {
                rating = _data[i]['Rating'];
                review = _data[i]['Review'];
                userFirstName = _data[i]['UserFirstName'];
                userProfile = _data[i]['UserProfile'];
                userPic = _data[i]['UserPic'];
                reviews += "<div style='display:inline-block'>" +
                    "<img src='" + userPic + "' width='32px' height='32px' style='margin-right: 10px'></img>" +
                    "<div style='display:inline-block;'><a href='" + userProfile + "'>" + userFirstName + "</a>" +
                    "</br> rated this a <b>" + rating + "</b>.</div></div><br/><br/>" +
                    "<i>" + review + "</i><br/><br/>" +
                    "<div class='input field'>" +
                    "<button class='btn green darken-2 waves-effect waves-light'><i class='mdi-hardware-keyboard-arrow-up'></i></button>" +
                    "<button class='btn red darken-2 waves-effect waves-light'><i class='mdi-hardware-keyboard-arrow-down'></i></button>" +
                    "</div><hr>";
            }
            $("#reviews")[0].innerHTML = reviews;
        }
	});
}

function addReview(placeType, locationX, locationY) {
    review = $("#review").val();
    $("#review").val('');
    rating = $("#rating").val();
    $("#rating").val(5);
    $.post("/api/addreview", {"review" : review
                             ,"placeType": placeType
                             ,"locationX": locationX
                             ,"locationY": locationY
                             ,"rating": rating
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the reviews for the active util
        getReviews(activeUtil['type'], activeUtil['position'][0], activeUtil['position'][1]);
        getUtilInfo(activeUtil, "old");
    });
}

function addFavorite(placeType, locationX, locationY) {
    $.post("/api/addfavorite", {"placeType": placeType
                                ,"locationX": locationX
                                ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil, "old");
    });
}

function removeFavorite(placeType, locationX, locationY) {
    $.post("/api/removefavorite", {"placeType": placeType
                                  ,"locationX": locationX
                                  ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil, "old");
    });
}

function cardInfo(util, placeType, locationX, locationY, newOrOld) {
    //TODO do this stuff in one post request, return tuples
    $.post("/api/createdplace",  {"placeType": placeType
                                 ,"locationX": locationX
                                 ,"locationY": locationY
				 })
    .done(function(data) {
	if (new String(data).valueOf()===new String("False").valueOf()) {
	    removeButton = "<button type='submit' class='btn red darken-2 waves-effect waves-light' value='Report'>Report<i class='mdi-alert-warning left'></i></button>";
	}
	else {
	    removeButton = "<button type='submit' class='btn red darken-2 waves-effect waves-light' value='Remove'>Remove<i class='mdi-alert-warning left'></i></button>";
	}
    $.post("/api/infavorites",  {"placeType": placeType
                                ,"locationX": locationX
                                ,"locationY": locationY
    }).done(function(data) {
        if (new String(data).valueOf()===new String("False").valueOf()) {
            favoritesButton = "<button type='submit' id='favoritesButton' class='btn green darken-2 waves-effect waves-light' onclick='addFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Add to My Places<i class='mdi-action-stars left'></i></button><br/><br/>" +
                "<button type='submit' class='btn red darken-2 waves-effect waves-light' value='Report'>Report<i class='mdi-alert-warning left'></i></button>";
        }
        else {
            favoritesButton = "<button type='submit' id='favoritesButton' class='btn red darken-2 waves-effect waves-light' onclick='removeFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Remove from My Places<i class='mdi-navigation-close left'></i></button>";
        }
        $.post("/api/reviewfromuserexists",  {"placeType": placeType
            ,"locationX": locationX
                ,"locationY": locationY
        })
        .done(function(data) {
            var reviewStr = "Add Review";
            if (data === "True") {
                reviewStr = "Update Review";
            }
            $(".utilDescription")[0].innerHTML =
                "<span id='descriptionHeader'></span>" +
                "<hr><div id='reviews'></div>" +
                "<div id='add-review' class='no-select'>" +
                "<h6 class='center-text'>Add a Review</h6>" +
                "<div class='input-field'>" +
                "<textarea id='review' name='review' class='materialize-textarea validate' maxlength=500 length='500'></textarea>" +
                "<label for='review'>Review</label></div>" +
		"<div class='row'><div class='input-field col s3'><label>1</label></div>" +
		"<div class='input-field col s7'><label>Rating (1 to 5)</label></div>" +
		"<div class='input-field col s2'><label>5</label></div><br/>" +
                "<div class='input-field col s12'><p class='range-field'>" +
                "<input type='range' id='rating' min='1' max='5'/>" +
		"</p></div></div><div class='input-field center-all'>" +
                "<button type='submit' class='btn green darken-2 waves-effect waves-light' onclick='addReview(&quot;" +
                util['type'] + "&quot;, " + util['position'][0] + ", " +
                util['position'][1] +")'>" + reviewStr +
                "<i class='mdi-editor-border-color left'></i></button>" +
                "<br/><br/>" + favoritesButton + "</div></div>";
            // Populate info window with reviews
            getReviews(util['type'], util['position'][0], util['position'][1]);
        });
    });
    });
    if (newOrOld==="old") {
	$.post("/api/getdescription",  {"placeType": placeType
				       ,"locationX": locationX
				       ,"locationY": locationY
				       })
	    .done(function(data) {
		$(".utilTitle")[0].innerHTML = utilType[0].toUpperCase() +
		    utilType.substring(1) + "<br>" + data;
	    });
    }
    else {
	$(".utilTitle")[0].innerHTML = utilType[0].toUpperCase() +
	    utilType.substring(1) + "<br><input type='text' id='description'><input type='hidden' id='placeType' value='" + utilType + "'><input type='hidden' id='locationX' value='" + utilPositionZero + "'><input type='hidden' id='locationY' value='" + utilPositionOne + "'><button class='btn green darken-2 waves-effect waves-light' onclick='addDescription()' value='Add description'>Add description</button>";

    }
}

function getDescription(util, placeType, locationX, locationY) {
    $.post("/api/getdescription",  {"placeType": placeType
                                 ,"locationX": locationX
                                 ,"locationY": locationY
				 })
	.done(function(data) {
	});
}

function toggleView(type) {
    var btnId = '';
    if (type === 'bench') {
        btnId = '#benchToggle';
    }
    else if (type === 'fountain') {
        btnId = '#fountainToggle';
    }
    else if (type === 'bathroom') {
        btnId = '#bathroomToggle';
    }
    var displayText = $(btnId)[0].value;
    var show = (displayText.indexOf('Show') != -1);
    if (show) {
        $(btnId)[0].value = displayText.replace('Show', 'Hide');
        $(btnId).toggleClass('darken-3');
    }
    else {
        $(btnId)[0].value = displayText.replace('Hide', 'Show');
        $(btnId).toggleClass('darken-3');
    }
    /* Toggle visibility of the markers */
    var utilImg = UTILITY_TYPES[type]['small'];
    for(var i = 0; i < markedUtils.length; ++i) {
        if (markedUtils[i].icon == utilImg) {
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
