from google.appengine.ext import ndb
from handlers.util import *

from models.user import User


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
        print 'GOING TO RENDER_STR'
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p=self, user_id=user_id)

    def render_permalink(self):
        # Handling cyclical dependencies
        from handlers.bloghandler import render_str
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p=self)
