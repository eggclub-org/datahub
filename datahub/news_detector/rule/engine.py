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

from oslo_log import log as logging

from datahub.news_detector import engine_base
from datahub.news_detector.rule.article import Article
from datahub.news_detector.rule.article import ArticleException
from datahub.news_detector.rule.article import Source
from datahub.news_detector.rule.config import SourceConfig
from datahub.news_detector.rule.extractor import Extractor

import datahub.conf

CONF = datahub.conf.CONF
LOG = logging.getLogger(__name__)


class Engine(engine_base.Engine):

    def __init__(self):
        self.config = SourceConfig()
        self.extractor = Extractor(self.config)

    def detect(self, context, target_url, is_article=False):
        if is_article:
            article = Article(target_url, config=self.config,
                              extractor=self.extractor)
            try:
                article.process()
            except ArticleException:
                LOG.error("There are something wrong with %s" % target_url)
                article = None
            return article
        else:
            try:
                src = Source(target_url, config=self.config,
                             extractor=self.extractor)
                result = src.process()
            except Exception:
                LOG.error("There are something wrong with %s" % target_url)
                result = None
            return result
