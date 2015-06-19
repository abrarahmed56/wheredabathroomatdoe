var map;
var newUtilType;
var activeUtil;
var draggableMarker = false;
var activeMarker = false;
var TYPE_BENCH = "bench";
var TYPE_BATHROOM = "bathroom";
var TYPE_FOUNTAIN = "fountain";
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
var mapMarkers = [];

function getUtilityName(name) {
    return (_.invert(UTILITY_TYPES))[name];
}

function initialize() {
    $('select').material_select();
    displayNearbyUtils();
}

function displayNearbyUtils() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var myLatlng = new google.maps.LatLng(position.coords.latitude,
                    position.coords.longitude);
            var mapOptions = {
                zoom: 17,
                center: myLatlng
            };
            map = new google.maps.Map($('#map-canvas')[0], mapOptions);
            getNearbyUtils(position.coords.latitude,position.coords.longitude);
        }, showError);
    }
    else {
        $('body').html("Geolocation is not supported by this browser.");
    }
}

function addUtil() {
    if (navigator.geolocation) {
        if (draggableMarker) {
            putNewUtil();
        }
        else {
            navigator.geolocation.getCurrentPosition(function(position) {
                newUtilType = $('#utilType').val();
                if (newUtilType != 'NONE') {
                    Materialize.toast("Drag icon to confirm location." +
                                      " Then click Mark Location.", 4000);
                    var latlng = new google.maps.LatLng(position.coords.latitude,
                                                        position.coords.longitude);
                    draggableMarker = new google.maps.Marker({
                        position: latlng,
                        map: map,
                        icon: UTILITY_TYPES[newUtilType]['small'],
                        draggable: true
                    });
                    $('#addButton').val('Mark Location');
                    $('#cancelAddButton').show();
                }
            }, showError);
        }
    }
}

function cancelAddUtil() {
    draggableMarker.setMap(null);
    draggableMarker = false;
    $('#addButton').val('Utility Spotted');
    $('#cancelAddButton').hide();
}

function putNewUtil() {
    var util = {
        position : [draggableMarker.position['F'], draggableMarker.position['A']],
        type : newUtilType
    };
    $.post("/api/add", {"longitude" : util['position'][0],
                        "latitude" : util['position'][1],
                        "type" : util['type']})
        .done(function(data) {
            var newMarker = markUtil(util);
            // Hide input form and toggle buttons
            $('#inputForm').fadeOut(700);
            $('#toggleButtons').fadeOut(700);
            // Open info window for newly created marker
            infoWindow.setContent(getUtilInfo(util, true, function after() {
                infoWindow.open(map, newMarker);
            }));
            activeUtil = util;
            activeMarker = newMarker;
            draggableMarker.setMap(null);
            draggableMarker = false;
            $('#addButton').val('Utility Spotted');
            $('#cancelAddButton').hide();
            Materialize.toast('Location marked', 3000);
            Materialize.toast('Please add a description', 5000);
        });
}

function getNearbyUtils(lati,longi) {
    $.post("/api/get", {"longitude" : longi, "latitude" : lati})
        .done(function(data) {
            var utilList = $.parseJSON(data);
            for (var i = 0; i < utilList.length; ++i) {
                markUtil(utilList[i]);
            }
        });
}

function markUtil(util) {
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
        activeMarker = marker;
        infoWindow.setContent(getUtilInfo(activeUtil, false, function after() {
            infoWindow.open(map, marker);
            setTimeout(function() {
                // Override Google Maps' inline styling
                var infoWindowContainer = $('.infoWindowCard')[0].parentElement;
                infoWindowContainer.id = 'infoWindowContainer';
                infoWindowContainer.style['overflow-x'] = "hidden";
                infoWindowContainer.parentElement.style['margin-left'] = "10px";
            }, 100);
        }));
    });
    google.maps.event.addListener(infoWindow, 'closeclick', function(){
        // Show input form and toggle buttons
        $('#inputForm').fadeIn(700);
        $('#toggleButtons').fadeIn(700);
        activeUtil = false;
        activeMarker = false;
    });
    mapMarkers.push(marker);
    return marker;
}

function getUtilInfo(util, isNewlyCreatedUtil, callback) {
    utilType = util['type'];
    utilPositionZero = util['position'][0];
    utilPositionOne = util['position'][1];
    $(".utilImage")[0].src = UTILITY_TYPES[utilType]['card'];
    $(".utilTitleBack").html(utilType[0].toUpperCase() + utilType.substring(1));
    cardInfo(util, utilType, utilPositionZero, utilPositionOne, isNewlyCreatedUtil, callback);
    return $('#infoWindow')[0].innerHTML;
}

function addDescription() {
    $.post("/api/adddescription", {"placeType": $("#placeType").val()
                                  ,"locationX": $("#locationX").val()
                                  ,"locationY": $("#locationY").val()
                                  ,"description": $("#description").val()
    }).done(function(data) {
        $("#description").val('');
        infoWindow.setContent(getUtilInfo(activeUtil, false, null));
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
        if (_data.length === 0) {
            $('#descriptionHeader').html("Unfortunately there aren't any reviews for this " +
                    placeType + " yet. That means you can be the first to write one!");
        }
        else {
            $('#descriptionHeader').html("Here are the reviews for this " + placeType + ":");
            for (var i=0; i<_data.length; ++i) {
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
            $("#reviews").html(reviews);
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
        getUtilInfo(activeUtil, false);
    });
}

function addFavorite(placeType, locationX, locationY) {
    $.post("/api/addfavorite", {"placeType": placeType
                                ,"locationX": locationX
                                ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil, false);
    });
}

function removeFavorite(placeType, locationX, locationY) {
    $.post("/api/removefavorite", {"placeType": placeType
                                  ,"locationX": locationX
                                  ,"locationY": locationY
    }).done(function(data) {
        Materialize.toast(data, 4000);
        // Refresh the info window for the active util
        getUtilInfo(activeUtil, false);
    });
}

function removePlace(placeType, locationX, locationY) {
    $.post("/api/removeplace", {"placeType": placeType
                ,"locationX": locationX
                ,"locationY": locationY
    }).done(function(data){
    infoWindow.close();
    activeMarker.setMap(null);
    activeMarker = false;
        $('#inputForm').fadeIn(700);
        $('#toggleButtons').fadeIn(700);
    });
}

function reportPlace(placeType, locationX, locationY) {
    if ($("#reason").val()==="") {
    Materialize.toast("Please enter a reason why you are reporting this location", 4000);
    }
    else {
    $.post("/api/reportplace", {"placeType": placeType
                    ,"locationX": locationX
                    ,"locationY": locationY
                    ,"reason": $("#reason").val()
                   }).done(function(data){
                       Materialize.toast(data, 4000);
                   });
    }
}

function letUserReportPlace(placeType, locationX, locationY) {
    infoWindow.setContent("<input type='text' placeholder='Why are you reporting this place?' id='reason'><button type='submit' class='btn red darken-2 waves-effect waves-light' onclick='reportPlace(&quot;" + placeType + "&quot;, " + locationX + ", " + locationY + ")'>Report</button><button type='submit' class='btn green darken-2 waves-effect waves-light' onclick='infoWindow.setContent(getUtilInfo(activeUtil, false, null))'>Cancel</button>");
}

function getDirections(locationX, locationY) {
    var myLatlng;
    var address = [locationY, locationX];
    navigator.geolocation.getCurrentPosition(function(position) {
        myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
        var replaceURL = "/api/directions/" + address + "/" + myLatlng
            replaceURL = replaceURL.replace("(", "").replace(")", "").replace(" ", "");
        window.location.href = replaceURL;
    });
}

function cardInfo(util, placeType, locationX, locationY, isNewlyCreatedUtil, callback) {
    var removeButton = '';
    var descriptionForm = '';
    //TODO do this stuff in one post request, return tuples
    $.post("/api/createdplace",  {"placeType": placeType
                                 ,"locationX": locationX
                                 ,"locationY": locationY
                 })
    .done(function(data) {
        if (new String(data).valueOf()===new String("False").valueOf()) {
            removeButton = "<button type='submit' onclick='letUserReportPlace(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ")' class='btn red darken-2 waves-effect waves-light' value='Report'>Report<i class='mdi-alert-warning left'></i></button>";
        }
        else {
            removeButton = "<button type='submit' onclick='removePlace(&quot;" + util['type'] + "&quot;, " + util['position'][0] + ", " + util['position'][1] + ")' class='btn red darken-2 waves-effect waves-light' value='Remove'>Remove<i class='mdi-alert-warning left'></i></button>";
            descriptionForm = utilType[0].toUpperCase() +
                utilType.substring(1) + "<br><span><input type='text' id='description' placeholder='Your description' style='width: 225px'>" +
                "<a style='float:right; padding-top: 10px' onclick='addDescription()'><i class='mdi-navigation-check'></i></a></span>" +
                "<input type='hidden' id='placeType' value='" + utilType + "'>" +
                "<input type='hidden' id='locationX' value='" + utilPositionZero + "'>" +
                "<input type='hidden' id='locationY' value='" + utilPositionOne + "'>";
            $('.utilTitleFront').html(descriptionForm);
        }
        directionsButton = "<button class='btn waves-effect waves-light teal' onclick='getDirections(" + util['position'][0] + ", " + util['position'][1] + ");'>" +
                "<i class='mdi-maps-directions left'></i>Directions</button>";
        $.post("/api/infavorites",  {"placeType": placeType
                                    ,"locationX": locationX
                                    ,"locationY": locationY
        }).done(function(data) {
            if (new String(data).valueOf()===new String("False").valueOf()) {
                favoritesButton = "<button type='submit' id='favoritesButton' class='btn green darken-2 waves-effect waves-light' onclick='addFavorite(&quot;" +
                    util['type'] + "&quot;, " + util['position'][0] + ", " +
                    util['position'][1] + ");'>Add to My Places<i class='mdi-action-stars left'></i></button><br/><br/>" +
                    directionsButton + "<br/><br/>" + removeButton;
            }
            else {
                favoritesButton = "<button type='submit' id='favoritesButton' class='btn red darken-2 waves-effect waves-light' onclick='removeFavorite(&quot;" +
                    util['type'] + "&quot;, " + util['position'][0] + ", " +
                    util['position'][1] + ");'>Remove from My Places<i class='mdi-navigation-close left'></i></button><br/><br/>" +
                    directionsButton;
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
                $(".utilDescription").html(
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
                    "<br/><br/>" + favoritesButton + "</div></div>");
                // Populate info window with reviews
                getReviews(util['type'], util['position'][0], util['position'][1]);
            });
        });
    });
    if (!isNewlyCreatedUtil) {
        $.post("/api/getdescription",  {"placeType": placeType
                                        ,"locationX": locationX
                                        ,"locationY": locationY
        })
        .done(function(description) {
            var title = utilType[0].toUpperCase() +
                    utilType.substring(1) + "<br/><p class='font-small'>" 
                    + description + "</p>";
            if (!descriptionForm) {
                if (!description) {
                    description = "No description available."
                }
                $(".utilTitleFront").html(title);
                $(".utilTitleBack").html(title);
            }
            else {
                $('#description').val(description);
                $(".utilTitleBack").html(title);
            }
        });
    }
    if (callback) {
        return callback();
    }
}

function toggleView(type) {
    var btnId = '';
    if (type === TYPE_BENCH) {
        btnId = '#benchToggle';
    }
    else if (type === TYPE_FOUNTAIN) {
        btnId = '#fountainToggle';
    }
    else if (type === TYPE_BATHROOM) {
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
    for(var i = 0; i < mapMarkers.length; ++i) {
        if (mapMarkers[i].icon == utilImg) {
            mapMarkers[i].setVisible(show);
        }
    }
}

function showError(error) {
    switch(error.code) {
        case error.PERMISSION_DENIED:
            $('body').html("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            $('body').html("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            $('body').html("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            $('body').html("An unknown error occurred.");
            break;
        default:
            break;
    }
}

google.maps.event.addDomListener(window, 'load', initialize);
$(document).ready(function() {
    $('#addButton').click(function() {
        addUtil();
    });
    $('#cancelAddButton').click(function() {
        cancelAddUtil();
    });
    $('#benchToggle').click(function() {
        toggleView(TYPE_BENCH);
    });
    $('#bathroomToggle').click(function() {
        toggleView(TYPE_BATHROOM);
    });
    $('#fountainToggle').click(function() {
        toggleView(TYPE_FOUNTAIN);
    });
});
