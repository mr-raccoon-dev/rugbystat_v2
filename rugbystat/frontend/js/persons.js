$().ready(function() {

// $('div.date').datepicker({
//   locale: 'ru',
//   pickTime: false,
//   format: "dd.mm.yyyy", 
// });

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
            $('#results').append('<div class="search-item"><a href="/persons/' + item.id + '/">' 
                + item.__str__ + '</a></div>');
        });

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

$('.editable').click(function() {
    var selector = this.id + 'Form';
    $("#" + selector).show();
    $("#submitForm").show();
})

$('#showPersonSeasonForm').click(function() {
    $(this).hide();
    $("#addPersonSeason").show();
})

});