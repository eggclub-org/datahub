#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from datahub.common import context as dh_context
from datahub.tests import base


class ContextTestCase(base.BaseTestCase):

    def _create_context(self, roles=None):
        return dh_context.RequestContext(auth_token='auth_token1',
                                         user_name='user1',
                                         roles=roles,
                                         is_admin=False,
                                         read_only=True,
                                         show_deleted=True,
                                         request_id='request_id1')

    def test_context(self):
        ctx = self._create_context()

        self.assertEqual("auth_token1", ctx.auth_token)
        self.assertEqual("user1", ctx.user_name)
        self.assertEqual([], ctx.roles)
        self.assertFalse(ctx.is_admin)
        self.assertTrue(ctx.read_only)
        self.assertTrue(ctx.show_deleted)
        self.assertEqual("request_id1", ctx.request_id)

    def test_context_with_roles(self):
        ctx = self._create_context(roles=['admin', 'service'])

        self.assertEqual("auth_token1", ctx.auth_token)
        self.assertEqual("user1", ctx.user_name)
        for role in ctx.roles:
            self.assertIn(role, ['admin', 'service'])
        self.assertFalse(ctx.is_admin)
        self.assertTrue(ctx.read_only)
        self.assertTrue(ctx.show_deleted)
        self.assertEqual("request_id1", ctx.request_id)

    def test_to_dict_from_dict(self):
        ctx = self._create_context()
        ctx2 = dh_context.RequestContext.from_dict(ctx.to_dict())

        self.assertEqual(ctx.auth_token, ctx2.auth_token)
        self.assertEqual(ctx.user_name, ctx2.user_name)
        self.assertEqual(ctx.is_admin, ctx2.is_admin)
        self.assertEqual(ctx.read_only, ctx2.read_only)
        self.assertEqual(ctx.roles, ctx2.roles)
        self.assertEqual(ctx.show_deleted, ctx2.show_deleted)
        self.assertEqual(ctx.request_id, ctx2.request_id)

    def test_request_context_sets_is_admin(self):
        ctxt = dh_context.make_admin_context()
        self.assertTrue(ctxt.is_admin)

    def test_context_get_log(self):
        ctx = self._create_context()
        val = ctx.get_logging_values()

        self.assertEqual(ctx.auth_token, val.get('auth_token'))
        self.assertEqual(ctx.user_name, val.get('user_name'))
        self.assertEqual(ctx.is_admin, val.get('is_admin'))
        self.assertEqual(ctx.read_only, val.get('read_only'))
        self.assertEqual(ctx.roles, val.get('roles'))
        self.assertEqual(ctx.show_deleted, val.get('show_deleted'))
        self.assertEqual(ctx.request_id, val.get('request_id'))

    def test_make_context(self):
        ctx = dh_context.make_context(user_name='fake_user')
        self.assertEqual(ctx.user_name, 'fake_user')

    def test_check_user_context(self):
        ctx = self._create_context()
        admin_ctx = dh_context.make_admin_context()

        self.assertFalse(dh_context.is_user_context(None))
        self.assertFalse(dh_context.is_user_context(admin_ctx))
        self.assertTrue(dh_context.is_user_context(ctx))
