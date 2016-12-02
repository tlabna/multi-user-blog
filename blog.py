import webapp2

from handlers.bloghandler import BlogHandler
from handlers.loginhandler import Login, Logout
from handlers.signuphandler import Signup, Register, Welcome
from handlers.posthandler import NewPost, PostPage, EditDeletePost, DeletePost, CommentHandler, EditCommentHandler, DeleteCommentHandler
from handlers.likehandler import LikeHandler
from handlers.util import users_key
from models.models import Post, User

from google.appengine.ext import ndb

# Start page for Blog


class BlogFront(BlogHandler):
    def get(self):
        # passing user_id to template for checks to show(or not) edit, like and
        # comment buttons
        user_id = self.getUserId()
        posts = Post.query().order(-Post.created)

        if user_id:
            username = User.get_by_id(user_id, parent=users_key()).name
            self.render('front.html', posts=posts,
                        user_id=user_id, username=username)
        else:
            self.render('front.html', posts=posts, user_id=user_id)

    def post(self):
        action = self.request.get('action')
        post_id = self.request.get('post_id')
        user_id = self.getUserId()

        # If logged out user tries to create, edit, delete, or like a blog
        # post, they are redirected to login page
        if not self.getUserId():
            self.redirect('/login')

        # If user clicks on edit/delete button redirect to edit page
        if action == 'edit/delete':
            self.redirect('/blog/edit/%s' % post_id)

# URL Handler
app = webapp2.WSGIApplication([('/blog/?', BlogFront),
                               ('/blog/(\d+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/welcome', Welcome),
                               ('/blog/edit/(\d+)', EditDeletePost),
                               ('/postdelete.html', DeletePost),
                               ('/like', LikeHandler),
                               ('/comment', CommentHandler),
                               ('/editcomment', EditCommentHandler),
                               ('/deletecomment', DeleteCommentHandler)
                               ],
                              debug=True)
