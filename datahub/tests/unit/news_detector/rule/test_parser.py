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

from lxml import etree
from lxml import html
import mock

from datahub.news_detector.rule import parser
from datahub.news_detector.rule.parser import Parser
from datahub.tests import base


class ObjectParserTest(base.BaseTestCase):

    def setUp(self):
        super(ObjectParserTest, self).setUp()
        self.root = etree.Element("html")
        etree.SubElement(self.root, "child").text = 'test'
        self.comment = html.HtmlComment('comment')

    def test_init(self):
        obj_none_text = parser.ObjectParser(self.root, 'xpath1', None)
        self.assertEqual('test', obj_none_text.text)
        obj_comment = parser.ObjectParser(self.comment, 'xpath2', 'foobar')
        self.assertEqual('comment', obj_comment.text)
        obj_text = parser.ObjectParser(self.root, 'xpath3', 'foobar')
        self.assertEqual('foobar', obj_text.text)

    def test_clear(self):
        obj_text = parser.ObjectParser(self.root, 'xpath3', 'foobar')
        obj_text.clear()
        self.assertIsNone(obj_text.text)
        self.assertIsNone(obj_text.xpath)
        self.assertEqual({}, obj_text.ele.attrib)

    def test_insert(self):
        obj_text = parser.ObjectParser(self.root, 'xpath3', 'foobar')
        obj_text.insert(1, self.comment)


class ParserTest(base.BaseTestCase):

    def setUp(self):
        super(ParserTest, self).setUp()
        self.doc = etree.Element("html")

    def test_xpath_re_str(self):
        node = mock.MagicMock()
        node.xpath.return_value = ['fake_str']
        res = Parser.xpath_re(node, 'fake_exp')
        self.assertEqual(1, len(res))
        self.assertIsNone(res[0].ele)
        self.assertEqual('fake_str', res[0].text)
        self.assertEqual('fake_exp', res[0].xpath)
        node.xpath.assert_called_once_with(
            'fake_exp',
            namespaces={'re': "http://exslt.org/regular-expressions"})

    def test_xpath_re_node(self):
        node = mock.MagicMock()
        node.xpath.return_value = [self.doc]
        res = Parser.xpath_re(node, 'fake_exp')
        self.assertEqual(1, len(res))
        self.assertEqual(self.doc, res[0].ele)
        self.assertEqual('fake_exp', res[0].xpath)
        node.xpath.assert_called_once_with(
            'fake_exp',
            namespaces={'re': "http://exslt.org/regular-expressions"})

    def test_drop_tag_list(self):
        node1, node2 = mock.MagicMock(), mock.MagicMock()
        Parser.drop_tag([node1, node2])
        node1.ele.drop_tag.assert_called_once_with()
        node2.ele.drop_tag.assert_called_once_with()

    def test_drop_tag_ele(self):
        node = mock.MagicMock()
        Parser.drop_tag(node)
        node.ele.drop_tag.assert_called_once_with()

    def test_get_text_with_decorator(self):
        node = parser.ObjectParser(self.doc, 'fake_xpath', 'fake_txt')
        res = Parser.getText(node)
        self.assertEqual('', res)
