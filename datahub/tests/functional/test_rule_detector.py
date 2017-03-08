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

from datahub.news_detector.rule.article import Source
from datahub.news_detector.rule import config
from datahub.news_detector.rule.extractor import Extractor
from datahub.tests import base

# This path is for Pycharm dev env
DOMAIN_PATH = "../../../data/targets"
# This path is for tox env
# DOMAIN_PATH = "./data/targets"


class TestRuleDetector(base.BaseTestCase):

    def setUp(self):
        super(TestRuleDetector, self).setUp()
        with open(DOMAIN_PATH) as f:
            targets = f.readlines()
        self.targets = [target.strip() for target in targets]
        self.config = config.SourceConfig()
        self.extractor = Extractor(self.config)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        logging.getLogger("tldextract").setLevel(logging.WARNING)

    def test_source_from_domain_list(self):
        for target in self.targets:
            source = Source(target, config=self.config,
                            extractor=self.extractor)
            outs = source.process()
            for out in outs:
                print(str(out))
