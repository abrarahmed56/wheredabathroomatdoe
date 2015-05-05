console.log('hi');

var App = new Marionette.Application();

App.addRegions({
    homeworkRegion: '#homework'
});

App.on("start", function() {
    console.log("started");
    var homeworksview = new App.CompositeView({collection:hws});
    //console.log(App.homeworkRegion);
    App.homeworkRegion.show(homeworksview);
});

App.HomeworkView = Marionette.ItemView.extend({
    template: "#t",
    tagName: "tr",
    events: {
	//var that = this;
	"click #delete": function() {
	    //this.save(this.toJSON());
	    var h = new HW({clas:'c', homework:'a', deadline: 'd'})
	    console.log(this.model);
	    //console.log(h);
	    this.model.save(this.model.toJSON());
	    this.remove();
	}
    }
});

App.HomeworksView = Marionette.CollectionView.extend({
    childView: App.HomeworkView,
    /*events: {
	"click #add": function() {
	    var h = $("#newhw").val();
	    if ( h.length > 0 ) {
		this.collection.add(new HW({clas:h, homework:'a', deadline: 'now'}));
		$("#newhw").val("");
	    }
	}
    }*/
});

App.CompositeView = Marionette.CompositeView.extend({
    template: "#comptemp",
    childView: App.HomeworkView,
    childViewContainer: "tbody",
    events: {
	"click #add": function() {
	    var c = $("#newclass").val();
	    var a = $("#newassignment").val();
	    var d = $("#newdeadline").val();
	    if ( c.length > 0 ) {
		if ( a.length == 0 ) {
		    a = "stuff"
		}
		if ( d != parseInt(d) || d.length == 0) {
		    d = 9001;
		}
		else {
		    d = parseInt(d);
		}
		var that = this;
		var h = new HW({clas:c, homework:a, deadline: d})
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
		$("#newhw").val("");
	    }
	},
    }
});

var HW = Backbone.Model.extend({
    idAttribute: "_id",
    //id: "_id",
    urlRoot: "/hw",
    defaults: {
	homework: "stuff",
	deadline: "ehh"
    }
});
var HWs = Backbone.Collection.extend({
    model: HW,
    url: "/hw",
    initialize: function() {
	this.fetch();
	this.on("change: d", function(){console.log('hi');}, this);
	var that = this;
	/*setInterval(function() {
	    that.fetch();
	}, 10000);*/
    }
});
var hw = new HW({
    clas: 'Softdev',
    homework: 'marionette',
    deadline: 'tomorrow'
});
var hw2 = new HW({
    clas: 'WPT',
    homework: 'questions',
    deadline: 'yesteday'
});
var hws = new HWs([hw, hw2]);

App.start();
