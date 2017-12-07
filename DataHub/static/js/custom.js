// $(document).ready(function(){
$(function(){
	var index;

	// $(document).ready(function() {
	// 	$('.selectpicker').selectpicker('render');
	// });

	$(document).on('click', '.thumbs-up', function() {
		$(this).toggleClass("thumbs-up-on");
		$(this).next(".thumbs-down-on").click();
		$(this).toggleClass("thumbs-up");
	});

	$(document).on('click', '.thumbs-up-on', function() {
		$(this).toggleClass("thumbs-up");
		$(this).toggleClass("thumbs-up-on");
	});

	$(document).on('click', '.thumbs-down', function() {
		$(this).toggleClass("thumbs-down-on");
		$(this).prev(".thumbs-up-on").click();
		$(this).toggleClass("thumbs-down");
	});

	$(document).on('click', '.thumbs-down-on', function() {
		$(this).toggleClass("thumbs-down");
		$(this).toggleClass("thumbs-down-on");
	});

	$(document).on('click', '.btn-follow', function(event) {
		event.stopPropagation();
		$(this).toggleClass("btn-following");
		$(this).attr("value", "Following");
		$(this).toggleClass("btn-follow");
	});

	$(document).on('click', '.btn-following', function(event) {
		event.stopPropagation();
		$(this).toggleClass("btn-follow");
		$(this).attr("value", "Follow");
		$(this).toggleClass("btn-following");
	});

	$(document).on({
	    mouseenter: function () {
	        $(this).attr("value", "Unfollow");
	    },
	    mouseleave: function () {
	        $(this).attr("value", "Following");
	    }
	}, ".btn-following");

	$('.action-unfollow').click(function() {
		$('.dataset:eq('+index+')').remove();
	});

	$('.action-delete').click(function() {
		$('.dataset:eq('+index+')').remove();
	});

	$('#popularDatasets').click(function() {
		window.location = "/statistics/datasets";
	});

	$('#popularUsers').click(function() {
		window.location = "/statistics/users";
	});

	$('#popularGenres').click(function() {
		window.location = "/statistics/genres";
	});

	$('#selectResultGroup').change(function() {
		$('.result-group').hide();
		if ($(this).val() == "all") {
			$('.result-group').fadeIn();
		} else {
			$('#'+$(this).val()).fadeIn();
		}
	});
	
	$('#search_filter').change(function() {
		var url = new URL(window.location.href);
		var q = url.searchParams.get("q");
		var sort = url.searchParams.get("sort");

		name = $('#checkbox_name').is(":checked")
		creator = $('#checkbox_creator').is(":checked")
		genre = $('#checkbox_genre').is(":checked")
		
		window.location = "/search/?q=" + q + "&name=" + name + "&username=" + creator + "&genre=" + genre + "&sort=" + sort
	});
	
	$('#search_sorting').change(function() {
		var url = new URL(window.location.href);
		var q = url.searchParams.get("q");
		var name = url.searchParams.get("name");
		var creator = url.searchParams.get("username");
		var genre = url.searchParams.get("genre");

		sort = $('#search_sorting option:selected').val()
		console.log(sort);
		window.location = "/search/?q=" + q + "&name=" + name + "&username=" + creator + "&genre=" + genre + "&sort=" + sort
	});
	
	$('#stats_filter').change(function() {
		var url = new URL(window.location.href);
		var sort = url.searchParams.get("sort");
		var filters = $('#stats_filter option:selected').val()
		window.location = window.location.pathname + "?filters=" + filters + "&sort=" + sort
	});
	
	$('#stats_sorting').change(function() {
		var url = new URL(window.location.href);
		var filters = url.searchParams.get("filters");
		var sort = $('#stats_sorting option:selected').val()
		window.location = window.location.pathname + "?filters=" + filters + "&sort=" + sort
	});

});

function toDataset(id) {
	window.location = "/dataset/" + id;
};

function follow(id, origin) {
	event.stopPropagation();
	window.location = "/follow/" + id + "/" + origin
}

function unfollow(id, origin) {
	event.stopPropagation();
	window.location = "/unfollow/" + id + "/" + origin 
}

function comment_rate(id, up, dataset) {
	if (up) {
		window.location = "/comment/rate/"+ id +"/1/" + dataset + "/"
	} else {
		window.location = "/comment/rate/"+ id +"/-1/" + dataset + "/"
	}
}