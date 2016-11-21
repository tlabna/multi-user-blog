import os

import webapp2
import jinja2

from google.appengine.ext import db

# Initializing Jinja and directing to the templates directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BlogHandler (webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **params):
        self.write(self.render_str(template, **params))

# Blog stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p = self)

class BlogFront(BlogHandler):
    def get(self):
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts)

class NewPost(BlogHandler):
    def get(self):
        self.render('newpost.html')

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(parent = blog_key(), subject = subject, content = content)
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = 'Both subject and content must be filled in!'
            self.render('newpost.html', subject = subject, conetent = content, error = error)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent = blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render('permalink.html', post = post)

app = webapp2.WSGIApplication([('/blog/?', BlogFront),
                               ('/blog/(\d+)', PostPage),
                               ('/blog/newpost', NewPost)
                               ],
                              debug=True)
