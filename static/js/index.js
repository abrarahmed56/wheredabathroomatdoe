var App = new Marionette.Application();

App.addRegions({
    placeRegion: '#place'
});

App.on("start", function() {
    var placesview = new App.CompositeView({collection:places});
    App.placeRegion.show(placesview);
});

App.PlaceView = Marionette.ItemView.extend({
    template: "#t",
    tagName: "tr",
    events: {
        "click #delete": function() {
            this.remove();
        },
        "click #directions": function() {
            var myLatlng;
            var locX = this.model.attributes.address[0];
            var locY = this.model.attributes.address[1];
            var address = [locY, locX];
            navigator.geolocation.getCurrentPosition(function(position) {
                myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
                var replaceURL = "/api/directions/" + address + "/" + myLatlng
                    replaceURL = replaceURL.replace("(", "").replace(")", "").replace(" ", "");
                window.location.replace(replaceURL);
            });
        }
    }
});

App.CompositeView = Marionette.CompositeView.extend({
    template: "#comptemp",
    childView: App.PlaceView,
    childViewContainer: "tbody"
});

var Place = Backbone.Model.extend({
    idAttribute: "PlacesID",
    urlRoot: "/api/myplaces",
});

var Places = Backbone.Collection.extend({
    model: Place,
    url: "/api/myplaces",
    initialize: function() {
        this.fetch();
    }
});

var places = new Places();

App.start();
