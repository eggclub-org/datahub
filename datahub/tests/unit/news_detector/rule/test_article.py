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
from newspaper.article import Article as BaseArticle
from newspaper.cleaners import DocumentCleaner

from datahub.news_detector.rule import article
from datahub.news_detector.rule import config
from datahub.news_detector.rule.extractor import Extractor
from datahub.news_detector.rule.extractor import VideoExtractor
from datahub.news_detector.rule.parser import Parser

from datahub.tests import base


class ArticleTest(base.BaseTestCase):

    def setUp(self):
        super(ArticleTest, self).setUp()
        self.url = "http://fake-url.boo"
        self.config = config.SourceConfig()
        self.extractor = Extractor(self.config)
        self.article = article.Article(self.url, config=self.config,
                                       extractor=self.extractor)
        self.doc = sentinel.html
        self.clean_doc = sentinel.clean_html

    @mock.patch.object(BaseArticle, 'download')
    def test_process_no_download(self, mock_download):
        self.assertRaises(article.ArticleException, self.article.process)
        mock_download.assert_called_once_with()

    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(BaseArticle, 'download')
    def test_process_no_parse(self, mock_download, mock_from):
        self.article.is_downloaded = True
        mock_from.return_value = None
        res = self.article.process()
        self.assertIsNone(res)
        mock_download.assert_called_once_with()

    @mock.patch.object(BaseArticle, 'set_movies')
    @mock.patch.object(BaseArticle, 'release_resources')
    @mock.patch.object(VideoExtractor, 'get_videos')
    @mock.patch.object(Extractor, 'calculate_best_node')
    @mock.patch.object(DocumentCleaner, 'clean')
    @mock.patch.object(Extractor, 'get_publishing_date')
    @mock.patch.object(Extractor, 'get_meta_data')
    @mock.patch.object(Extractor, 'get_meta_keywords')
    @mock.patch.object(Extractor, 'extract_tags')
    @mock.patch.object(Extractor, 'get_canonical_link')
    @mock.patch.object(Extractor, 'get_meta_description')
    @mock.patch.object(Extractor, 'get_favicon')
    @mock.patch.object(Extractor, 'get_meta_lang')
    @mock.patch.object(Extractor, 'get_authors')
    @mock.patch.object(Extractor, 'get_title')
    @mock.patch.object(BaseArticle, 'get_parse_candidate')
    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(BaseArticle, 'download')
    def test_process_ok(self, mock_download, mock_from, mock_get_parse,
                        mock_get_title, mock_get_auth, mock_get_lang,
                        mock_get_ico, mock_get_desc, mock_get_link,
                        mock_extract, mock_get_kw, mock_get_data,
                        mock_get_date, mock_clean, mock_calc, mock_video,
                        mock_release, mock_set_video):
        self.article.is_downloaded = True
        mock_get_title.return_value = 'fake_title'
        mock_get_auth.return_value = ['fake_auth']
        mock_get_lang.return_value = 'fake_lang'
        mock_get_ico.return_value = 'fake_ico'
        mock_get_desc.return_value = 'fake_desc'
        mock_get_link.return_value = 'fake_link'
        mock_extract.return_value = 'fake_tag'
        mock_get_kw.return_value = 'fake_keywords'
        mock_get_data.return_value = 'fake_meta_data'
        mock_get_date.return_value = 'fake_date'
        mock_get_parse.return_value.link_hash = 'fake_hash'
        mock_calc.return_value.xpath = 'fake_content'
        mock_video.return_value = 'fake_video'
        mock_clean.return_value = self.doc
        mock_from.return_value = self.clean_doc

        self.article.process()

        # TODO(hieulq): add more check for all mocks
        mock_download.assert_called_once_with()
        mock_release.assert_called_once_with()
        mock_set_video.assert_called_once_with('fake_video')
