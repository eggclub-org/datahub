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
from newspaper.network import MRequest
from newspaper.source import Source as BaseSource

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


# NOTE(hieulq): we mock multithread request for speeding up the tests
@mock.patch('newspaper.network.multithread_request')
class SourceTest(base.BaseTestCase):

    def setUp(self):
        super(SourceTest, self).setUp()
        self.url = 'http://foo.bar'
        self.config = config.SourceConfig()
        self.extractor = Extractor(self.config)
        self.source = article.Source(self.url, config=self.config,
                                     extractor=self.extractor)
        self.fake_request = MRequest(self.url, self.config)

    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(BaseSource, 'download')
    def test_process_no_download(self, mock_download, mock_from, mock_mreq):
        mock_from.return_value = None
        mock_mreq.return_value = [self.fake_request]
        res = self.source.process()
        self.assertEqual({}, res)
        mock_download.assert_called_once_with()
        mock_from.assert_called_once_with('')
        mock_mreq.assert_has_calls([mock.call([self.url], self.config),
                                    mock.call([], self.config)])

    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(BaseSource, 'download')
    def test_process_no_parse(self, mock_download, mock_from, mock_mreq):
        self.source.is_downloaded = True
        mock_mreq.return_value = [self.fake_request]
        mock_from.return_value = None
        res = self.source.process()
        self.assertEqual({}, res)
        mock_download.assert_called_once_with()
        mock_from.assert_called_once_with('')
        mock_mreq.assert_has_calls([mock.call([self.url], self.config),
                                    mock.call([], self.config)])

    @mock.patch.object(article.Article, 'process')
    @mock.patch.object(article.Article, 'is_valid_url')
    @mock.patch.object(Extractor, 'get_urls')
    @mock.patch.object(Extractor, 'get_feed_urls')
    @mock.patch.object(BaseSource, '_get_category_urls')
    @mock.patch.object(Parser, 'fromstring')
    @mock.patch('newspaper.network.get_html')
    def test_process_article_ok(self, mock_get_html, mock_from, mock_get_cat,
                                mock_get_feed, mock_get_url, mock_valid,
                                mock_process, mock_mreq):
        self.source.is_downloaded = True
        fake_req1 = MRequest('http://a.foo.bar', self.config)
        fake_req1.resp = 'ok1'
        fake_req2 = MRequest('http://b.foo.bar', self.config)
        fake_req2.resp = 'ok2'
        mock_mreq.return_value = [fake_req1, fake_req2]
        mock_from.side_effect = [None, sentinel.fake_html1,
                                 sentinel.fake_html2]
        mock_valid.return_value = True
        mock_process.side_effect = [None, article.ArticleException]
        mock_get_url.side_effect = [[('fake_url1', 'fake_title1')],
                                    [('fake_url2', 'fake_title2')],
                                    ['fake_feed1'], ['fake_feed2']]
        mock_get_cat.return_value = ['http://foo.bar/fake_url1',
                                     'http://foo.bar/fake_url2']
        mock_get_feed.return_value = ['http://foo.bar/fake_feed1',
                                      'http://foo.bar/fake_feed2']

        res = self.source.process()

        # TODO(hieulq): add more check for all mocks
        self.assertEqual(2, len(res))
        mock_get_html.assert_has_calls([mock.call(self.url, self.config),
                                        mock.call('http://a.foo.bar',
                                                  response='ok1'),
                                        mock.call('http://b.foo.bar',
                                                  response='ok2')],
                                       any_order=True)
        mock_mreq.assert_has_calls([mock.call(['http://foo.bar/fake_url1',
                                               'http://foo.bar/fake_url2'],
                                              self.config),
                                    mock.call(['http://foo.bar/fake_feed1',
                                               'http://foo.bar/fake_feed2'],
                                              self.config)])
        mock_process.assert_has_calls([mock.call(), mock.call()])
