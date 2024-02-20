$().ready(function() {

var searchManager = {
    get_list: function() {
        $("#results").html('');
        var q = $("#team-input").val();

        $.getJSON({
            url: teamListUrl + '?limit=100&search=' + q,
            success: function(data) {
                searchManager.process_list(data);
            }
        });
    },
    process_list: function(data) {
        $.each(data.results, function(iter, item) {
            $('#results').append('<div class="search-item"><a href="/teams/' + item.id + '/">' + item.short_name + ' (' + item.operational_years + ')</a></div>');
        });

        // $('#results a').click(function(e) {
        //     e.preventDefault();
        //     searchManager.get_team(this);
        // });

    },

    get_team: function(domElement) {
        var id = domElement.dataset.teamId;
        $("#results").html('');

        $.getJSON({
            url: teamListUrl + id + "/",
            success: function(data) {
                window.history.pushState({}, '', '/teams/' + id + '/');
                window.location.reload();
                searchManager.process_team(data);
            }
        });
    },
    process_team: function(team) {
        $('#results').append('<div class="team-title"><h2>' + team.name + ' ' + team.city.name + ' (' + team.operational_years + ')</h2></div>');
        $('#results').append('<div class="team-story"><p>' + team.story + '</p></div>');
        if(team.documents.length > 0) {
            $('#results').append('<div class="documents-div">' + 
                '<table class="table table-striped table-hover" id="documents-table"><thead><tr>' + 
                '<th>Заголовок</th>' + 
                '<th>Описание</th>' + 
                '<th>Месяц/Год</th>' + 
                '<th>Ссылка</th>' + 
                '</tr></thead><tbody></tbody></table>' +
                '</div>');
            
            $.each(team.documents, function(iter, item) {
                var link;
                var year;
                if (item.is_image == true) {
                    link = '<a class="dropbox-link" href="' + item.dropbox_path + 
                    '"><img src="' + item.dropbox_thumb + '"/></a>'
                } else {
                    link = '<a href="' + item.dropbox_path + 
                    '">Нет превью</a>'
                };

                if (item.month != null) {
                    year = item.month + '/' + item.year
                } else {
                    year = item.year
                };

                $('#documents-table tbody').append('<tr class="document-row">' + 
                    '<td>' + item.title + '</td>' +
                    '<td>' + item.description + '</td>' +
                    '<td>' + year + '</td>' +
                    '<td>' + link + '</td>' +
                    '</tr>');
            });

        };

        // $('.dropbox-link').click(function(e) {
        //     e.preventDefault();
        //     $('.modal-body').html('<img src="' + this.href + '"/>');
        //     $('.modal').show();
        // });
        // $('.close').click(function(e) {
        //     $('.modal').hide();
        // });

    },
};


var timeout;

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
  
  
$('#team-input').keypress(function() {
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

$('#showTeamForm').click(function() {
    $(this).hide();
    $('form#teamForm').show();
});

$('#cancelTeamForm').click(function() {
    $('button#showTeamForm').show();
    $('form#teamForm').hide();
});


$('#showTeamSeasonForm').click(function() {
    $(this).hide();
    $('form#addSeason').show();
});

$('#cancelSeasonForm').click(function() {
    $('button#showTeamSeasonForm').show();
    $('form#addSeason').hide();
});

$('#submitSeasonForm').click(function() {
    var dataArray = $('#addSeason').serializeArray(),
        json = {};
  
    var json = objectifyForm(dataArray);
    
    $.ajax({
        url: teamSeasonListUrl,
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
  
  
// function yHandler() {
//     if(document.body.scrollHeight - window.innerHeight - 50 < window.scrollY) {
//         window.PAGE += 1;
//         searchManager.get_list(window.PAGE);
//     }
// };

// window.onscroll = yHandler;

});