# All Rights Reserved.
#
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

import mock
import oslo_messaging as messaging
from oslo_serialization import jsonutils

from datahub.common import context
from datahub.common import mq
from datahub.tests import base


class TestMQ(base.TestCase):

    @mock.patch.object(mq, 'RequestContextSerializer')
    @mock.patch.object(messaging, 'RPCClient')
    def test_get_client(self, mock_client, mock_ser):
        mq.TRANSPORT = mock.Mock()
        tgt = mock.Mock()
        ser = mock.Mock()
        mock_client.return_value = 'client'
        mock_ser.return_value = ser

        client = mq.get_client(tgt, version_cap='1.0', serializer='foo',
                               timeout=6969)

        mock_ser.assert_called_once_with('foo')
        mock_client.assert_called_once_with(mq.TRANSPORT,
                                            tgt, version_cap='1.0',
                                            serializer=ser, timeout=6969)
        self.assertEqual('client', client)

    def test_get_notifier(self):
        mq.init(base.CONF)
        self.assertIsNotNone(mq.TRANSPORT)
        self.assertIsNotNone(mq.NOTIFIER)
        self.config(host=None)

        notifier = mq.get_notifier(service='foobar', host='::1')

        self.assertEqual(notifier.publisher_id, 'foobar.::1')

    @mock.patch.object(mq, 'RequestContextSerializer')
    @mock.patch.object(messaging, 'get_rpc_server')
    def test_get_server(self, mock_get, mock_ser):
        mq.TRANSPORT = mock.Mock()
        ser = mock.Mock()
        tgt = mock.Mock()
        ends = mock.Mock()
        mock_ser.return_value = ser
        mock_get.return_value = 'server'

        server = mq.get_server(tgt, ends, serializer='foo')

        mock_ser.assert_called_once_with('foo')
        mock_get.assert_called_once_with(mq.TRANSPORT, tgt, ends,
                                         executor='eventlet', serializer=ser)
        self.assertEqual('server', server)

    def test_cleanup_transport_null(self):
        mq.TRANSPORT = None
        mq.NOTIFIER = mock.Mock()
        self.assertRaises(AssertionError, mq.cleanup)

    def test_cleanup_notifier_null(self):
        mq.TRANSPORT = mock.Mock()
        mq.NOTIFIER = None
        self.assertRaises(AssertionError, mq.cleanup)

    def test_cleanup(self):
        mq.NOTIFIER = mock.Mock()
        mq.TRANSPORT = mock.Mock()
        trans_cleanup = mock.Mock()
        mq.TRANSPORT.cleanup = trans_cleanup

        mq.cleanup()

        trans_cleanup.assert_called_once_with()
        self.assertIsNone(mq.TRANSPORT)
        self.assertIsNone(mq.NOTIFIER)

    def test_add_extra_exmods(self):
        mq.EXTRA_EXMODS = []

        mq.add_extra_exmods('foo', 'bar')

        self.assertEqual(['foo', 'bar'], mq.EXTRA_EXMODS)

    def test_clear_extra_exmods(self):
        mq.EXTRA_EXMODS = ['foo', 'bar']

        mq.clear_extra_exmods()

        self.assertEqual(0, len(mq.EXTRA_EXMODS))

    def test_serialize_entity(self):
        with mock.patch.object(jsonutils, 'to_primitive') as mock_prim:
            mq.JsonPayloadSerializer.serialize_entity('context', 'entity')

        mock_prim.assert_called_once_with('entity', convert_instances=True)


class TestRequestContextSerializer(base.BaseTestCase):
    def setUp(self):
        super(TestRequestContextSerializer, self).setUp()
        self.mock_base = mock.Mock()
        self.ser = mq.RequestContextSerializer(self.mock_base)
        self.ser_null = mq.RequestContextSerializer(None)

    def test_serialize_entity(self):
        self.mock_base.serialize_entity.return_value = 'foo'

        ser_ent = self.ser.serialize_entity('context', 'entity')

        self.mock_base.serialize_entity.assert_called_once_with('context',
                                                                'entity')
        self.assertEqual('foo', ser_ent)

    def test_serialize_entity_null_base(self):
        ser_ent = self.ser_null.serialize_entity('context', 'entity')

        self.assertEqual('entity', ser_ent)

    def test_deserialize_entity(self):
        self.mock_base.deserialize_entity.return_value = 'foo'

        deser_ent = self.ser.deserialize_entity('context', 'entity')

        self.mock_base.deserialize_entity.assert_called_once_with('context',
                                                                  'entity')
        self.assertEqual('foo', deser_ent)

    def test_deserialize_entity_null_base(self):
        deser_ent = self.ser_null.deserialize_entity('context', 'entity')

        self.assertEqual('entity', deser_ent)

    def test_serialize_context(self):
        context = mock.Mock()

        self.ser.serialize_context(context)

        context.to_dict.assert_called_once_with()

    @mock.patch.object(context, 'RequestContext')
    def test_deserialize_context(self, mock_req):
        self.ser.deserialize_context('context')

        mock_req.from_dict.assert_called_once_with('context')
