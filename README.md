# Flask-Admin WalrusModel

[Walrus](https://github.com/coleifer/walrus) model backend for the
[Flask-Admin](https://github.com/flask-admin/flask-admin/)
**(Note: Work in progress!)**

  * **[Walrus](https://github.com/coleifer/walrus)** is a set of Python
    wrappers for working with Redis and other Redis-like KVS databases
  * **[Flask-Admin](https://github.com/flask-admin/flask-admin/)** is an
    easy-to-use admin interface for the [Flask](http://flask.pocoo.org)
    web framework
  * If you don't know what **Flask** is, this repo is probably not for
    you! ;-)

## Introduction

I'm working on a Flask project that makes use of
([rlite](https://github.com/seppo0010/rlite-py)-backed) Walrus models,
and I thought it would be useful to have a generic interface to make the
data manageable with Flask-Admin. So this is primarily to work in my
project, but hopefully it will be useful elsewhere, too.  This is my
first "real" extension so please bear with all the rough edges!

## Setup

***Note:** this project is still work-in-progress, so don't expect it to
work completely even after you set it up!*

The main module is inside the "walrusadmin" folder. Place this in your
`PYTHON_PATH` to get it working. You can then set up your models for
Flask-Admin like so:

    from walrusadmin import ModelView

    # MyModel is the model you want to manage
    from models import MyModel
    
    # ...set up Flask app, Flask-Admin, etc here... #

    admin.add_view(ModelView(MyModel))

You can, of course, subclass `walrusadmin.ModelView` to customize it, as
with any other Flask-Admin ModelView backend

    class UserAdmin(ModelView):
        # ... some config here ...#

    admin.add_view(UserAdmin(MyModel))

For a full example, see the `testapp.py` file—which is also what I'm
using to check that the admin interface works (no, I haven't got the hang
of unittests yet).

## Contributing

***Note:** Since I don't have Redis installed, I'm using
[rlite](https://github.com/seppo0010/rlite-py) to test
the scripts. You will need to either have the `hirlite` python package
installed, or edit testapp.py to use an actual Redis database.*

I'm still at the beginning stage of coding. Of course, any help would be
appreciated :-)

And I'm still new to development, so don't worry about messing with my
coding style: I don't have one yet!
    
