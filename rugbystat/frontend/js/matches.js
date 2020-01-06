$().ready(function() {

function objectifyForm(formArray) {
  var returnArray = {};
  for (var i = 0; i < formArray.length; i++){
    var val = formArray[i]['value'];
    if (val === "") {
      val = null
    };
    returnArray[formArray[i]['name']] = val;
  }
  return returnArray;
};

  
$('#id_date').datepicker({
  language: 'ru',
  format: "yyyy-mm-dd", 
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

$('#submitMatchForm').click(function() {
  var dataArray = $('#addMatch').serializeArray(),
      json = {};

  var json = objectifyForm(dataArray);
  if (json['story'] == null) {
    json['story'] = ''
  };

  $.ajax({
      url: matchListUrl,
      type: 'POST',
      data: JSON.stringify(json),
      contentType: 'application/json',
      dataType: 'json',
      success: function () {
        $('.showForm').show();
        $('.addForm').hide();
        $('#moderationModal').modal('toggle');
      },
  });
});

});
