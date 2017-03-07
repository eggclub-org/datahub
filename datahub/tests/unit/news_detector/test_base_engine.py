# Copyright 2017 EGG Club.
#
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

from datahub import news_detector
from datahub.news_detector.dtree import engine as dtree_engine
from datahub.news_detector.rule import engine as r_engine
from datahub.tests import base


class BaseEngineTestCase(base.TestCase):

    def test_load_engine_from_config(self):
        self.config(engine='foobar', group='news_detector')
        self.assertRaises(NotImplementedError, news_detector.engine)
        self.config(engine='d-tree', group='news_detector')
        self.assertIsInstance(news_detector.engine(), dtree_engine.Engine)
        self.config(engine='rule', group='news_detector')
        self.assertIsInstance(news_detector.engine(), r_engine.Engine)
