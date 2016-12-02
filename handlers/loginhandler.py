''' Module that handles logging in '''

from handlers.bloghandler import BlogHandler
from models.models import User


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
            self.render('login-form.html', error=msg, username=username)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/login')
