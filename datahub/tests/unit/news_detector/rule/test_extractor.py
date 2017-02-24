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

from datahub.news_detector.rule import config
from datahub.news_detector.rule import extractor
from datahub.news_detector.rule.parser import ObjectParser
from datahub.news_detector.rule.parser import Parser

from datahub.tests import base

ATTRS = ['name', 'rel', 'itemprop', 'class', 'id']
VALS = ['author', 'byline', 'dc.creator']


class RuleExtractorTestCase(base.TestCase):

    def setUp(self):
        super(RuleExtractorTestCase, self).setUp()
        self.doc = sentinel.fake_doc
        self.ele = sentinel.fake_ele
        self.extractor = extractor.Extractor(config.SourceConfig())
        self.fake_title = ObjectParser(self.ele, 'fake_title_ele',
                                       'fake_title')
        self.fake_h1 = ObjectParser(self.ele, 'fake_h1_ele', 'fake_h1')
        self.fake_fb = ObjectParser(self.ele, 'fake_fb_ele', 'fake_fb')
        self.fake_author = ObjectParser(self.ele, 'fake_author_ele',
                                        'fake_author')
        self.fake_meta_lang = ObjectParser(self.ele, 'fake_metalang_ele',
                                           'fake_metalang')

    @mock.patch.object(Parser, 'getElementsByTag',
                       return_value=None)
    def test_get_title_no_title_element(self, mock_get):
        res = self.extractor.get_title(self.doc)

        self.assertEqual('', res)
        mock_get.assert_called_once_with(self.doc, tag='title')

    @mock.patch.object(Parser, 'xpath_re')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_title_by_title_element(self, mock_get, mock_xpath):
        self.fake_h1.text = 'fake_title'
        mock_get.side_effect = [[self.fake_title], [self.fake_h1]]
        mock_xpath.return_value = [self.fake_fb]

        res = self.extractor.get_title(self.doc)

        self.assertEqual('fake_title_ele', res)
        mock_get.assert_has_calls([mock.call(self.doc, tag='title'),
                                   mock.call(self.doc, tag='h1')])
        mock_xpath.assert_called_once_with(self.doc, '//meta['
                                                     '@property="og:title"]'
                                                     '/@content')

    @mock.patch.object(Parser, 'xpath_re')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_title_by_h1(self, mock_get, mock_xpath):
        self.fake_fb.text = 'fake_h1'

        mock_get.side_effect = [[self.fake_title], [self.fake_h1]]
        mock_xpath.return_value = [self.fake_fb]

        res = self.extractor.get_title(self.doc)

        self.assertEqual('fake_h1_ele', res)
        mock_get.assert_has_calls([mock.call(self.doc, tag='title'),
                                   mock.call(self.doc, tag='h1')])
        mock_xpath.assert_called_once_with(self.doc, '//meta['
                                                     '@property="og:title"]'
                                                     '/@content')

    @mock.patch.object(Parser, 'xpath_re')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_title_by_h1_in_title(self, mock_get, mock_xpath):
        self.fake_title.text = 'fake_title_big'
        self.fake_h1.text = 'fake_title_b'
        self.fake_fb.text = 'fake_title'

        mock_get.side_effect = [[self.fake_title], [self.fake_h1]]
        mock_xpath.return_value = [self.fake_fb]

        res = self.extractor.get_title(self.doc)

        self.assertEqual('fake_h1_ele', res)
        mock_get.assert_has_calls([mock.call(self.doc, tag='title'),
                                   mock.call(self.doc, tag='h1')])
        mock_xpath.assert_called_once_with(self.doc, '//meta['
                                                     '@property="og:title"]'
                                                     '/@content')

    @mock.patch.object(Parser, 'xpath_re')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_title_by_fb_in_title(self, mock_get, mock_xpath):
        fake_title = ObjectParser(self.ele, 'fake_title_ele', 'fake_title_big')
        fake_h1 = ObjectParser(self.ele, 'fake_h1_ele', 'fake_h1')
        fake_fb = ObjectParser(self.ele, 'fake_fb_ele', 'fake_title')

        mock_get.side_effect = [[fake_title], [fake_h1]]
        mock_xpath.return_value = [fake_fb]

        res = self.extractor.get_title(self.doc)

        self.assertEqual('fake_fb_ele', res)
        mock_get.assert_has_calls([mock.call(self.doc, tag='title'),
                                   mock.call(self.doc, tag='h1')])
        mock_xpath.assert_called_once_with(self.doc, '//meta['
                                                     '@property="og:title"]'
                                                     '/@content')

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_author_invalid_meta(self, mock_get):
        self.fake_author.ele = mock.MagicMock()
        self.fake_author.ele.tag = 'meta'
        self.fake_author.ele.xpath.return_value = ['fake_text']
        mock_get.side_effect = [[self.fake_author], [], [], [], [], [], [], [],
                                [], [], [], [], [], [], []]

        res = self.extractor.get_authors(self.doc)

        self.assertEqual([], res)
        mock_calls = []
        for attr in ATTRS:
            for val in VALS:
                mock_calls.append(mock.call(self.doc, attr=attr, value=val))
        mock_get.assert_has_calls(mock_calls)
        self.fake_author.ele.xpath.assert_called_once_with(
            'fake_author_ele/@content')

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_author_valid(self, mock_get):
        self.fake_author.ele.tag = 'super_meta'
        self.fake_author.text = 'By: Foo Bar, Far Boo'
        mock_get.side_effect = [[self.fake_author], [], [], [], [], [], [],
                                [], [], [], [], [], [], [], []]

        res = self.extractor.get_authors(self.doc)

        mock_calls = []
        for attr in ATTRS:
            for val in VALS:
                mock_calls.append(mock.call(self.doc, attr=attr, value=val))
        mock_get.assert_has_calls(mock_calls)
        self.assertEqual(['fake_author_ele'], res)

    @mock.patch.object(Parser, 'getAttribute')
    def test_get_meta_lang_attr(self, mock_get):
        mock_get.return_value = 'Fake_Lang'
        res = self.extractor.get_meta_lang(self.doc)
        self.assertEqual(('fake_lang', '/html/@lang'), res)
        mock_get.assert_called_once_with(self.doc, attr='lang')

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_meta_lang_attr_none(self, mock_get_ele, mock_get_attr):
        self.fake_meta_lang.ele = mock.MagicMock()
        self.fake_meta_lang.ele.tag = 'meta'
        self.fake_meta_lang.ele.xpath.return_value = ['Fake_Lang']
        mock_get_attr.return_value = None
        mock_get_ele.return_value = [self.fake_meta_lang]

        res = self.extractor.get_meta_lang(self.doc)

        self.assertEqual(('fake_lang', 'fake_metalang_ele/@content'), res)
        mock_get_attr.assert_called_once_with(self.doc, attr='lang')
        mock_get_ele.assert_called_once_with(self.doc, tag='meta',
                                             attr='http-equiv',
                                             value='content-language')
        self.fake_meta_lang.ele.xpath.assert_called_once_with(
            'fake_metalang_ele/@content')

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_none_meta_lang_attr(self, mock_get_ele, mock_get_attr):
        mock_get_attr.return_value = None
        mock_get_ele.return_value = None

        res = self.extractor.get_meta_lang(self.doc)

        self.assertEqual(('', ''), res)
        mock_get_attr.assert_called_once_with(self.doc, attr='lang')
        mock_get_ele.assert_has_calls([
            mock.call(self.doc, tag='meta', attr='http-equiv',
                      value='content-language'),
            mock.call(self.doc, tag='meta', attr='name', value='lang')])

    @mock.patch.object(Parser, 'css_select')
    def test_get_meta_content_none(self, mock_css):
        mock_css.return_value = None
        res = self.extractor.get_meta_content(self.doc, 'fake_meta')
        self.assertEqual('', res)
        mock_css.assert_called_once_with(self.doc, 'fake_meta')

    @mock.patch.object(Parser, 'css_select')
    def test_get_meta_content(self, mock_css):
        mock_css.return_value = [self.fake_meta_lang]
        res = self.extractor.get_meta_content(self.doc, 'fake_meta')
        self.assertEqual('fake_metalang_ele/@content', res)
        mock_css.assert_called_once_with(self.doc, 'fake_meta')

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'css_select')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_canonical_link_ca(self, mock_get_ele, mock_get_css,
                                   mock_get_attr):
        mock_get_ele.return_value = [self.fake_meta_lang]
        mock_get_css.return_value = []
        mock_get_attr.return_value = 'fake_url'
        res = self.extractor.get_canonical_link(self.doc)
        self.assertEqual('fake_metalang_ele/@href', res)
        mock_get_ele.assert_called_once_with(self.doc, tag='link', attr='rel',
                                             value='canonical')
        mock_get_css.assert_called_once_with(self.doc,
                                             'meta[property="og:url"]')
        mock_get_attr.assert_called_once_with(self.ele, 'href')

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'css_select')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_canonical_link_og(self, mock_get_ele, mock_get_css,
                                   mock_get_attr):
        mock_get_ele.return_value = []
        mock_get_css.return_value = [self.fake_meta_lang]
        mock_get_attr.return_value = 'fake_url'
        res = self.extractor.get_canonical_link(self.doc)
        self.assertEqual('fake_metalang_ele/@content', res)
        mock_get_ele.assert_called_once_with(self.doc, tag='link', attr='rel',
                                             value='canonical')
        mock_get_css.assert_called_once_with(self.doc,
                                             'meta[property="og:url"]')
        mock_get_attr.assert_called_once_with(self.ele, 'content')

    @mock.patch.object(Parser, 'css_select')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_canonical_link_none(self, mock_get_ele, mock_get_css):
        mock_get_ele.return_value = []
        mock_get_css.return_value = []
        res = self.extractor.get_canonical_link(self.doc)
        self.assertEqual('', res)
        mock_get_ele.assert_called_once_with(self.doc, tag='link', attr='rel',
                                             value='canonical')
        mock_get_css.assert_called_once_with(self.doc,
                                             'meta[property="og:url"]')

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_fav_icon_ok(self, mock_get_ele):
        mock_get_ele.return_value = [self.fake_meta_lang]
        res = self.extractor.get_favicon(self.doc)
        self.assertEqual('fake_metalang_ele/@href', res)
        mock_get_ele.assert_called_once_with(self.doc, tag='link', attr='rel',
                                             value='icon')

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_fav_icon_none(self, mock_get_ele):
        mock_get_ele.return_value = []
        res = self.extractor.get_favicon(self.doc)
        self.assertEqual('', res)
        mock_get_ele.assert_called_once_with(self.doc, tag='link', attr='rel',
                                             value='icon')
