
	$(document).ready(function() {
		var today = new Date();
		$('#calendar').fullCalendar({
			header: {
				left: 'prev,next today',
				center: 'title',
				right: ''
			},
			defaultDate: today.getUTCFullYear().toString() + "-" + (today.getUTCMonth()+1).toString() + "-" + today.getUTCDate().toString(),
			editable: true,
			eventLimit: true,
			events: {
				url: 'data',
				error: function() {
					$('#script-warning').show();
				}
			},
			loading: function(bool) {
				$('#loading').toggle(bool);
			}
		});

	});