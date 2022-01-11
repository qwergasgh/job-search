
function status_vacancy(id) {
    id_vacancy = id.toString();
    if (document.getElementById(id_vacancy).value == 'add') {
        document.getElementById(id_vacancy).value='delete';
        console.log(status_vacancy_database(id_vacancy, 'add'));
    }
    else {
        document.getElementById(id_vacancy).value='add';
        console.log(status_vacancy_database(id_vacancy, 'delete'));
    }
}


function status_vacancy_database(id_vacancy, func_param) {
    var result = $.ajax({
        type: 'POST',
        url: 'status-favorite-vacancy',
        data: {id: id_vacancy, param: func_param},
        dataType: "text"
    });
    return result.responseText;
}