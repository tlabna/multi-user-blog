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
$('.submit-button').on('click', function(e) {
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
        data: { "post_id": post_id, "comment": comment },
        success: function(data) {
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

// Edit comments

// Show edit form when user clicks on edit and hide comment
$('.comment-list').on('click', '.edit', function(e) {
    e.preventDefault();
    $(this).parent().prev('div.comment-edit-form').toggle('display');
    $(this).parent().toggle('display');
});

// Submit edit to backend and dynamically update and store in DB
$('.comment-list').on('click', '.save-button', function(e) {
    e.preventDefault();
    var commentText = $(this).prev('textarea.comment-input').val();
    // Check if the user is submitting and empty comment (i.e. they are trying to delete by submitting a empty comment). If not then Post else notify user.
    if ($.trim(commentText).length > 0) {
        var commentDiv = $(this).parent().parent().next('div.comment-single');
        var commentEditForm = $(this).parent().parent();
        var commentID = $(this).data('comment_id');
        $.ajax({
            type: "post",
            url: "/editcomment",
            dataType: 'json',
            data: { "comment_id": commentID, "new_comment": commentText },
            success: function(data) {
                commentDiv.find('p.comment-content').html(data.comment);
                commentDiv.toggle('display');
                commentEditForm.toggle('display');
            },
            error: function(err) {
                console.log(err);
                console.log('There was a problem with this comment');
            }
        });
    } else {
        $(this).parent().next().text("Trying to delete your comment? Please use the delete button.");
        $(this).parent().next().toggle(1400, function() {
            $(this).parent().next('.error').text("");
            $(this).parent().next('.error').toggle(0);
        });
    }
});

// Cancel editing a comment
$('.comment-list').on('click', '.cancel-button', function(e) {
    e.preventDefault();
    $(this).parent().parent().next('div.comment-single').toggle('display');
    $(this).parent().parent().toggle('display');
});

// Delete comments
$('.comment-list').on('click', '.delete', function(e) {
    e.preventDefault();
    var commentID = $(this).data('comment_id');
    var commentDiv = $(this).parent();
    $.ajax({
        type: "post",
        url: "/deletecomment",
        dataType: 'json',
        data: { "comment_id": commentID },
        success: function(data) {
            commentDiv.remove();
            // For logging purposes
            //console.log(data.success);
        },
        error: function(err) {
            console.log(err);
            console.log('There was a problem');
        }
    });
});
