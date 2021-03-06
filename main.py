import webapp2
from model import *
from auth import *
from datetime import datetime

class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def cookie_master(self):
        """ gets and verfies cookies so that only valid
            users can access certain functions """
        id_hash_username = self.request.cookies.get('user_id')
        # if user_id cookie exists
        if id_hash_username is not None:
            if cookie_verify(id_hash_username):
                id_hash_user_list = id_hash_username.split("|")
                try:
                    id = int(id_hash_user_list[0])
                except ValueError:
                    return False
                user = User.get_by_id(id)
                if user.username == id_hash_user_list[2]:
                    return True, id_hash_username
                else:
                    return False
            else:
                return False
        else:
            return False

    def get_username_from_cookie(self):
        # use this method after cookie_master() method returns true
        # This method returns the username contained in the uesr_id cookie
        _, id_hash_username = self.cookie_master()
        username = id_hash_username.split("|")[2]
        return username


class SignUp(BlogHandler):
    def get(self):
        return self.render("signup.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username=username,
                      email=email)

        # check to see if an user with the same username already exists or not
        q = User.gql("WHERE username = :username", username=username)
        user_exist = q.get()

        if user_exist:
            params["user_exist"] = "<b>'%s'</b> already exists." % username
            # if the same username already exists, set username to empty string
            params["username"] = ""
            have_error = True
        if not input_valid_username(username):
            params["error_username"] = "Not a valid username."
            have_error = True
        if not input_valid_password(password):
            params["error_password"] = "Not a valid password."
            have_error = True
        elif password != verify:
            params["error_verify"] = "Passwords did not match."
            have_error = True
        if not input_valid_email(email):
            params['error_email'] = "Not a valid email."
            have_error = True

        if have_error:
            return self.render('signup.html', **params)
        else:
            # if user's inputs are correct, then hash the password
            # and then create an user entity in the User relation
            pw_hash = make_pw_hash(username, password)
            user = User(username=username, password=pw_hash)
            user.put()
            # get the user id and then use it to set a cookie
            user_id = user.key().id_or_name()
            self.response.set_cookie("user_id",
                                     cookie_hash(str(user_id), username))
            # redirect user to his or her homepage
            return self.redirect("/blog/my")


class Login(BlogHandler):
    def get(self):
        return self.render("login.html")

    def post(self):
        """ Use the user's input username to select the user stored
            and hash the user's input password to compare with the
            stored hashed password """
        username = self.request.get("username")
        password = self.request.get("password")
        q = User.gql("WHERE username = :username", username=username)
        user = q.get()
        if user:
            pw_hash = user.password
            if valid_pw_hash(username, password, pw_hash):
                user_id = user.key().id_or_name()
                self.response.set_cookie('user_id',
                                         cookie_hash(str(user_id), username))
                return self.redirect("/blog/my")
            else:
                error_password = 'Invalid password'
                self.render("login.html",
                            username=username,
                            error_password=error_password)
        else:
            error_username = 'User does not exist.'
            return self.render("login.html", error_username=error_username)


class Logout(BlogHandler):
    def get(self):
        if self.cookie_master():
            # delete all cookies
            self.response.delete_cookie('user_id')
            self.response.delete_cookie('post_id')
            self.response.delete_cookie('comment_id')
            return self.redirect('/')
        else:
            return self.redirect('/login')


class HomePage(BlogHandler):
    def get(self):
        # if the user's logged in, display his or her username at the
        # right corner together with log out link
        if self.cookie_master():
            username = self.get_username_from_cookie()
            return self.render("index.html", username=username)
        else:
            return self.render("index.html")


class Blog(BlogHandler):
    """ This class selects ten most recent posts created and order them
        in descending order."""
    def get(self):
        posts = Post.gql("order by modified_time desc limit 10")
        if self.cookie_master():
            # get the current logged in user's username for page display
            # control purpose. e.g. if the current logged in user is the
            # same as the author of a post, then show the delete and edit
            # buttons
            username = self.get_username_from_cookie()
            return self.render("blog.html", posts=posts, username=username)
        else:
            return self.render("blog.html", posts=posts)


class MyPage(BlogHandler):
    def get(self):
        if self.cookie_master():
            author = self.get_username_from_cookie()
            my_posts = Post.gql("WHERE author = :author"
                                " ORDER BY modified_time DESC", author=author)
            self.render("my.html",
                        my_posts=my_posts,
                        author=author,
                        username=author)
        else:
            return self.redirect("/login")


class NewPost(BlogHandler):
    """ This class deals with the creating of a new post """
    def get(self):
        if self.cookie_master():
            username = self.get_username_from_cookie()
            return self.render("post.html", username=username)
        else:
            return self.redirect("/signup")

    def post(self):
        if self.cookie_master():
            # current logged in user as the author
            author = self.get_username_from_cookie()

            title = self.request.get("title")
            content = self.request.get("content")

            if title and content:
                # replace the new line character with <br> so that the post
                # will render properly
                content = content.replace("\n", "<br>")
                post = Post(title=title, content=content, author=author)
                post.put()
                # the id of the post just created will be the permalink to
                # that post
                return self.redirect('/blog/postpage?id=%s' % str(post.key().id()))
            else:
                error = 'Both title and content are needed.'
                return self.render("post.html",
                                   title=title,
                                   content=content,
                                   error=error,
                                   username=author)
        else:
            return self.redirect('/login')


class PostPage(BlogHandler):
    def get(self):
        # request: stuff after the ? sign
        request = self.request.query_string
        try:
            post_id = request.split("=")[1]
        except IndexError:
            return self.write("Not Found")

        try:
            post_id = int(post_id)
        except ValueError:
            return self.write("Not Found")

        key = db.Key.from_path('Post', post_id)
        post = db.get(key)

        if not post:
            return self.write("Not Found")

        if self.cookie_master():
            username = self.get_username_from_cookie()
            return self.render("postpage.html", post=post, username=username)
        else:
            return self.render("postpage.html", post=post)

    def post(self):
        """ This post method deals with the liking, commenting functions """
        if self.cookie_master():
            # get the current logged in username from cookie
            username = self.get_username_from_cookie()

            # get the current post on display
            request = self.request.query_string
            try:
                post_id = request.split("=")[1]
            except IndexError:
                return self.write("Not Found")

            try:
                post_id = int(post_id)
            except ValueError:
                return self.write("Not Found")

            # if the request post id does exist, go on and get the post
            # from db using the post_id in the url
            key = db.Key.from_path('Post', post_id)
            post = db.get(key)

            # handling voting form submission
            author = self.request.get("author")
            vote = self.request.get("vote")
            comment = self.request.get("comment")

            # since both liking and commenting are dealt within this post
            # method, an hidden input with name type is used in order to
            # differentiate comment and like
            task_type = self.request.get("type")

            if task_type == "comment":
                if comment:
                    Comment(post=post,
                            author=username,
                            content=comment).put()
                    return self.redirect("/blog/postpage?id=%s" % str(post_id))

                elif not comment:
                    error = "Comment content is needed."
                    return self.render("postpage.html",
                                       post=post,
                                       username=username,
                                       error=error)

            elif task_type == "like":
                # selects all the votes associated with a certain post
                # even though caching is a better thing to do here
                votes = []
                for vote in post.votes:
                    votes.append(vote.voter)

                if author == username:
                    error = "You cannot like your own posts, old sport."
                    return self.render("postpage.html",
                                       post=post,
                                       error=error,
                                       username=username)

                elif username in votes:
                    error = "You have voted for this post already."
                    return self.render("postpage.html",
                                       post=post,
                                       error=error,
                                       username=username)

                elif vote == "up":
                    post.vote_count += 1
                    Vote(post=post, voter=username).put()
                    post.put()

                    msg = "Thanks for supporting!"
                    return self.render("postpage.html",
                                       post=post,
                                       msg=msg,
                                       username=username)
        else:
            return self.redirect("/login")


class DeletePost(BlogHandler):
    """ This class only accpets post method to delete a post """
    def post(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()
            post_id = self.request.get("id")

            try:
                post_id = int(post_id)
            except ValueError:
                return self.redirect("/blog")

            key = db.Key.from_path('Post', post_id)
            post = db.get(key)
            if post.author == current_user:
                db.delete(key)
                return self.redirect("/blog/my")
            else:
                error = "You cannot delete others' posts"
                return self.render("postpage.html", post=post, error=error)
        else:
            return self.redirect("/login")


class EditPost(BlogHandler):
    def get(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()
            request = self.request.query_string
            try:
                post_id = request.split("=")[1]
            except IndexError:
                return self.write("Not Found")

            try:
                post_id = int(post_id)
            except ValueError:
                return self.write("Not Found")

            key = db.Key.from_path('Post', post_id)
            post = db.get(key)
            if not post:
                return self.write("Not Found")
            elif post.author != current_user:
                return self.direct("/blog")
            else:
                # since content is displayed inside textarea, replace
                # <br> with \n
                content = post.content.replace("<br>", "\n")
                self.response.set_cookie("post_id",
                                         cookie_hash(str(post_id),
                                                     post.author))
                return self.render("edit.html",
                                   title=post.title,
                                   content=content,
                                   author=post.author,
                                   post_id=post_id,
                                   username=current_user)
        else:
            return self.redirect('/login')

    def post(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()

            request = self.request.query_string
            try:
                post_id = request.split("=")[1]
            except IndexError:
                return self.write("Not Found")

            title = self.request.get("title")
            content = self.request.get("content")
            author = self.request.get("author")
            id_hash_username = self.request.cookies.get("post_id")

            if author != current_user:
                return self.redirect("/blog")
            if not cookie_verify(id_hash_username):
                return self.redirect("/blog")
            if title and content:
                content = content.replace("\n", "<br>")
                post_id = int(id_hash_username.split("|")[0])
                key = db.Key.from_path('Post', post_id)
                post = db.get(key)
                post.title = title
                post.content = content
                post.modified_time = datetime.now()
                post.put()
                return self.redirect('/blog/postpage?id=%s' % str(post.key().id()))
            else:
                error = 'Both title and content are needed.'
                return self.render("edit.html",
                                   title=title,
                                   content=content,
                                   author=author,
                                   error=error,
                                   post_id=post_id)
        else:
            return self.redirect('/login')


class EditComment(BlogHandler):
    """ This class handles the rendering and changing of a post's comment """
    def get(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()
            # query_string looks like comment_id=123&post_id=456
            request = self.request.query_string
            request_list = request.split("&")
            try:
                comment_id = request_list[0].split("=")[1]
            except IndexError:
                return self.write("Not Found")

            try:
                comment_id = int(comment_id)
            except ValueError:
                return self.write("Not Found")

            key = db.Key.from_path('Comment', comment_id)
            comment = db.get(key)
            if not comment:
                return self.write("Not Found")
            elif comment.author != current_user:
                return self.direct("/blog")
            else:
                # since content is displayed inside textarea, replace
                # <br> with \n
                content = comment.content.replace("<br>", "\n")
                # get the post_id so that when a user cancels on editing,
                # he can be redirected to the post page with this post_id
                post_id = self.request.get("post_id")
                return self.render("editcomment.html",
                                   content=content,
                                   author=comment.author,
                                   comment_id=comment_id,
                                   post_id=post_id,
                                   username=current_user)
        else:
            return self.redirect('/login')

    def post(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()
            request = self.request.query_string
            request_list = request.split("&")
            try:
                comment_id = request_list[0].split("=")[1]
            except IndexError:
                return self.write("Not Found")

            try:
                comment_id = int(comment_id)
            except ValueError:
                return self.write("Not Found")

            content = self.request.get("content")
            author = self.request.get("author")
            post_id = self.request.get("post_id")

            # make sure that users can only edit their own posts
            if author != current_user:
                return self.redirect("/blog")

            # only update when comment content is given
            if content:
                content = content.replace("\n", "<br>")
                key = db.Key.from_path('Comment', comment_id)
                comment = db.get(key)
                comment.content = content
                comment.modified_time = datetime.now()
                comment.put()
                return self.redirect('/blog/postpage?id=%s' % post_id)
            else:
                error = 'Comment content is needed.'
                self.render("editcomment.html",
                            content=content,
                            author=author,
                            error=error,
                            comment_id=comment_id,
                            post_id=post_id)
        else:
            return self.redirect('/login')


class DeleteComment(BlogHandler):
    """ This class only accpets post method to delete a comment """
    def post(self):
        if self.cookie_master():
            current_user = self.get_username_from_cookie()
            comment_id = self.request.get("comment_id")
            post_id = self.request.get("post_id")

            try:
                comment_id = int(comment_id)
            except ValueError:
                return self.redirect("/blog")

            key = db.Key.from_path('Comment', comment_id)
            comment = db.get(key)
            if comment:
                if comment.author == current_user:
                    db.delete(key)
                    return self.redirect('/blog/postpage?id=%s' % post_id)
                else:
                    error = "You cannot delete others' comment"
                    self.render("postpage.html", post=post, error=error)
            else:
                return self.redirect('/blog/postpage?id=%s' % post_id)
        else:
            return self.redirect("/login")


app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/signup', SignUp),
    ('/login', Login),
    ('/blog/logout', Logout),
    ('/blog', Blog),
    ('/blog/post', NewPost),
    ('/blog/postpage', PostPage),
    ('/blog/my', MyPage),
    ('/blog/edit', EditPost),
    ('/blog/edit-comment', EditComment),
    ('/blog/delete', DeletePost),
    ('/blog/delete-comment', DeleteComment)
], debug=False)
