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
from datahub.news_detector.rule.extractor import Extractor

import datahub.conf

CONF = datahub.conf.CONF


class Engine(engine_base.Engine):

    def __init__(self):
        self.config = SourceConfig()
        self.extractor = Extractor(self.config)

    def detect(self, context, target_url, is_article=False):
        if is_article:
            article = Article(target_url, config=self.config)
            article.extractor = self.extractor
            article.download()
            article.build()
        else:
            src = Source(target_url, config=self.config)
            src.extractor = self.extractor
            src.download()
            src.parse()

TARGET = 'http://giaitri.vnexpress.net'
# ARTICLE = 'http://suckhoe.vnexpress.net/tin-tuc/dinh-duong/uong-nuoc-lanh' \
#          '-giup-giam-can-3536234.html'
ARTICLE = 'http://www.baomoi.com/ios-cach-khac-phuc-van-de-dinh-ma-doc-tu' \
          '-redirect-quang-cao-khi-vao-bat-ki-website-nao/c/19620631.epi'
# ARTICLE = 'https://vnhacker.blogspot.com/2017/01/nuoc-my-va-nguoi-nhap-cu' \
#           '.html'


def main():

    eg = Engine()
    eg.detect(None, ARTICLE, True)


if __name__ == '__main__':
    if __name__ == '__main__':
        main()