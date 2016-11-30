''' All models are stored here '''

from google.appengine.ext import ndb
from handlers.util import *


# User Model
class User(ndb.Model):
    name = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    email = ndb.StringProperty()
    likes = ndb.IntegerProperty(repeated=True, default=None)

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.query(User.name == name).get()
        return u

    @classmethod
    def register(cls, name, pw, email=None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


class Post(ndb.Model):
    subject = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    author = ndb.KeyProperty(kind=User, required=True)
    likes = ndb.IntegerProperty(default=0)
    # This will take a list of user_ids
    liked_by = ndb.IntegerProperty(repeated=True, default=None)

    def render(self, user_id):
        # Handling cyclical dependencies
        from handlers.bloghandler import render_str
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p=self, user_id=user_id)

    def render_permalink(self):
        # Handling cyclical dependencies
        from handlers.bloghandler import render_str
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p=self)

    def get_comments(self):
        """helper function to display fetch all comments for their respective
        post from the datastore"""
        comments = Comment.query(Comment.post == self.key).order(-Comment.created).fetch()
        return comments


class Comment(ndb.Model):
    content = ndb.StringProperty(required=True)
    author = ndb.KeyProperty(kind = User, required=True)
    post = ndb.KeyProperty(kind = Post, required=True)
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    def render(self, user_id):
        # Handling cyclical dependencies
        from handlers.bloghandler import render_str
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('comment.html', c=self, user_id=user_id)

    # HTML that will be rendered dynamically to show user the comment they just submitted
    def render_single_comment(comment):
        html = '''
                <div class="comment-edit-form col-xs-12" style="display: None">
                    <form method="post" class="edit-form">
                        <textarea name="edit-comment" class="comment-input col-xs-12">%s</textarea>
                        <a href="#" data-commentid="%s" class="save-button">Save</a> |
                        <a href="#" class="cancel-button">Cancel</a>
                    </form>
                  <p class="error"><p>
                </div>
                <div class="comment-single col-xs-12">
                    <p class="grey small border-top">%s said:</p>
                    <p class="comment-content">%s</p>
                    <a href="#" class="edit">Edit</a> |
                    <a href="#" data-comment_id="%s" class="delete">Delete</a>
                </div>
                ''' % (comment.content, comment.key.id(), comment.author.get().name, comment.content, comment.key.id())
        return html
