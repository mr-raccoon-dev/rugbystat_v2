$().ready(function() {

$('#id_date').datepicker({
  language: 'ru',
  format: "dd.mm.yyyy", 
  clearBtn: true,
  startView: 2,
});

$('.showForm').click(function() {
    $(this).hide();
    $('.addForm').show();
});

$('.cancelForm').click(function() {
    $('.showForm').show();
    $('.addForm').hide();
});


});
