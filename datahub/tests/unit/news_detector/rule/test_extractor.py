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

import mock
from mock import sentinel

from datahub.news_detector.rule import config
from datahub.news_detector.rule import extractor
from datahub.news_detector.rule.parser import ObjectParser
from datahub.news_detector.rule.parser import Parser

from datahub.tests import base


class RuleExtractorTestCase(base.TestCase):

    def setUp(self):
        super(RuleExtractorTestCase, self).setUp()
        self.doc = sentinel.fake_doc
        self.ele = sentinel.fake_ele
        self.extractor = extractor.Extractor(config.SourceConfig())

    @mock.patch.object(Parser, 'getElementsByTag',
                       return_value=None)
    def test_get_title_no_title_element(self, mock_get):
        res = self.extractor.get_title(self.doc)

        self.assertEqual('', res)
        mock_get.assert_called_once_with(self.doc, tag='title')

    @mock.patch.object(Parser, 'xpath_re')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_title_by_title_element(self, mock_get, mock_xpath):
        fake_title = ObjectParser(self.ele, 'fake_title_ele', 'fake_title')
        fake_h1 = ObjectParser(self.ele, 'fake_h1_ele', 'fake_title')
        fake_fb = ObjectParser(self.ele, 'fake_fb_ele', 'fake_fb')

        mock_get.side_effect = [[fake_title], [fake_h1]]
        mock_xpath.return_value = [fake_fb]

        res = self.extractor.get_title(self.doc)

        self.assertEqual('fake_title_ele', res)
        mock_get.assert_has_calls([mock.call(self.doc, tag='title'),
                                   mock.call(self.doc, tag='h1')])
        mock_xpath.assert_called_once_with(self.doc, '//meta['
                                                     '@property="og:title"]'
                                                     '/@content')
