# -*- coding: utf8 -*-
#
# Copyright (c) 2011, Jerónimo José Albi <jeronimo.albi@gmail.com>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of copyright holders nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from sqlalchemy import MetaData
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import object_mapper

META = MetaData()
SESSION = None
ENGINE = None


def execute(sql, **kwargs):
    """Execute an SQL statement in global session context

    SQL parameters are given as keyword arguments.
    Parameter inside SQL statement are given using variable names
    prefixed with a ":" character.

    Example statement:
        SELECT * FROM some_table WHERE id = :id

    """

    result = SESSION.execute(sql, kwargs)

    return result


class BaseModel(object):
    """Base class for models"""

    def __repr__(self):
        cls_name = self.__class__.__name__
        description = str(self)

        if description:
            text = '<%s: %s>' % (cls_name, description)
        else:
            text = '<%s>' % cls_name

        return text

    def __str__(self):
        #call unicode to get value and encode str as UTF8
        return unicode(self).encode('utf8')

    @staticmethod
    def new_session():
        """Create a new Session

        New Sessions must be finished by calling commit()
        or rollback() session methods.

        """

        session = SESSION()

        return session

    @classmethod
    def query(cls, session=None):
        """Get a query instance for current model class"""

        #when noo session is given use global session
        if not session:
            session = SESSION

        query = session.query(cls)

        return query

    @classmethod
    def query_from(cls, statement, session=None):
        """Get a query instance for current model class using select
        statement to get data.
        """

        query = cls.query(session=session)
        query = query.from_statement(statement)

        return query

    @classmethod
    def get(cls, *args, **kw):
        """Shortcut to get a model instance using SQLAlchemy
        ORM model get method.

        Session can be given as keyword argument.

        """

        session = None
        if 'session' in kw:
            session = kw['session']
            del kw['session']

        query = cls.query(session=session)

        return query.get(*args, **kw)

    @property
    def current_session(self):
        """Get current instance Session"""

        session = SESSION.object_session(self)

        return session


# define base model class for declarative definitions
DeclarativeModel = declarative_base(name="DeclarativeModel", cls=BaseModel)


class IterableModel(BaseModel):
    """Base class for models to allow iteration of fields.

    This allow to convert a model instance to dict using dict
    function on model instances.

    """

    def __iter__(self):
        self._mapper = object_mapper(self)
        self._col_iter = iter(self._mapper.columns)

        return self

    def next(self):
        #skip non public properties
        column = self._col_iter.next()
        mapper_property = self._mapper.get_property_by_column(column)
        field_name = mapper_property.key

        while field_name.startswith('_'):
            column = self._col_iter.next()
            mapper_property = self._mapper.get_property_by_column(column)
            field_name = mapper_property.key

        field_value = getattr(self, field_name)

        return (field_name, field_value)


# define base model class for iterable declarative definitions
IterableDeclarativeModel = declarative_base(
    name="IterableDeclarativeModel",
    cls=IterableModel,
)


def init_database_engine(config):
    """Initialize connection to database"""

    global ENGINE

    engine_kwds = {
        'prefix': u'database.',
        'convert_unicode': True,
    }
    ENGINE = engine_from_config(config.copy(), **engine_kwds)


def init_database_session():
    """Init connection with database"""

    global SESSION

    SESSION = scoped_session(sessionmaker())
    SESSION.configure(bind=ENGINE)


def clean_database_session():
    """Cleans any pending transactions and return connections to the pool"""

    SESSION.remove()


def create_all_tables():
    """Create tables that are not created yet"""

    META.create_all(ENGINE)
