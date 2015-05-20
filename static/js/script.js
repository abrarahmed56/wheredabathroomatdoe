var matchEmails = function() {
    email1 = document.getElementById("registerEmail1").value;
    email2 = document.getElementById("registerEmail2").value;
    if (email1 != email2) {
	Materialize.toast('Please enter matching emails', 4000);
	return false;
    }
    return true;
}
