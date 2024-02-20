$().ready(function() {

function objectifyForm(formArray) {
  var returnArray = {};
  for (var i = 0; i < formArray.length; i++){
    returnArray[formArray[i]['name']] = formArray[i]['value'];
  }
  return returnArray;
};

var searchManager = {
    get_list: function() {
        $("#results").html('');
        var q = $("#person-input").val();

        query_params = {'search': q, 'limit': 100};

        $.getJSON({
            url: personListUrl,
            data: query_params,
            success: function(data) {
                searchManager.process_list(data);
            }
        });
    },

    process_list: function(data) {
        $.each(data.results, function(iter, item) {
            $('#results').append('<div class="search-item"><a href="/persons/' + item.id + '/">' 
                + item.full_name + '</a></div>');
        });

    },

};

var timeout;

$('a.letter').on('click', function (e) {
    e.preventDefault();
    var val = $(this).text();
    $("#person-input").val(val);
    window.history.pushState(
        {}, "",
        updateQueryStringParameter(window.location.href, 'search', val)
    );
    searchManager.get_list();
});

$('#person-input').keypress(function() {
    if(timeout) { 
        clearTimeout(timeout);
    }
    timeout = setTimeout(function() {
        searchManager.get_list();
    }, 500);
});

$('#search-submit-btn').click(function() {
    searchManager.get_list();
});

  $('#id_dob').datepicker({
    language: 'ru',
    format: "dd.mm.yyyy", 
    clearBtn: true,
    startView: 2,
  });
  $('#id_dod').datepicker({
    language: 'ru',
    format: "dd.mm.yyyy", 
    clearBtn: true,
    startView: 2, 
  });


// $('.editable').click(function() {
//     var selector = this.id + 'Form';
//     $("#" + selector).show();
//     $("#submitForm").show();
// });

$('#showPersonForm').click(function() {
    $(this).hide();
    $('.editable').hide();
    $('form#personForm').show();
});

$('#cancelPersonForm').click(function() {
    $('button#showPersonForm').show();
    $('form#personForm').hide();
});


$('#showPersonSeasonForm').click(function() {
    $(this).hide();
    $("#addPersonSeason").show();
});

$('#cancelPersonSeasonForm').click(function() {
    $('#showPersonSeasonForm').show();
    $("#addPersonSeason").hide();
});

$('#submitPersonSeasonForm').click(function() {
    $('#showPersonSeasonForm').show();
    $("#addPersonSeason").hide();
    var dataArray = $('#addPersonSeason').serializeArray(),
        json = {};

    var json = objectifyForm(dataArray);
    json['person'] = person;

    $.ajax({
        url: personSeasonListUrl,
        type: 'POST',
        data: JSON.stringify(json),
        contentType: 'application/json',
        dataType: 'json',
        success: function () {
            $('#showPersonSeasonForm').show();
            $('#addPersonSeason').hide();
            $('#moderationModal').modal('toggle');
        },
    });
});

});
