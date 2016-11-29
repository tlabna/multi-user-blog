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

// COMMENTS

// show form to enter comment and remove placeholder when clicked
$('.comment-placeholder').on('click', function(e) {
    var commentForm = $(this).parent().find('.comment-input-form');
    commentForm.css('display', 'block');
    commentForm.find('.comment-input').focus();
    // log form for debugging
    // console.log(commentForm.html());
    $(this).css('display', 'none');
});

// Submit comments then dynamically update comments and save to db
$('.submit-button').on('click', function(e){
  e.preventDefault();
  var comment = $(this).parent().find('.comment-input').val();
  var post_id = $(this).data('postid');
  var commentForm = $(this).parent().parent();
  // log comment
  //console.log(comment);
  $.ajax({
    type: "post",
    url: "/comment",
    dataType: 'json',
    data: {"post_id": post_id, "comment": comment},
    success: function(data){
      commentForm.css('display', 'none');
      commentForm.prev('.comment-placeholder').css('display', 'block');
      commentForm.find('textarea').val('');
      commentForm.parent().find('div.comment-list').prepend(data.comment);
    }
  });
});

// Reverse display when user clicks on cancel
$('.cancel-comment').on('click', function(e) {
  e.preventDefault();
  $('.comment-input-form').css('display', 'none');
  $('.comment-placeholder').css('display', 'block');
});
