# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Base class for holding contextual information of a request

This class has several uses:

* Used for storing security information in a web request.
* Used for passing contextual details to oslo.log.

Projects should subclass this class if they wish to enhance the request
context or provide additional information in their specific WSGI pipeline
or logging context.
"""

from eventlet.green import threading
from positional import positional
import uuid

_request_store = threading.local()


def generate_request_id():
    """Generate a unique request id."""
    return 'req-%s' % uuid.uuid4()


class RequestContext(object):

    """Helper class to represent useful information about a request context.

    Stores information about the security context under which the user
    accesses the system, as well as additional request information.
    """

    user_idt_format = u'{user}'

    @positional(enforcement=positional.WARN)
    def __init__(self,
                 auth_token=None,
                 user=None,
                 is_admin=False,
                 read_only=False,
                 show_deleted=False,
                 request_id=None,
                 overwrite=True,
                 roles=None,
                 user_name=None):
        """Initialize the RequestContext

        :param overwrite: Set to False to ensure that the greenthread local
                          copy of the index is not overwritten.
        """
        self.user_id = user

        self.auth_token = auth_token
        self.user_name = user_name
        self.is_admin = is_admin
        self.read_only = read_only
        self.show_deleted = show_deleted
        self.roles = roles or []

        if not request_id:
            request_id = generate_request_id()
        self.request_id = request_id
        if overwrite or not get_current():
            self.update_store()

    def update_store(self):
        """Store the context in the current thread."""
        _request_store.context = self

    def to_dict(self):
        """Return a dictionary of context attributes."""
        user_idt = self.user_idt_format.format(user=self.user_id)

        return {'user': self.user_id,
                'is_admin': self.is_admin,
                'read_only': self.read_only,
                'show_deleted': self.show_deleted,
                'auth_token': self.auth_token,
                'request_id': self.request_id,
                'roles': self.roles,
                'user_identity': user_idt,
                'user_name': self.user_name}

    def get_logging_values(self):
        """Return a dictionary of logging specific context attributes."""
        values = {'user_name': self.user_name}
        values.update(self.to_dict())
        return values

    @classmethod
    def from_dict(cls, values, **kwargs):
        """Construct a context object from a provided dictionary."""
        kwargs.setdefault('auth_token', values.get('auth_token'))
        kwargs.setdefault('user', values.get('user'))
        kwargs.setdefault('is_admin', values.get('is_admin', False))
        kwargs.setdefault('read_only', values.get('read_only', False))
        kwargs.setdefault('show_deleted', values.get('show_deleted', False))
        kwargs.setdefault('request_id', values.get('request_id'))
        kwargs.setdefault('user_name', values.get('user_name'))
        return cls(**kwargs)


def is_user_context(context):
    """Indicates if the request context is a normal user."""
    if not context or not isinstance(context, RequestContext):
        return False
    if context.is_admin:
        return False
    return True


def get_current():
    """Return this thread's current context

    If no context is set, returns None
    """
    return getattr(_request_store, 'context', None)


def make_context(*args, **kwargs):
    return RequestContext(*args, **kwargs)


def make_admin_context(show_deleted=False):
    """Create an administrator context.

    :param show_deleted: if True, will show deleted items when query db
    """
    context = RequestContext(is_admin=True,
                             show_deleted=show_deleted)
    return context
