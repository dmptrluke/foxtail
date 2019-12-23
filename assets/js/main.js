import 'bootstrap';
import 'colcade';
import Choices from "choices.js";

$(function () {
    $('[data-toggle="tooltip"]').tooltip();

    $('#id_text').keyup(function () {
        let length = $(this).val().length;
        let limit = $(this).attr('maxlength');

        length = limit - length;
        let plural = (length === 1) ? "" : "s";
        $('#hint_id_text').text(length + ' character' + plural + ' remaining.');
    });
});
