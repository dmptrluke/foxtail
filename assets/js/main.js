import 'bootstrap';
import 'svgxuse';

const maxLength = 280;

$(function () {
    $('[data-toggle="tooltip"]').tooltip();

    $('#id_text').keyup(function () {
        let length = $(this).val().length;
        length = maxLength - length;
        let plural = (length === 1) ? "" : "s";
        $('#hint_id_text').text(length + ' character' + plural + ' remaining.');
    });
});
