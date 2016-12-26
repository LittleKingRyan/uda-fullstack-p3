# Project 3
1. Multi user blog
2. This project is the third homework of Udacity's Full-stack nano degree.

## About Website:
https://uda-fullstack-p3-153101.appspot.com/

    Home page. There's a link, 'Visit Blog' in the top right corner, which takes a user to
    see all the blog posts.

https://uda-fullstack-p3-153101.appspot.com/blog

    Blog Page that lists the top 10 most recent (based on modified time) posts.

    This page has two additional links: 'My Page' and 'New Post'.

    If a logged out user clicks on the 'My Page' or 'New Post' links, he or she will be redirected
    to the sign up page.

    After clicking on the title of a post, a user will presented with the permant link with the url form like:
    https://uda-fullstack-p3-153101.appspot.com/blog/postpage?id=5654313976201216



https://uda-fullstack-p3-153101.appspot.com/signup

    Sign up page.

https://uda-fullstack-p3-153101.appspot.com/login

    Login in page.

    After logging in, a user will be redirected to his or her homepage with all of his or her posts.

    Also, his or her username will appear on the top right corner with a log out link below.

After logging in, a user can comment its or other users' posts. He or she can also delete and/or a post if
the post was made by that him or herself. A user may not like his or her own posts. A user can only like each of  other users' posts only once.

## About Code:
Python code is divided into three files, main.py, auth.py and model.py.

auth.py:

    As the names suggest, auth.py has a bunch of functions that handle the hashing and verifying of cookies and
    passwords. It also deals with verifying if a user's input is valid or not.

model.py:

    model.py defines the jinja environment and datastore classes.

Additionally, there is a python file called play.py, in which I write and test certain functions.