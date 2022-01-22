var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

$('#form_search').on('submit', function(event){
    event.preventDefault();
    $.ajax({
        url: '/search',
        method: 'POST',
        data: $(this).serialize(),
        beforeSend:function() {
            $('#search').attr('disabled', 'disabled');
            $('#process').css('display', 'block');
            $('.progress-bar').css('width', '2%');
            $('.progress-bar-label').text('2%');
        },
        success:function(response) {
            //console.log(response)
            var timer = setInterval(function() {
                $.getJSON('/search/parsing', {}, function(data) {
                    console.log(data)
                    $('.progress-bar').css('width', data.percentage + '%');
                    $('.progress-bar-label').text(data.percentage + '%');
                    if (data.percentage == 100) {
                        clearInterval(timer);
                        document.location.href = '/report';
                    }
                });
            }, 5000);
        },
        error: function(error) {
            console.log(error);
        }
    })
});


//var source = new EventSource("/progress");
//	source.onmessage = function(event) {
//		$('.progress-bar').css('width', event.data+'%').attr('aria-valuenow', event.data);
//		$('.progress-bar-label').text(event.data+'%');
//		if(event.data == 100){
//			source.close()
//		}
//	}