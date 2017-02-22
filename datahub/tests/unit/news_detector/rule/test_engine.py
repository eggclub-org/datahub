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

from datahub.news_detector.rule import engine
from datahub.news_detector.rule import article
from datahub.tests import base


class RuleEngineTestCase(base.TestCase):

    @mock.patch.object(article.Article, 'process',
                       side_effect=article.ArticleException)
    def test_detect_article_false(self, mock_process):
        en = engine.Engine()
        res = en.detect(self.context, target_url="foobar", is_article=True)

        self.assertIsNone(res)
        mock_process.assert_called_once_with()

    @mock.patch.object(article.Source, 'process')
    def test_detect_domain_false_bad_url(self, mock_process):
        en = engine.Engine()

        res = en.detect(self.context, target_url="foobar", is_article=False)

        self.assertIsNone(res)
        self.assertFalse(mock_process.called)
