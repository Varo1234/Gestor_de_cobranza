$(document).ready(function() {
    $("#agregar_pago").click(function() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(sendPosition);
        } else {
            alert("Geolocation is not supported by this browser.");
        }
    });

    function sendPosition(position) {
        $.ajax({
            url: '',  // Use the current URL
            type: 'post',
            data: {
                'monto': $('#monto').val(),
                'latitud': position.coords.latitude,
                'longitud': position.coords.longitude,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data) {
                alert("Pago agregado exitosamente!");
                location.reload();
            },
            error: function(data) {
                alert("Error al agregar pago.");
            }
        });
    }
});
