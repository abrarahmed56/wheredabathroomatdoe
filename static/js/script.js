var matchEmails = function() {
    email1 = document.getElementById("email1").value
    email2 = document.getElementById("email2").value
    if (email1 != email2) {
	Materialize.toast('Please enter matching emails', 4000)
    }
}
