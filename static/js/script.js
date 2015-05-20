var matchEmails = function() {
    email1 = document.getElementById("registerEmail1").value;
    email2 = document.getElementById("registerEmail2").value;
    if (email1 != email2) {
	Materialize.toast('Please enter matching emails', 4000);
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
