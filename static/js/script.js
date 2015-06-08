var matchEmails = function(id1, id2) {
    email1 = document.getElementById(id1).value;
    email2 = document.getElementById(id2).value;
    if (email1 != email2) {
        Materialize.toast('Please enter matching emails', 4000);
        return false;
    }
    return true;
}

var matchPasswords = function(id1, id2) {
    pass1 = document.getElementById(id1).value;
    pass2 = document.getElementById(id2).value;
    if (pass1 != pass2) {
        Materialize.toast('Please enter matching passwords', 4000);
        return false;
    }
    return true;
}

var showFlashes = function() {
    for (var i = 0; i < flashed_messages.length; ++i) {
	Materialize.toast(flashed_messages[i], 4000);
    }
}

function getScreenCoordinates(obj) {
    var p = {};
    p.x = obj.offsetLeft;
    p.y = obj.offsetTop;
    while (obj.offsetParent) {
        p.x = p.x + obj.offsetParent.offsetLeft;
        p.y = p.y + obj.offsetParent.offsetTop;
        if (obj == document.getElementsByTagName("body")[0]) {
            break;
        }
        else {
            obj = obj.offsetParent;
        }
    }
    return p;
}

var toggleLogoDisplay = function() {
    // Toggle visibility for logo to prevent menu icon and logo from overlapping
    var logo = document.getElementById("logo");
    var menu = document.getElementById("nav-menu");
    var logoCoords = getScreenCoordinates(logo);
    var menuCoords = getScreenCoordinates(menu);
    if (menuCoords.x != 0) { // menu.x is 0 when the menu icon is not visible
        if (Math.abs(logoCoords.x - menuCoords.x) <= 250) {
            logo.style.visibility = 'hidden';
            return;
        }
    }
    // Default to visible
    logo.style.visibility = 'visible';
}

var switchModalFocus = function(fromModal, toModal) {
    $(fromModal).closeModal();
    setTimeout(function() {
        $(toModal).openModal();
    }, 300);
}

$(document).ready(function() {
    $(".button-collapse").sideNav();
    $(".modal-trigger").leanModal();
    toggleLogoDisplay();
    showFlashes();
});
$(window).resize(function() {
    toggleLogoDisplay();
});
