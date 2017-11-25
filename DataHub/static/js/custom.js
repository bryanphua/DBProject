// $(document).ready(function(){
$(function(){
	var index;

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

	// $(document).on('click', '.dataset', function() {
	// 	window.location = "/dataset";
	// });

	$('.dataset-menu').click(function() {
		index = $('.dataset-menu').index(this);
	});

	$('.action-unfollow').click(function() {
		$('.dataset:eq('+index+')').remove();
	});

	$('.action-delete').click(function() {
		$('.dataset:eq('+index+')').remove();
	});

});

function toDataset(id) {
	window.location = "/dataset/" + id;
};