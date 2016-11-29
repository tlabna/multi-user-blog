''' Module to handle User likes '''
import json

from models.models import Post
from handlers.bloghandler import BlogHandler
from handlers.util import blog_key


class LikeHandler(BlogHandler):
    def post(self):
        post_id = int(self.request.get('post_key'))
        user_id = self.getUserId()
        post = Post.get_by_id(post_id, parent=blog_key())

        # Check if user has already liked post
        if user_id in post.liked_by:
            post.likes -= 1
            post.liked_by.remove(user_id)
            self.user.likes.remove(post_id)
            self.write(json.dumps(({'likes': post.likes})))
            post.put()
            self.user.put()
        else:
            post.likes += 1
            post.liked_by.append(user_id)
            self.user.likes.append(post_id)
            self.write(json.dumps(({'likes': post.likes})))
            post.put()
            self.user.put()
