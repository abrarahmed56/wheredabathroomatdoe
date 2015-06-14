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
	//var that = this;
	"click #delete": function() {
	    //this.save(this.toJSON());
	    var h = new Place({type:'bench', address:'bs', rating: 5})
	    console.log(this);
	    //console.log(h);
	    this.model.save(this.model.toJSON());
	    this.remove();
	},
	"click #directions": function() {
	    var myLatlng;
	    var locX = this.model.attributes.address[0];
	    var locY = this.model.attributes.address[1];
	    console.log(locX);
	    console.log(locY);
	    var address = [locY, locX];
	    console.log("address: " + address)
	    navigator.geolocation.getCurrentPosition(function(position) {
                myLatlng = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
		var replaceURL = "/api/directions/" + address + "/" + myLatlng
		console.log(replaceURL);
		replaceURL = replaceURL.replace("(", "").replace(")", "").replace(" ", "");
		console.log(replaceURL);
		window.location.replace(replaceURL);
	    });
	    //var replaceURL = "/api/directions/" + this.model.attributes.address + "/" + myLatlng;
	    //console.log(replaceURL);
	    console.log("dir");
	}
    }
});

App.PlacesView = Marionette.CollectionView.extend({
    childView: App.HomeworkView,
    /*events: {
	"click #add": function() {
	    //var h = $("#newhw").val();
	    //if ( h.length > 0 ) {
	    this.collection.add(new Place({type:'bench', address:'bs', rating: 5}));
	    //$("#newhw").val("");
	    }
	}
    }*/
});

App.CompositeView = Marionette.CompositeView.extend({
    template: "#comptemp",
    childView: App.PlaceView,
    childViewContainer: "tbody",
    events: {
	"click #add": function() {
	    console.log("add clicked");
	    var c = "bench";
	    var a = "bs";
	    var d = 5;
	    var that = this;
	    var h = new Place({type:c, address:a, rating: d})
	    /*h.save(h.toJSON(), {success: function(m, r) {
	      if (r.result.n==1) {
	      that.collection.add(h);
	      that.render();
	      }
	      }
	      })*/
	    console.log(h.toJSON());
	    h.save(h.toJSON());
	    this.collection.add(h);
	    //$("#newhw").val("");
	},
    }
});

var Place = Backbone.Model.extend({
    idAttribute: "_id",
    //id: "_id",
    urlRoot: "/api/marionette",
    defaults: {
	/*homework: "stuff",
	deadline: "ehh"*/
    }
});
var Places = Backbone.Collection.extend({
    model: Place,
    url: "/api/marionette",
    initialize: function() {
	this.fetch();
	this.on("change: d", function(){console.log('hi');}, this);
	var that = this;
	/*setInterval(function() {
	    that.fetch();
	}, 10000);*/
    }
});

var place = new Place({
    type: 'Softdev',
    address: 'marionette',
    rating: 3
});
var place2 = new Place({
    type: 'WPT',
    address: 'questions',
    rating: 5
});
var places = new Places([place, place2]);

App.start();
google.maps.event.addDomListener(window, 'load', initialize);
