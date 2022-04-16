
/* Submit letter */

$('#letter-form').submit(function(e) {
  var data = $("#letter-form").serialize();
  var dif = $(difficulty).serialize();

  /* Empty input */
  $('#letter-form input').val('');
  
  $.ajax({
    type: "POST",
    url: '',
    data: data,
	dif: dif,
    success: function(data) {
      /* Refresh if finished */
      if (data.finished) {
        location.reload();
      }
      else {
        /* Update current */
        $('#current').text(data.current);
        
        /* Update errors */
        if (dif != 'hard') {
			$('#errors').html(
          	'Errors (' + data.errors.length + '/8): ' +
          	'<span class="text-danger spaced" style="color: orangered;">' + data.errors + '</span>');
		}
		else {
			$('#errors').html(
          	'Errors (' + data.errors.length + '/6): ' +
          	'<span class="text-danger spaced" style="color: orangered;">' + data.errors + '</span>');
		}
		
        
        /* Update drawing */
        updateDrawing(data.errors);
      }
    }
  });
  e.preventDefault();
});

function updateDrawing(errors) {
  $('#hangman-drawing').children().slice(0, errors.length).show();
}
