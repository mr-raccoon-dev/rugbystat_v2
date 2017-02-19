$().ready(function() {

var searchDocsManager = {
    get_list: function(page) {
        var year = $("#id_year").val(),
            source = $("#id_source").val(),
            source_type = $("#id_source_type").val(),
            query_params = {'page': page};

        if(year != '') {
            query_params['year'] = year;
        };
        if(source != '') {
            query_params['source'] = source;
        };
        if(source_type != '') {
            query_params['source__type'] = source_type;
        };

        // console.log(query_params);

        if(window.GETPAGE == true){
            $.getJSON({
                url: documentListUrl,
                data: query_params,
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

                if (item.description == null) {
                    var description = "";
                } else {
                    var description = item.description.replace(/(\r\n|\n|\r)/gm, "<br>");
                };

                $('#documents-table tbody').append('<tr class="document-row">' + 
                    '<td>' + item.title + '</td>' +
                    '<td>' + description + '</td>' +
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

function yHandler() {
    if(document.body.scrollHeight - window.innerHeight - 50 < window.scrollY){
        window.PAGE += 1;
        searchDocsManager.get_list(window.PAGE);
    }
};

window.onscroll = yHandler;
});
