$().ready(function() {

window.PAGE = 1;
window.GETPAGE = true;

$().ajaxStart(function() {
    $('#indicator').show();
}).ajaxStop(function() {
    $('#indicator').hide();
});

});