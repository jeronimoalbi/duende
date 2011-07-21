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
or functions. But drawback of using a fixed system is that you loose
flexibility.
