# -*- coding: utf-8 -*-

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
import logging

from datahub.news_detector.rule import article
from datahub.news_detector.rule import config
from datahub.news_detector.rule.extractor import Extractor
from datahub.tests import base

# This path is for Pycharm dev env
# DOMAIN_PATH = "../../../data/targets"
# This path is for tox env
DOMAIN_PATH = "./data/targets"


class TestRuleDetector(base.BaseTestCase):

    def setUp(self):
        super(TestRuleDetector, self).setUp()
        self.config = config.SourceConfig()
        self.extractor = Extractor(self.config)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("tldextract").setLevel(logging.WARNING)

    def test_source_from_domain_list(self):
        with open(DOMAIN_PATH) as f:
            tars = f.readlines()
        targets = [target.strip() for target in tars]
        for target in targets:
            source = article.Source(target, config=self.config,
                                    extractor=self.extractor)
            outs = source.process()
            if outs:
                for out in outs:
                    print(str(out))

    def test_single_source(self):
        url = "http://vnexpress.net"
        src = article.Source(url, config=self.config, extractor=self.extractor)
        res = src.process()
        for a in src.articles:
            print(a.url)
        print('fin')
