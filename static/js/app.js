console.log('hi');

var App = new Marionette.Application();

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
	    console.log(this.model);
	    //console.log(h);
	    this.model.save(this.model.toJSON());
	    this.remove();
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
    urlRoot: "/hw",
    defaults: {
	/*homework: "stuff",
	deadline: "ehh"*/
    }
});
var Places = Backbone.Collection.extend({
    model: Place,
    url: "/favorites",
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
