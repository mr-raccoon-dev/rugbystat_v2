$().ready(function() {

window.PAGE = 1;
window.GETPAGE = true;

var searchDocsManager = {
    get_list: function(page) {
        var q = $("#id_year").val();

        if(window.GETPAGE == true){
            $.getJSON({
                url: documentListUrl + '?year=' + q + '&page=' + page,
                success: function(data) {
                    searchDocsManager.process_list(data);
                },
                error: function() {
                    window.GETPAGE = false;
                }
            });
        };
    },
    process_list: function(data) {
        if(data.count > 0) {
            $.each(data.results, function(iter, item) {
                if(item.date != null){
                    var title = item.title + ' (' + item.date + ')'
                }
                else{
                    var title = item.title
                }
            
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

$('#search-submit-btn').click(function() {
    window.PAGE = 1;
    window.GETPAGE = true;
    $("#documents-table tbody").html('');
    searchDocsManager.get_list(window.PAGE);
});

$().ajaxStart(function() {
    $('#indicator').show();
}).ajaxStop(function() {
    $('#indicator').hide();
});

function yHandler() {
    if(document.body.scrollHeight - window.innerHeight - 50 < window.scrollY){
        window.PAGE += 1;
        searchDocsManager.get_list(window.PAGE);
    }
};

window.onscroll = yHandler;

});