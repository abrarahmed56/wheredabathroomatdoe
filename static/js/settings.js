window.addEventListener('load', load);
var load = function() {
    $("#confirm_email_link").click(function() {
        $.post("/confirm/send/email", function(data) {
            if (data === "OK") {
                window.location.reload();
            }
        });
    });
}
