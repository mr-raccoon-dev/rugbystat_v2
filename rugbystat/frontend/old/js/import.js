$().ready(function() {

  $.fn.select2.defaults.set( "theme", "bootstrap" );
  
  $('#id_date_start').datepicker({
    language: 'ru',
    format: "yyyy-mm-dd", 
    clearBtn: true,
    startView: 2,
  });
  $('#id_date_end').datepicker({
    language: 'ru',
    format: "yyyy-mm-dd", 
    clearBtn: true,
    startView: 2, 
  });

});
