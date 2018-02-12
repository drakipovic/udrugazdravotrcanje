function callApi(settings){
    settings.dataType = 'json';
    settings.contentType = 'application/json';
    settings.username = localStorage.getItem("username")
    settings.password = localStorage.getItem("password")

    settings.error = function(xhr, status, err){
        var response = JSON.parse(xhr.responseText);
        console.error(response);
    }.bind(this)

    $.ajax(settings);
}