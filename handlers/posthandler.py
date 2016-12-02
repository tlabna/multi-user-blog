import json

from google.appengine.ext import ndb
from models.models import Post, Comment
from handlers.bloghandler import BlogHandler
from handlers.util import *


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render('newpost.html', user_id=self.user.key.id(),
                        username=self.user.name)
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            post = Post(parent=blog_key(), subject=subject,
                        content=content, author=self.user.key)
            post.put()
            self.redirect('/blog/%s' % str(post.key.id()))
        else:
            error = 'Both subject and content must be filled in!'
            self.render('newpost.html', subject=subject,
                        conetent=content, error=error)


class PostPage(BlogHandler):
    def get(self, post_id):
        key = ndb.Key('Post', int(post_id), parent=blog_key())
        post = key.get()

        # Would be hard to get to permalink without being logged in, However,
        # if hacker knows id of post they could technically modify a post.
        # Therefore, redirect if not logged in user
        if not self.user:
            self.redirect('/login')

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post,
                    user_id=post.author.id(), username=self.user.name)


class EditDeletePost(BlogHandler):
    def get(self, post_id):
        post_id = int(post_id)
        post = Post.get_by_id(post_id, parent=blog_key())
        user_id = self.getUserId()

        if not post:
            self.error(404)
            return

        # Checking if the current user is in fact the author of the post, if
        # not redirect to blog
        if post.author.id() == user_id:
            self.render("editpost.html", subject=post.subject,
                        content=post.content, user_id=user_id, username=self.user.name)
        else:
            self.redirect('/login')

    def post(self, post_id):
        subject = self.request.get('subject')
        content = self.request.get('content')
        action = self.request.get('action')
        post_key = ndb.Key('Post', int(post_id), parent=blog_key())
        user_id = self.getUserId()
        post = post_key.get()

        # If logged out or incorrect user user tries to edit, delete a blog
        # post, they are redirected to login page
        if (not user_id) or (post.author.id() != user_id):
            self.redirect('/login')
            return

        if action == 'save edit':
            if subject and content:
                # Updating post entity in DB
                post.subject = subject
                post.content = content
                post.put()

                self.redirect('/blog/%s' % str(post.key.id()))
            else:
                error = 'Both subject and content must be filled in!'
                self.render('editpost.html', subject=subject,
                            content=content, error=error)

        if action == 'delete':
            post_key.delete()
            self.render('/postdelete.html', user_id=user_id,
                        username=self.user.name)


class DeletePost(BlogHandler):
    def get(self):
        self.render('postdelete.html')


# Comment Handlers

class CommentHandler(BlogHandler):
    def post(self):
        # If not a logged in user redirect to login
        if not self.user:
            self.redirect('/login')
        else:
            comment = self.request.get('comment')
            post_id = int(self.request.get('post_id'))
            post = Post.get_by_id(post_id, parent=blog_key())
            author = self.user
            if not comment:
                return  # do nothing if empty comment
            else:
                c = Comment(content=comment, author=author.key, post=post.key)
                c.put()
                comment = Comment.render_single_comment(c)
                # return JSON to Ajax
                self.write(json.dumps(({'comment': comment})))


class EditCommentHandler(BlogHandler):
    def post(self):
        if not self.user:
            self.redirect('/login')
        else:
            comment_id = int(self.request.get('comment_id'))
            new_comment = self.request.get('new_comment')
            comment = Comment.get_by_id(comment_id)
            if comment:
                if comment.author.id() == self.user.key.id():
                    comment.content = new_comment
                    comment.put()
                    self.write(json.dumps(
                        ({'comment': self.render_comment(comment.content)})))
            else:
                self.write(json.dumps(({'comment': "There was no comment"})))

    def render_comment(self, comment):
        """ Function to render line breaks just as posts"""
        comment = comment.replace('\n', '<br>')
        return comment


class DeleteCommentHandler(BlogHandler):
    def post(self):
        if not self.user:
            self.redirect('/login')
        else:
            comment_id = int(self.request.get('comment_id'))
            comment = Comment.get_by_id(comment_id)

            if self.user.key.id() == comment.author.id():
                comment.key.delete()
                self.write(json.dumps(({'success': 'Comment deleted'})))
