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
import fixtures
import lxml.etree
from oslo_log import log as logging

from datahub.news_detector.rule import article
from datahub.news_detector.rule import config
from datahub.news_detector.rule.extractor import Extractor
from datahub.tests import base

# This path is for Pycharm dev env
# DOMAIN_PATH = "../../../data/targets"
# This path is for tox env
DOMAIN_PATH = "./data/targets"
LOG = logging.getLogger(__name__)


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
            try:
                source = article.Source(target, config=self.config,
                                        extractor=self.extractor)
                source.download()
                source.parse()

                source.set_categories()
                source.download_categories()  # mthread
                source.parse_categories()

                source.generate_articles()
                outs = source._generate_format_for_categories(
                    sampling=3, process_all=False)
                template = None
                for domain, articles in outs.items():
                    for index, art in enumerate(articles):
                        if index == 0:
                            template = art
                            continue
                        try:
                            art.download()
                            art.from_format(template)
                        except (article.ArticleException,
                                lxml.etree.XPathEvalError):
                            LOG.error("Error getting content of article\n"
                                      "%s \n"
                                      "from template of article \n"
                                      "%s \n" % (str(art), str(template)))
                            continue
                if outs:
                    for out in outs:
                        LOG.info('==============')
                        LOG.info(str(out))
            except fixtures.TimeoutException:
                LOG.error("Cannot process source with url %s" %
                          source.url)
                continue

    def test_single_source(self):
        url = "http://www.baotainguyenmoitruong.vn/kinh-te/" \
              "201703/gpp-ca-mau-san-sang-don-dong-khi-dau-tien-2789387/"
        src = article.Article(url, config=self.config,
                              extractor=self.extractor)
        src.process()
        # self.assertNotEqual(1, len(res))
        # for a in src.articles:
        #     LOG.info(a.url)
