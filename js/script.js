/* All JS code for dynamically updating data on blog */

// LIKES

$('.like').on('click', function(e) {
    e.preventDefault();
    var instance = $(this);
    var key = $(this).data('key');

    $.ajax({
        type: "post",
        url: "/like", // Route which will handle the request
        dataType: 'json',
        data: {
            "post_key": key
        },
        success: function(data) {
            instance.find('span').html(data.likes);
        }
    });
});
