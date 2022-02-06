var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

$('#id_form_parsing').on('submit', function(event) {
    console.log('in function submit parsing');
    event.preventDefault();
    $.ajax({
        url: '/search/',
        method: 'POST',
        data: $(this).serialize(),
        beforeSend:function() {
            $('#parsing').attr('disabled', 'disabled');
            $('#process').css('display', 'block');
            $('.progress-bar').css('width', '0%');
            $('.progress-bar-label').text('0%');
        },
        success:function(response) {
            //console.log(response);
            var timer = setInterval(function() {
                $.getJSON('/search/progress-parsing', {}, function(data) {
                    //console.log(data);
                    $('.progress-bar').css('width', data.percentage + '%');
                    $('.progress-bar-label').text(data.percentage + '%');
                    if (data.percentage == 100) {
                        clearInterval(timer);
                        document.location.href = '/parsing-result';
                    }
                });
            }, 5000);
        },
        error: function(error) {
            console.log(error);
        }
    })
});


$(window).on('beforeunload', function(event) {
    event.preventDefault();
    $.ajax({
        url: '/search/stop-parsing',
        method: 'POST'
    });
});
