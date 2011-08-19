====================
Duende web framework
====================

What is it ?
____________

Duende is a WSGI web framework built on top of Paster. It uses SQLAlchemy
as ORM and Jinja2 for templates.

The main difference with other frameworks is that duende don't use URL to
controller routes as most of python web frameworks do, but instead it uses a
fixed URL dispatching system.

By using a fixed system is not necessary to maintain URL mapping file(s) for
each controller or to inspect files looking for exposed controller instances
or functions. But drawback of using a fixed system is that you loose some
flexibility.


Installation and setup
______________________

To install duende just run:
    pip install duende
or:
    easy_install duende

After you can start a new application named foo by running:
    paster create -t duende foo

You can replace foo for the name of your application, but have in mind that
examples will use foo as application name.

This command is going to create directory with a duende application skeleton
that you can use as a start base.

Inside the new directory you will need to create some folders that are used by
default settings to keep session and template cache. These folders are
var/sessions/data, var/sessions/lock and var/templates/cache.

Settings are stored in a file called duende.ini (you can change the name if you
want). Edit this file to setup values for your specific needs.

After you finish changing settings run:
    paster serve duende.ini

and open http://localhost:8080/ in your browser. You will see a "404 Not Found"
message because there is no view handler to manage the request yet :).


First steps
___________

New create a src/foo/view/root.py file so it looks like:

::

    # -*- coding: utf8 -*-
    from duende.lib.view import utf8_text
    from duende.lib.view import redirect
    from duende.lib.view import restrict

    from foo import url


    @redirect
    def index(request):
        #redirect to /login URL
        return url('/login/')


    @restrict('GET')
    @utf8_text
    def login(request):
        #handle /login requests by printing a text
        return u'Wops ! its just a test'


Save it and open http://localhost:8080/ in your browser. This time you will be
redirected to http://localhost:8080/login/ where a text will be displayed.

Inside your application directory there is a second ini file called urls.ini.
This file "plug" different applications to a base URL, allowing Duende to know
wich application will handle each request.

By default when you access an application base URL like / (for default app), or
/blog/ for an application "plugged" in /blog, Duende will look for a file called
root.py inside that application view directory, and then for a function called
index.
In similar way it will inspect URLs to see mapped application, and then look
inside view directory for a module and a function to handle request. For example,
in case of http://localhost:8080/user/login/ the steps to get handler will be:

- If there is an app plugged to /user use that app function view.root.login() to
  generate response
- Else get app plugged to / URL and use its view.user.login() to generate
  response
