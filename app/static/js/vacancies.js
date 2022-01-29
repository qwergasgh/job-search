var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

function delete_vacancy(id) {
    id_vacancy = id.toString();
    $.ajax({
        type: 'POST',
        url: '/vacancies/delete-vacancy',
        data: JSON.stringify({id: id_vacancy}),
        contentType: 'application/json',
        success: function(response) {
            console.log('valid' + response.valid);
            document.location.href = '/vacancies';
        },
        error: function(error) {
            // console.log(error);
            console.log('valid' + error.valid);
        }
    });
}