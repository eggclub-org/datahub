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
        self.ele_text = etree.fromstring("<child name='fake'>test</child>")
        self.doc = etree.fromstring("<html name='froot'><sib>sib</sib><child "
                                    "name='fake'>test</child>foo</html>")

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
        self.assertEqual('sib test foo', res)

    def test_css_select(self):
        res = Parser.css_select(self.doc, 'html')
        self.assertEqual(1, len(res))
        self.assertEqual('sib test foo', res[0].text)
        self.assertEqual('/html', res[0].xpath)

    def test_node_to_string(self):
        res = Parser.nodeToString(self.doc)
        self.assertEqual('<html name="froot"><sib>sib</sib><child '
                         'name="fake">test</child>foo</html>', res)

    def test_get_ele_by_tag_with_attr(self):
        res = Parser.getElementsByTag(self.doc, tag='child', attr='name',
                                      value='fake')
        self.assertEqual(1, len(res))
        self.assertEqual('test', res[0].text)
        self.assertEqual('/html/child', res[0].xpath)

    def test_get_ele_by_tag_no_attr(self):
        root = etree.Element('root')
        root.append(self.doc)
        res = Parser.getElementsByTag(root, tag='root')
        self.assertEqual([], res)

    def test_child_node_with_text_enable(self):
        res = Parser.childNodesWithText(self.ele_text)
        self.assertEqual(1, len(res))
        self.assertEqual('test', res[0].text)
        self.assertEqual('text', res[0].tag)

    def test_child_node_with_text_disable(self):
        res = Parser.childNodesWithText(self.doc)
        self.assertEqual(3, len(res))
        self.assertEqual(None, res[0].tail)
        self.assertEqual('sib', res[0].text)
        self.assertEqual('sib', res[0].tag)
        self.assertEqual('foo', res[1].tail)
        self.assertEqual('test', res[1].text)
        self.assertEqual('child', res[1].tag)
        self.assertEqual(None, res[2].tail)
        self.assertEqual('foo', res[2].text)
        self.assertEqual('text', res[2].tag)

    def test_get_children(self):
        res = Parser.getChildren(self.doc)
        self.assertEqual(2, len(res))
        self.assertEqual(None, res[0].tail)
        self.assertEqual('sib', res[0].text)
        self.assertEqual('sib', res[0].tag)
        self.assertEqual('foo', res[1].tail)
        self.assertEqual('test', res[1].text)
        self.assertEqual('child', res[1].tag)

    def test_remove(self):
        node = self.doc.find('child')
        Parser.remove(node)
        nodes_after_remove = Parser.getElementsByTag(self.doc, tag='child')
        self.assertEqual(0, len(nodes_after_remove))

    def test_get_attr(self):
        res = Parser.getAttribute(self.doc, attr='name')
        self.assertEqual('froot', res)

    def test_del_attr(self):
        Parser.delAttribute(self.doc, attr='name')
        self.assertEqual({}, self.doc.attrib)

    def test_previous_sibb(self):
        node = self.doc.find('child')
        res = Parser.previousSibling(node)
        self.assertEqual('sib', res.tag)
        self.assertEqual('sib', res.text)
