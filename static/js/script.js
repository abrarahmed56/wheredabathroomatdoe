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

$(document).ready(function() {
    $(".button-collapse").sideNav();
    $(".modal-trigger").leanModal();
    showFlashes();
});
