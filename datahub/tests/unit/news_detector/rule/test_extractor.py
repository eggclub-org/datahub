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

from collections import defaultdict
import mock
from mock import sentinel
from newspaper.extractors import ContentExtractor
from newspaper.text import StopWords

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
        self.fake_meta_data = ObjectParser(self.ele, 'fake_metadata_ele',
                                           'fake_metadata')

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
        mock_get_attr.assert_has_calls([mock.call(self.ele, 'content'),
                                        mock.call(self.ele, 'content')])

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

    def test_extract_tags_doc_none(self):
        res = self.extractor.extract_tags([])
        self.assertEqual(extractor.NO_STRINGS, res)

    @mock.patch.object(Parser, 'css_select')
    def test_extract_tags_element_none(self, mock_select):
        mock_select.return_value = None
        res = self.extractor.extract_tags([self.doc])
        self.assertEqual(extractor.NO_STRINGS, res)
        mock_select.assert_has_calls([mock.call([self.doc],
                                                extractor.A_REL_TAG_SELECTOR),
                                     mock.call([self.doc],
                                               extractor.A_HREF_TAG_SELECTOR)])

    @mock.patch.object(Parser, 'css_select')
    def test_extract_tags_ok(self, mock_select):
        mock_select.return_value = [self.fake_meta_lang]
        res = self.extractor.extract_tags([self.doc])
        self.assertEqual(set([self.fake_meta_lang.xpath]), res)
        mock_select.assert_called_once_with([self.doc],
                                            extractor.A_REL_TAG_SELECTOR)

    @mock.patch.object(Parser, 'css_select')
    def test_get_meta_data_key_tag(self, mock_select):
        self.fake_meta_lang.ele = mock.MagicMock()
        self.fake_meta_data.ele = mock.MagicMock()
        self.fake_meta_lang.ele.attrib.get.side_effect = ['farboo:bar', None,
                                                          'foo']
        self.fake_meta_data.ele.attrib.get.return_value = 'farboo'
        mock_select.return_value = [self.fake_meta_data, self.fake_meta_lang]
        res = self.extractor.get_meta_data(self.doc)
        expected = defaultdict(dict)
        expected['farboo'] = {'bar': 'fake_metalang_ele/@value',
                              'farboo': 'fake_metadata_ele'}
        self.assertEqual(expected, res)
        self.fake_meta_lang.ele.attrib.get.assert_has_calls([
            mock.call('property'), mock.call('content'), mock.call('value')
        ])
        self.fake_meta_data.ele.attrib.get.assert_has_calls([
            mock.call('property'), mock.call('content')
        ])
        mock_select.assert_called_once_with(self.doc, 'meta')

    @mock.patch.object(Parser, 'css_select')
    def test_get_meta_data_key_none(self, mock_select):
        self.fake_meta_data.ele = mock.MagicMock()
        self.fake_meta_data.ele.attrib.get.return_value = None
        mock_select.return_value = [self.fake_meta_data]
        res = self.extractor.get_meta_data(self.doc)
        expected = defaultdict(dict)
        self.assertEqual(expected, res)
        mock_select.assert_called_once_with(self.doc, 'meta')
        self.fake_meta_data.ele.attrib.get.assert_has_calls([
            mock.call('property'), mock.call('name'),
            mock.call('content'), mock.call('value')
        ])

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_publishing_date_ok(self, mock_get_tag, mock_get_attr):
        mock_get_tag.return_value = [self.fake_meta_data]
        mock_get_attr.return_value = '2017-03-25'
        res = self.extractor.get_publishing_date('fake_url', self.doc)
        self.assertEqual('fake_metadata_ele/@content', res)
        mock_get_tag.assert_called_once_with(self.doc, attr='property',
                                             value='rnews:datePublished')
        mock_get_attr.assert_called_once_with(self.fake_meta_data.ele,
                                              'content')

    @mock.patch.object(Parser, 'getAttribute')
    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_publishing_date_fail(self, mock_get_tag, mock_get_attr):
        mock_get_tag.return_value = [self.fake_meta_data]
        mock_get_attr.return_value = '2017-13'
        res = self.extractor.get_publishing_date('fake_url', self.doc)
        self.assertEqual('', res)
        mock_get_tag.assert_has_calls([
            mock.call(self.doc, attr='property', value='rnews:datePublished'),
            mock.call(self.doc, attr='property',
                      value='article:published_time'),
            mock.call(self.doc, attr='name', value='OriginalPublicationDate'),
            mock.call(self.doc, attr='itemprop', value='datePublished'),
            mock.call(self.doc, attr='itemprop', value='datePublished'),
            mock.call(self.doc, attr='property', value='og:published_time'),
            mock.call(self.doc, attr='name', value='article_date_original'),
            mock.call(self.doc, attr='name', value='publication_date'),
            mock.call(self.doc, attr='name', value='sailthru.date'),
            mock.call(self.doc, attr='name', value='PublishDate')
        ])
        mock_get_attr.assert_has_calls([
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'datetime'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
            mock.call(self.fake_meta_data.ele, 'content'),
        ])

    def test_get_urls_none(self):
        res = self.extractor._get_urls(None, 'fake_title')
        self.assertEqual([], res)

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_urls_titles(self, mock_get):
        self.fake_meta_data.ele = mock.MagicMock()
        self.fake_meta_data.ele.get.return_value = 'http://www.example.com'
        self.fake_meta_data.ele.text = 'fake_text'
        mock_get.return_value = [self.fake_meta_data]
        res = self.extractor._get_urls(self.doc, 'fake_title')
        self.assertEqual([('http://www.example.com', 'fake_text')], res)
        mock_get.assert_called_once_with(self.doc, tag='a')
        self.fake_meta_data.ele.get.assert_has_calls([
            mock.call('href'), mock.call('href'), mock.call('href')
        ])

    @mock.patch.object(Parser, 'getElementsByTag')
    def test_get_urls_no_titles(self, mock_get):
        self.fake_meta_data.ele = mock.MagicMock()
        self.fake_meta_data.ele.get.return_value = 'http://www.example.com'
        self.fake_meta_data.ele.text = 'fake_text'
        mock_get.return_value = [self.fake_meta_data]
        res = self.extractor._get_urls(self.doc, None)
        self.assertEqual([('http://www.example.com')], res)
        mock_get.assert_called_once_with(self.doc, tag='a')
        self.fake_meta_data.ele.get.assert_has_calls([
            mock.call('href'), mock.call('href'), mock.call('href')
        ])

    @mock.patch.object(ContentExtractor, 'get_score')
    @mock.patch.object(ContentExtractor, 'update_node_count')
    @mock.patch.object(ContentExtractor, 'update_score')
    @mock.patch.object(Parser, 'getParent')
    @mock.patch.object(ContentExtractor, 'is_boostable')
    @mock.patch.object(StopWords, 'get_stopword_count')
    @mock.patch.object(ContentExtractor, 'is_highlink_density')
    @mock.patch.object(Parser, 'getText')
    @mock.patch.object(ContentExtractor, 'nodes_to_check')
    def test_calculate_best_node(self, mock_check, mock_get_text,
                                 mock_highlink, mock_get_sw, mock_boost,
                                 mock_get_parent, mock_update_score,
                                 mock_update_count, mock_get_score):
        mock_ws = mock.MagicMock()
        mock_check.return_value = [self.fake_meta_data]
        mock_get_text.return_value = 'fake_text'
        mock_highlink.return_value = False
        mock_boost.return_value = True
        mock_get_parent.side_effect = [self.fake_author, self.fake_meta_lang]
        mock_get_score.return_value = 1

        mock_get_sw.return_value = mock_ws
        mock_ws.get_stopword_count.return_value = 3

        res = self.extractor.calculate_best_node(self.doc)

        self.assertEqual(self.fake_author, res)
        mock_check.assert_called_once_with(self.doc)
        mock_get_text.assert_has_calls([mock.call(self.ele),
                                        mock.call(self.ele)])
        mock_highlink.assert_called_once_with(self.ele)
        mock_get_sw.assert_has_calls([mock.call('fake_text'),
                                      mock.call('fake_text')], any_order=True)
        mock_boost.assert_called_once_with(self.ele)
        mock_get_parent.assert_has_calls([mock.call(self.fake_meta_data),
                                          mock.call(self.fake_author)])
        mock_update_score.assert_has_calls([
            mock.call(self.fake_author, 53),
            mock.call(self.fake_meta_lang, 26.5)])
        mock_update_count.assert_has_calls([mock.call(self.fake_author, 1),
                                            mock.call(self.fake_meta_lang, 1)])
        mock_get_score.assert_has_calls([mock.call(self.fake_author),
                                         mock.call(self.fake_meta_lang)])

    @mock.patch.object(ContentExtractor, 'get_score')
    @mock.patch.object(ContentExtractor, 'update_node_count')
    @mock.patch.object(ContentExtractor, 'update_score')
    @mock.patch.object(Parser, 'getParent')
    @mock.patch.object(ContentExtractor, 'is_boostable')
    @mock.patch.object(StopWords, 'get_stopword_count')
    @mock.patch.object(ContentExtractor, 'is_highlink_density')
    @mock.patch.object(Parser, 'getText')
    @mock.patch.object(ContentExtractor, 'nodes_to_check')
    def test_calculate_best_node_15(self, mock_check, mock_get_text,
                                    mock_highlink, mock_get_sw, mock_boost,
                                    mock_get_parent, mock_update_score,
                                    mock_update_count, mock_get_score):
        mock_ws = mock.MagicMock()
        mock_check.return_value = [self.fake_meta_data] * 16
        mock_get_text.return_value = 'fake_text'
        mock_highlink.return_value = False
        mock_boost.return_value = True
        mock_get_parent.return_value = self.fake_author
        mock_get_score.return_value = 1

        mock_get_sw.return_value = mock_ws
        mock_ws.get_stopword_count.return_value = 3

        res = self.extractor.calculate_best_node(self.doc)

        self.assertEqual(self.fake_author, res)
        mock_check.assert_called_once_with(self.doc)
        mock_get_text.assert_has_calls([mock.call(self.ele),
                                        mock.call(self.ele)])
        mock_highlink.assert_has_calls([mock.call(self.ele)] * 16)
        mock_get_sw.assert_has_calls([mock.call('fake_text'),
                                      mock.call('fake_text')], any_order=True)
        mock_boost.assert_has_calls([mock.call(self.ele)] * 16)
        mock_get_parent.assert_has_calls([mock.call(self.fake_meta_data),
                                          mock.call(self.fake_author)])
        mock_update_score.assert_has_calls([mock.call(self.fake_author, 53),
                                            mock.call(self.fake_author, 26.5)])
        mock_update_count.assert_has_calls([mock.call(self.fake_author, 1),
                                            mock.call(self.fake_author, 1)])
        mock_get_score.assert_called_once_with(self.fake_author)

    @mock.patch.object(ContentExtractor, 'nodes_to_check')
    def test_calculate_best_node_none(self, mock_check):
        mock_check.return_value = []

        res = self.extractor.calculate_best_node(self.doc)

        self.assertEqual(None, res)
        mock_check.assert_called_once_with(self.doc)


class VideoExtractorTestCase(base.TestCase):

    def setUp(self):
        super(VideoExtractorTestCase, self).setUp()
        self.doc = sentinel.fake_doc
        self.extractor = extractor.VideoExtractor(config.SourceConfig(),
                                                  self.doc)

    @mock.patch.object(Parser, 'getAttribute')
    def test_get_src(self, mock_get):
        mock_get.side_effect = [None, 'fake_attr']
        res = self.extractor.get_src(self.doc)
        self.assertEqual('fake_attr', res)
        mock_get.assert_has_calls([mock.call(self.doc, 'src'),
                                   mock.call(self.doc, 'data-src')])
