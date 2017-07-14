$().ready(function() {

var searchManager = {
    get_list: function() {
        $("#results").html('');
        var q = $("#person-input").val();

        $.getJSON({
            url: personListUrl + '?limit=100&search=' + q,
            success: function(data) {
                searchManager.process_list(data);
            }
        });
    },

    process_list: function(data) {
        $.each(data.results, function(iter, item) {
            $('#results').append('<div class="search-item"><a data-person-id="' + item.id + '" href="#">' 
                + item.__str__ + '</a></div>');
        });

        $('#results a').click(function(e) {
            e.preventDefault();
            searchManager.get_person(this);
        });

    },

    get_person: function(domElement) {
        var id = domElement.dataset.personId;
        $("#results").html('');

        $.getJSON({
            url: personListUrl + id + "/",
            success: function(data) {
                searchManager.process_person(data);
            }
        });
    },
    process_person: function(person) {
        $('#results').append('<div class="team-title"><h2>' + person.full_name 
            + ' (' + person.living_years + ')</h2></div>');
        $('#results').append('<div class="team-story"><p>' + person.story + '</p></div>');
        if(person.seasons.length > 0) {
            $('#results').append('<div class="documents-div">' + 
                '<table class="table table-striped table-hover" id="documents-table"><thead><tr>' + 
                '<th>Год</th>' + 
                '<th>Роль</th>' + 
                '<th>Комментарии</th>' + 
                '</tr></thead><tbody></tbody></table>' +
                '</div>');
            
            $.each(person.seasons, function(iter, item) {
                $('#documents-table tbody').append('<tr class="document-row">' + 
                    '<td>' + item.year + '</td>' +
                    '<td>' + item.role + '</td>' +
                    '<td>' + item.story + '</td>' +
                    '</tr>');
            });

        };
    },
};


var timeout;

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

});