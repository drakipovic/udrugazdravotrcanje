function callApi(settings){
    settings.dataType = 'json';
    settings.contentType = 'application/json';

    settings.error = function(xhr, status, err){
        var response = JSON.parse(xhr.responseText);
        console.error(response);
    }.bind(this)

    $.ajax(settings);
}