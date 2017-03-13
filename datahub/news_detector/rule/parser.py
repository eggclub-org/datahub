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

from html.parser import HTMLParser

import lxml.etree
import lxml.html
import lxml.html.clean

from newspaper import parsers
from newspaper import text


class ObjectParser(object):
    def __init__(self, ele, xpath, text=''):
        self.ele = ele
        self.xpath = xpath
        if isinstance(ele, lxml.html.HtmlComment) or \
                isinstance(ele, lxml.etree._Comment):
            self.text = ele.text
        elif text:
            self.text = text
        elif ele is not None:
            self.text = Parser.getText(ele)
        else:
            self.text = ''

    def clear(self):
        self.ele.clear()
        self.xpath = None
        self.text = None

    def insert(self, idx, element):
        self.ele.insert(idx, element)


# Decorator for convert ObjectParser to LXML object
def check(idx=[], *types):
    def check_type(f):

        def re_f(*args, **kwargs):
            for (i, typ) in zip(idx, types):
                if isinstance(args[i], typ) and typ == ObjectParser:
                    args = args[:i] + (args[i].ele,) + args[i + 1:]
            return f(*args, **kwargs)
        re_f.__name__ = f.__name__
        return re_f
    return check_type


class Parser(parsers.Parser):

    @classmethod
    def xpath_re(cls, node, expression):
        result = []
        regexp_namespace = "http://exslt.org/regular-expressions"
        items = node.xpath(expression, namespaces={'re': regexp_namespace})
        for item in items:
            if isinstance(item, str):
                result.append(ObjectParser(None, expression, item))
            else:
                result.append(ObjectParser(item, expression))
        return result

    @classmethod
    def drop_tag(cls, nodes):
        if isinstance(nodes, list):
            for node in nodes:
                node.ele.drop_tag()
        else:
            nodes.ele.drop_tag()

    @classmethod
    @check([1], ObjectParser)
    def getText(cls, node):
        txts = [i for i in node.itertext()]
        return text.innerTrim(' '.join(txts).strip())

    @classmethod
    @check([1], ObjectParser)
    def css_select(cls, node, selector):
        result = []
        tree = lxml.etree.ElementTree(node)
        items = node.cssselect(selector)
        for item in items:
            result.append(ObjectParser(item, tree.getpath(item)))
        return result

    @classmethod
    @check([1], ObjectParser)
    def nodeToString(cls, node):
        """`decode` is needed at the end because `etree.tostring`
        returns a python bytestring
        """
        return lxml.etree.tostring(node, method='html').decode()

    @classmethod
    @check([1], ObjectParser)
    def getElementsByTag(
            cls, node, tag=None, attr=None, value=None, childs=False):
        result = []
        NS = "http://exslt.org/regular-expressions"
        # selector = tag or '*'
        selector = 'descendant-or-self::%s' % (tag or '*')
        if attr and value:
            selector = '%s[re:test(@%s, "%s", "i")]' % (selector, attr, value)
        elems = node.xpath(selector, namespaces={"re": NS})
        # remove the root node
        # if we have a selection tag
        if node in elems and (tag or childs):
            elems.remove(node)
        tree = lxml.etree.ElementTree(node)
        for elem in elems:
            result.append(ObjectParser(elem, tree.getpath(elem)))
        return result

    @classmethod
    @check([1], ObjectParser)
    def childNodesWithText(cls, node):
        root = node
        # create the first text node
        # if we have some text in the node
        if root.text:
            t = lxml.html.HtmlElement()
            t.text = root.text
            t.tag = 'text'
            root.text = None
            root.insert(0, t)
        # loop childs
        for c, n in enumerate(list(root)):
            idx = root.index(n)
            # don't process texts nodes
            if n.tag == 'text':
                continue
            # create a text node for tail
            if n.tail:
                t = cls.createElement(tag='text', text=n.tail, tail=None)
                root.insert(idx + 1, t)
        return list(root)

    @classmethod
    @check([1], ObjectParser)
    def getChildren(cls, node):
        return node.getchildren()

    @classmethod
    def getComments(cls, node):
        result = []
        tree = lxml.etree.ElementTree(node)
        items = node.xpath('//comment()')
        for item in items:
            result.append(ObjectParser(item, tree.getpath(item)))
        return result

    @classmethod
    def get_parent_xpath(cls, xpath):
        if "/@" in xpath:
            xpath = xpath.split("/@")[0]

        xpath = xpath.rsplit("/", 1)[0]
        return xpath

    @classmethod
    def getParent(cls, node):
        if isinstance(node, ObjectParser):
            return ObjectParser(node.ele.getparent(),
                                cls.get_parent_xpath(node.xpath))
        else:
            return node.getparent()

    @classmethod
    @check([1], ObjectParser)
    def remove(cls, node):
        parent = node.getparent()
        if parent is not None:
            if node.tail:
                prev = node.getprevious()
                if prev is None:
                    if not parent.text:
                        parent.text = ''
                    parent.text += ' ' + node.tail
                else:
                    if not prev.tail:
                        prev.tail = ''
                    prev.tail += ' ' + node.tail
            node.clear()
            parent.remove(node)

    @classmethod
    @check([1], ObjectParser)
    def getTag(cls, node):
        return node.tag

    @classmethod
    @check([1], ObjectParser)
    def previousSibling(cls, node):
        nodes = []
        for c, n in enumerate(node.itersiblings(preceding=True)):
            nodes.append(n)
            if c == 0:
                break
        return nodes[0] if nodes else None

    # NOTE(hieulq): get attr of iframe data-src is not implemented in video
    # extractor
    @classmethod
    @check([1], ObjectParser)
    def getAttribute(cls, node, attr=None):
        if attr:
            attr = node.attrib.get(attr, None)
        if attr:
            attr = HTMLParser().unescape(attr)
        return attr

    @classmethod
    @check([1], ObjectParser)
    def delAttribute(cls, node, attr=None):
        if attr:
            _attr = node.attrib.get(attr, None)
            if _attr:
                del node.attrib[attr]

    @classmethod
    @check([1], ObjectParser)
    def setAttribute(cls, node, attr=None, value=None):
        if attr and value:
            node.set(attr, value)
