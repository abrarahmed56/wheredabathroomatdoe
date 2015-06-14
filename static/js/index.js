console.log('hi');

var App = new Marionette.Application();

function initialize() {
    err = $('flashed_messages');
    $('select').material_select();
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
            var mapOptions = {
                zoom: 15,
                center: myLatlng
            }
	})
    }
}


App.addRegions({
    placeRegion: '#place'
});

App.on("start", function() {
    console.log("started");
    var placesview = new App.CompositeView({collection:places});
    App.placeRegion.show(placesview);
});

App.PlaceView = Marionette.ItemView.extend({
    template: "#t",
    tagName: "tr",
    events: {
	"click #delete": function() {
	    var h = new Place({type:'bench', address:'bs', rating: 5})
	    this.model.save(this.model.toJSON());
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

App.PlacesView = Marionette.CollectionView.extend({
    childView: App.HomeworkView,
});

App.CompositeView = Marionette.CompositeView.extend({
    template: "#comptemp",
    childView: App.PlaceView,
    childViewContainer: "tbody"
});

var Place = Backbone.Model.extend({
    idAttribute: "PlacesID",
    urlRoot: "/api/marionette",
});
var Places = Backbone.Collection.extend({
    model: Place,
    url: "/api/marionette",
    initialize: function() {
	this.fetch();
	this.on("change: d", function(){console.log('hi');}, this);
    }
});

var places = new Places();

App.start();
google.maps.event.addDomListener(window, 'load', initialize);
