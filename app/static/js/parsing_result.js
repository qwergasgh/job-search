var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})


function status_temp_vacancy(id) {
    id_vacancy = id.toString();
    if (document.getElementById(id_vacancy).checked != true) {
        document.getElementById(id_vacancy).removeAttribute('checked');
        set_database(id_vacancy, 'n');
    }
    else {
        document.getElementById(id_vacancy).checked='y';
        set_database(id_vacancy, 'y');
    }
}

function set_database(id_vacancy, func_param) {
    // console.log(id_vacancy, func_param)
    $.ajax({
        type: 'POST',
        url: '/parsing-result/set-status-vacancy',
        data: JSON.stringify({id: id_vacancy, param: func_param}),
        contentType: 'application/json',
        success: function(response) {
            console.log(response.status + ' ' + response.valid);
        },
        error: function(error) {
            // console.log(error);
            console.log(error.status + ' ' + error.valid);
        }
    });
}

function delete_vacancy(id_vacancy) {
    // console.log(id_vacancy, func_param)
    $.ajax({
        type: 'POST',
        url: '/parsing-result/delete-vacancy',
        data: JSON.stringify({id: id_vacancy}),
        contentType: 'application/json',
        success: function(response) {
            console.log(response.status + ' ' + response.valid);
            document.location.href = '/parsing-result/';
        },
        error: function(error) {
            // console.log(error);
            console.log(error.status + ' ' + error.valid);
        }
    });
}