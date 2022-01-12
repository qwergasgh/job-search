function status_vacancy(id) {
    id_vacancy = id.toString();
    if (document.getElementById(id_vacancy).value == 'add') {
        document.getElementById(id_vacancy).value='delete';
        set_database(id_vacancy, 'add');
    }
    else {
        document.getElementById(id_vacancy).value='add';
        set_database(id_vacancy, 'delete');
    }
}


function set_database(id_vacancy, func_param) {
    console.log(id_vacancy, func_param)
    $.ajax({
        type: 'POST',
        url: '/report/set-status-vacancy',
        data: JSON.stringify({id: id_vacancy, param: func_param}),
        contentType: 'application/json',
        success: function(response) {
            console.log(response.status + ' ' + response.valid);
        },
        error: function(error) {
            console.log(error);
            console.log(error.status + ' ' + error.valid);
        }
    });
}