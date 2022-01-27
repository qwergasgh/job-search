var csrftoken = $('meta[name=csrf-token]').attr('content')

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken)
        }
    }
})

function set_database_favorites() {
    
}


function status_temp_vacancies(func_param) {
    $.ajax({
        type: 'POST',
        url: '/search/parsing-result/set-status-vacancies',
        data: JSON.stringify({param: func_param}),
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

function status_temp_vacancy(id) {
    id_vacancy = id.toString();
    if (document.getElementById(id_vacancy).checked == 'y') {
        document.getElementById(id_vacancy).checked='n';
        set_database(id_vacancy, 'y');
    }
    else {
        document.getElementById(id_vacancy).checked='y';
        set_database(id_vacancy, 'n');
    }
}

function set_database(id_vacancy, func_param) {
    // console.log(id_vacancy, func_param)
    $.ajax({
        type: 'POST',
        url: '/search/parsing-result/set-status-vacancy',
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