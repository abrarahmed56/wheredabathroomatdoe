var map, err, button, utilList, activeType;
var activeUtil;
var activeMarker = false;
var SHOW = true;
var MARK = false;
var UTILITY_TYPES = {"fountain" : {'small' : "static/img/fountain.gif"
                                  ,'large' : "static/img/fountain.png"}
                    ,"bathroom" : {'small' : "static/img/bathroom.gif"
                                  ,'large' : "static/img/bathroom.png"}
                    ,"bench"    : {'small' : "static/img/bench.gif"
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
    $.post("/api/add", {"longitude" : util['position'][0],
                        "latitude" : util['position'][1],
                        "type" : util['type']})
        .done(function(data) {
            markUtil(util);
            activeMarker.setMap(null);
            activeMarker = false;
            $('input[type="button"]')[0].value = 'Utility Spotted';
            Materialize.toast('Location marked', 3000);
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
        infoWindow.setContent(getUtilInfo(activeUtil));
        infoWindow.open(map, marker); });
    google.maps.event.addListener(infoWindow, 'closeclick', function(){
        // Show input form and toggle buttons
        $('#inputForm').fadeIn(700);
        $('#toggleButtons').fadeIn(700);
    });
    markedUtils.push(marker);
}

function getUtilInfo(util) {
    utilType = util['type'];
    utilPositionZero = util['position'][0];
    utilPositionOne = util['position'][1];
    $(".utilImage")[0].src = UTILITY_TYPES[utilType]['large'];
    $(".utilTitle")[0].innerHTML = utilType[0].toUpperCase() + utilType.substring(1);
    $(".utilTitle")[1].innerHTML = utilType[0].toUpperCase() + utilType.substring(1);
    inFavorites(util, utilType, utilPositionZero, utilPositionOne);
    return $('#infoWindow')[0].innerHTML;
}

function getReviews(placeType, locationX, locationY) {
    $.post("/api/getreviews", {"placeType": placeType
                              ,"locationX": locationX
                              ,"locationY": locationY
    }).done(function(data) {
        _data = eval(data);
        var reviews = "";
        for (var i=0; i<_data.length; i++) {
            rating = _data[i]['Rating'];
            review = _data[i]['Review'];
            userFirstName = _data[i]['UserFirstName'];
            userProfile = _data[i]['UserProfile'];
            userPic = _data[i]['UserPic'];
            reviews += "<a href='" + userProfile + "'>" + userFirstName + "</a>" +
                " rated this a <b>" + rating + "</b>.<br/><br/>" +
                "<i>" + review + "</i><br/><br/>" +
                "<div class='input field'>" +
                "<button class='btn green darken-2 waves-effect waves-light'><i class='mdi-hardware-keyboard-arrow-up'></i></button>" +
                "<button class='btn red darken-2 waves-effect waves-light'><i class='mdi-hardware-keyboard-arrow-down'></i></button>" +
                "</div><hr>";
        }
        $("#reviews")[0].innerHTML = reviews;
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
    });
}

function addFavorite(placeType, locationX, locationY) {
    $.post("/api/addfavorite", {"placeType": placeType
                                ,"locationX": locationX
                                ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil);
    });
}

function removeFavorite(placeType, locationX, locationY) {
    $.post("/api/removefavorite", {"placeType": placeType
                                  ,"locationX": locationX
                                  ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil);
    });
}

function inFavorites(util, placeType, locationX, locationY) {
    $.post("/api/infavorites",  {"placeType": placeType
                                ,"locationX": locationX
                                ,"locationY": locationY
    }).done(function(data) {
        if (new String(data).valueOf()===new String("False").valueOf()) {
            favoritesButton = "<button type='submit' id='favoritesButton' class='btn green darken-2 waves-effect waves-light' onclick='addFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Add Favorite<i class='mdi-action-stars left'></i></button><br/><br/>" +
                "<button type='submit' class='btn red darken-2 waves-effect waves-light' value='Report'>Report<i class='mdi-alert-warning left'></i></button>";
        }
        else {
            favoritesButton = "<button type='submit' id='favoritesButton' class='btn red darken-2 waves-effect waves-light' onclick='removeFavorite(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ");'>Remove Favorite<i class='mdi-navigation-close left'></i></button>";
        }
        $(".utilDescription")[0].innerHTML =
            "Here are the reviews for this " + util['type']  + ". " +
            "<hr><div id='reviews'></div>" +
            "<h6 class='center-text'>Add a Review</h6>" +
            "<div class='input-field'>" +
            "<textarea id='review' name='review' class='materialize-textarea validate' maxlength=500 length='500'></textarea>" +
            "<label for='review'>Review</label></div>" +
            "<div class='input-field'><label>Rating (1 to 5)</label><br/>" +
            "<p class='range-field'>" +
            "<input type='range' id='rating' min='1' max='5'/>" +
            "</p></div><div class='input-field center-all'>" +
            "<button type='submit' class='btn green darken-2 waves-effect waves-light' onclick='addReview(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] +")'>Add Review<i class='mdi-editor-border-color left'></i></button>" +
            "<br/><br/>" + favoritesButton + "</div>";
        // Populate info window with reviews
        getReviews(util['type'], util['position'][0], util['position'][1]);
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
