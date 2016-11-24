import os
import hashlib
import hmac
import random
from string import letters
import re

import webapp2
import jinja2

from google.appengine.ext import db

# Initializing Jinja and directing to the templates directory
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

secret = 'eyDMx2uZBm0MOw6Da9Hg'

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class BlogHandler (webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **params):
        self.write(self.render_str(template, **params))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie',
                                         '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))

    def getUserId(self):
        user_id = self.read_secure_cookie('user_id')
        if user_id:
            return int(user_id.split('|')[0])
        else:
            return None

# User Stuff

def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

def users_key(group = 'default'):
    return db.Key.from_path('users', group)

class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    @classmethod
    def by_id(cls, uid):
        return User.get_by_id(uid, parent = users_key())

    @classmethod
    def by_name(cls, name):
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

# Blog Stuff

def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)
    author = db.ReferenceProperty(User, required = True)

    def render(self, user_id):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p = self, user_id = user_id)

    def render_permalink(self):
        self._render_text = self.content.replace('\n', '<br>')
        return render_str('post.html', p = self)

# Handlers

class BlogFront(BlogHandler):
    def get(self):
        # passing user_id to template for checks to show(or not) edit, like and comment buttons
        user_id = self.getUserId()
        posts = Post.all().order('-created')
        self.render('front.html', posts = posts, user_id = user_id)

    def post(self):
        action = self.request.get('action')
        post_id = self.request.get('post_id')

        # If logged out user tries to create, edit, delete, or like a blog post, they are redirected to login page
        if not self.getUserId():
            self.redirect('/login')

        # If user clicks on edit/delete button redirect to edit page
        if action == 'edit/delete':
            self.redirect('/blog/edit/%s' % post_id)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render('newpost.html')
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(parent = blog_key(), subject = subject, content = content, author = self.user.key())
            post.put()
            self.redirect('/blog/%s' % str(post.key().id()))
        else:
            error = 'Both subject and content must be filled in!'
            self.render('newpost.html', subject = subject, conetent = content, error = error)

class PostPage(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent = blog_key())
        post = Post.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post, user_id = post.author.key().id())

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class Signup(BlogHandler):
    def get(self):
        self.render('signup-form.html')

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username = self.username, email = self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Passwords don't match. Try again."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError

class Register(Signup):
    def done(self):
        #make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/blog/welcome')

class Login(BlogHandler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login. Try again.'
            self.render('login-form.html', error = msg)

class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/login')

class Welcome(BlogHandler):
    def get(self):
        if self.user:
            self.render('welcome.html', username = self.user.name)
        else:
            self.redirect('/signup')

class EditDeletePost(BlogHandler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        user_id = self.getUserId()

        if not post:
            self.error(404)
            return

        # Checking if the current user is in fact the author of the post, if not redirect to blog
        if post.author.key().id() == user_id:
            self.render("editpost.html", subject = post.subject, content = post.content)
        else:
            self.redirect('/login')

    def post(self, post_id):
        subject = self.request.get('subject')
        content = self.request.get('content')
        action = self.request.get('action')
        post_key = db.Key.from_path('Post', int(post_id), parent = blog_key())
        user_id = self.getUserId()

        # If logged out or incorrect user user tries to edit, delete a blog post, they are redirected to login page
        if (not user_id) or (post_id != user_id):
            self.redirect('/login')
            return

        if action == 'save edit':
            if subject and content:
                # Updating post entity in DB
                post = db.get(post_key)
                post.subject = subject
                post.content = content
                post.put()

                self.redirect('/blog/%s' % str(post.key().id()))
            else:
                error = 'Both subject and content must be filled in!'
                self.render('editpost.html', subject = subject, content = content, error = error)

        if action == 'delete':
            db.delete(post_key)
            self.redirect('/postdelete.html')

class DeletePost(BlogHandler):
    def get(self):
        self.render('postdelete.html')

app = webapp2.WSGIApplication([('/blog/?', BlogFront),
                               ('/blog/(\d+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ('/blog/welcome', Welcome),
                               ('/blog/edit/(\d+)', EditDeletePost),
                               ('/postdelete.html', DeletePost)
                               ],
                              debug=True)
