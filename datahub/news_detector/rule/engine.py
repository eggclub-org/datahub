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

from newspaper import Article
from newspaper import Source

from datahub.news_detector import engine_base
from datahub.news_detector.rule.config import SourceConfig

import datahub.conf

CONF = datahub.conf.CONF


class Engine(engine_base.Engine):

    def __init__(self):
        self.config = SourceConfig()

    def detect(self, context, target_url, is_article=False):
        if is_article:
            article = Article(target_url, config=self.config)
            article.download()
            article.parse()
        else:
            src = Source(target_url, config=self.config)
            src.download()
            src.parse()
