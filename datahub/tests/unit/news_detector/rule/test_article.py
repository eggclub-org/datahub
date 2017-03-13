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

import fixtures
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
from datahub.news_detector.rule.parser import ObjectParser
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

    def test_from_format_exc(self):
        self.assertRaises(article.ArticleException,
                          self.article.from_format, None)

    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(Parser, 'xpath_re')
    def test_from_format_none(self, mock_xpath, mock_from):
        target = article.Article('http://foo.bar', config=self.config,
                                 extractor=self.extractor)
        target.is_downloaded = True
        mock_from.return_value = self.doc

        target.from_format(self.article)

        mock_xpath.assert_not_called()

    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(Parser, 'xpath_re')
    def test_from_format_ok(self, mock_xpath, mock_from):
        mock_xpath.side_effect = [
            [ObjectParser(self.doc, 'xpath1', 'fake_title1')],
            [ObjectParser(self.doc, 'xpath1', 'fake_text1')],
            [ObjectParser(self.doc, 'xpath1', 'fake_author1')],
            [ObjectParser(self.doc, 'xpath1', 'fake_date1')]]
        self.article.title = 'fake_title'
        self.article.text = 'fake_text'
        self.article.publish_date = 'fake_date'
        self.article.authors = ['fake_author']
        target = article.Article('http://foo.bar', config=self.config,
                                 extractor=self.extractor)
        target.is_downloaded = True
        mock_from.return_value = self.doc

        target.from_format(self.article)

        self.assertEqual('fake_title1', target.title)
        self.assertEqual('fake_text1\n', target.text)
        self.assertEqual('fake_date1', target.publish_date)
        self.assertEqual('fake_author1', target.authors)
        mock_xpath.assert_has_calls([mock.call(target.doc, 'fake_title'),
                                     mock.call(target.doc, 'fake_text'),
                                     mock.call(target.doc, ['fake_author']),
                                     mock.call(target.doc, 'fake_date')])

    @mock.patch.object(Parser, 'fromstring')
    def test_from_format_exc_doc(self, mock_from):
        target = article.Article('http://foo.bar', config=self.config,
                                 extractor=self.extractor)
        target.is_downloaded = True
        mock_from.return_value = None
        self.assertRaises(article.ArticleException,
                          target.from_format, self.article)

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
        print(str(self.article))
        mock_download.assert_called_once_with()
        mock_release.assert_called_once_with()
        mock_set_video.assert_called_once_with('fake_video')


class SourceTest(base.BaseTestCase):

    def setUp(self):
        super(SourceTest, self).setUp()
        self.url = 'http://foo.bar'
        self.config = config.SourceConfig()
        self.config.use_meta_language = True
        self.extractor = Extractor(self.config)
        self.source = article.Source(self.url, config=self.config,
                                     extractor=self.extractor)
        self.fake_request = MRequest(self.url, self.config)

    @mock.patch('newspaper.network.multithread_request')
    @mock.patch.object(Parser, 'fromstring')
    @mock.patch.object(BaseSource, 'download')
    def test_process_no_download(self, mock_download, mock_from, mock_mreq):
        mock_from.return_value = None
        mock_mreq.return_value = [self.fake_request]
        res = self.source.process()
        self.assertEqual({}, res)
        mock_download.assert_called_once_with()
        mock_from.assert_called_once_with('')
        mock_mreq.assert_called_once_with([self.url], self.config)

    @mock.patch('newspaper.network.multithread_request')
    @mock.patch.object(BaseSource, 'download')
    def test_process_timeout(self, mock_download, mock_mreq):
        mock_download.side_effect = [fixtures.TimeoutException]
        res = self.source.process()
        self.assertEqual({}, res)
        mock_download.assert_called_once_with()

    @mock.patch('newspaper.network.multithread_request')
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
        mock_mreq.assert_called_once_with([self.url], self.config)

    @mock.patch('newspaper.network.multithread_request')
    @mock.patch.object(article.Article, 'process')
    @mock.patch.object(article.Article, 'is_valid_url')
    @mock.patch.object(Extractor, 'get_urls')
    @mock.patch.object(BaseSource, '_get_category_urls')
    @mock.patch.object(Parser, 'fromstring')
    @mock.patch('newspaper.network.get_html')
    def _process_test(self, mock_get_html, mock_from, mock_get_cat,
                      mock_get_url, mock_valid, mock_process, mock_mreq,
                      is_process, process_all):
        self.source.is_downloaded = True
        fake_req1 = MRequest('http://a.foo.bar', self.config)
        fake_req1.resp = 'ok1'
        fake_req2 = MRequest('http://b.foo.bar', self.config)
        fake_req2.resp = 'ok2'
        mock_mreq.return_value = [fake_req1, fake_req2]
        mock_from.side_effect = [None, sentinel.fake_html1,
                                 sentinel.fake_html2]
        mock_valid.return_value = True
        mock_process.side_effect = [None, article.ArticleException, None, None]
        mock_get_url.side_effect = [[('fake_url1', 'fake_title1')],
                                    [('fake_url2', 'fake_title2')]]
        mock_get_cat.return_value = ['http://foo.bar/fake_url1',
                                     'http://foo.bar/fake_url2']

        if is_process:
            res = self.source.process()
        else:
            # prepare
            self.source.download()
            self.source.parse()

            self.source.set_categories()
            self.source.download_categories()
            self.source.parse_categories()

            self.source.generate_articles()
            if process_all:
                res = self.source._generate_format_for_categories(
                    sampling=1, process_article=True, process_all=process_all)
            else:
                res = self.source._generate_format_for_categories(
                    sampling=1, process_article=False, process_all=process_all)

        self.assertEqual(2, len(res))
        mock_get_html.assert_has_calls([mock.call(self.url, self.config),
                                        mock.call('http://a.foo.bar',
                                                  response='ok1'),
                                        mock.call('http://b.foo.bar',
                                                  response='ok2')],
                                       any_order=True)
        mock_mreq.assert_called_once_with(['http://foo.bar/fake_url1',
                                           'http://foo.bar/fake_url2'],
                                          self.config)
        if is_process:
            mock_process.assert_has_calls([mock.call(), mock.call()])
        elif process_all:
            mock_process.assert_has_calls([mock.call(), mock.call(),
                                           mock.call(), mock.call()])
        else:
            mock_process.assert_not_called()

    def test_generate_format_unprocess(self):
        self._process_test(is_process=False, process_all=False)

    def test_generate_format_unprocess_all(self):
        self._process_test(is_process=False, process_all=True)

    def test_process_source_ok(self):
        self._process_test(is_process=True, process_all=False)
