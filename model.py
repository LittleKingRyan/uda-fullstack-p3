import os
import jinja2
from bleach import clean
from markupsafe import Markup
from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


""" this do_clean function is found here:
http://stackoverflow.com/questions/8976683/jinja2-escape-all-html-but-img-b-etc
"""
def do_clean(text, **kw):
    return Markup(clean(text, **kw))

jinja_env.filters['clean'] = do_clean


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Post(db.Model):
    title = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    author = db.StringProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add = True)
    modified_time = db.DateTimeProperty(auto_now_add = True)
    vote_count = db.IntegerProperty(default=0)
    voted_by = db.TextProperty(default='')


class Vote(db.Model):
    post = db.ReferenceProperty(Post, collection_name='votes')
    voter = db.StringProperty(required=True)


class Comment(db.Model):
    post = db.ReferenceProperty(Post, collection_name='comments')
    author = db.StringProperty(required=True)
    created_time = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty(required=True)


class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()
