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
from dateutil.parser import parse as date_parser
from newspaper import extractors
from newspaper import urls
from newspaper.videos import extractors as ve
import re

RE_LANG = r'^[A-Za-z]{2}$'
NO_STRINGS = set()
A_REL_TAG_SELECTOR = "a[rel=tag]"
A_HREF_TAG_SELECTOR = ("a[href*='/tag/'], a[href*='/tags/'], "
                       "a[href*='/topic/'], a[href*='?keyword=']")


class VideoExtractor(ve.VideoExtractor):

    def __init__(self, config, top_node):
        super(VideoExtractor, self).__init__(config, top_node)

    def get_src(self, node):
        return self.parser.getAttribute(node, 'src') or \
            self.parser.getAttribute(node, 'data-src')


class Extractor(extractors.ContentExtractor):

    def get_title(self, doc):
        """Fetch the article title and analyze it

        Assumptions:
        - title tag is the most reliable (inherited from Goose)
        - h1, if properly detected, is the best (visible to users)
        - og:title and h1 can help improve the title extraction
        - python == is too strict, often we need to compare fitlered
          versions, i.e. lowercase and ignoring special chars

        Explicit rules:
        1. title == h1, no need to split
        2. h1 similar to og:title, use h1
        3. title contains h1, title contains og:title, len(h1) > len(og:title)
         use h1
        4. title starts with og:title, use og:title
        5. use title, after splitting
        """
        title_xpath = ''
        title_element = self.parser.getElementsByTag(doc, tag='title')
        # no title found
        if not title_element:
            return title_xpath

        # title elem found
        title_text = title_element[0].text
        title_xpath = title_element[0].xpath

        # title from h1
        # - extract the longest text from all h1 elements
        # - too short texts (less than 2 words) are discarded
        # - clean double spaces
        title_text_h1 = ''
        title_element_h1_list = self.parser.getElementsByTag(doc, tag='h1')
        if title_element_h1_list:
            # sort by len and set the longest
            title_element_h1_list.sort(key=lambda obj: len(obj.text),
                                       reverse=True)
            title_text_h1 = title_element_h1_list[0].text
            # clean double spaces
            title_text_h1 = ' '.join([x for x in title_text_h1.split() if x])

        # title from og:title
        title_element_fb = (self.parser.xpath_re(doc,
                            '//meta[@property="og:title"]/@content') or
                            self.parser.xpath_re(doc,
                            '//meta[@name="og:title"]/@content') or '')
        title_text_fb = title_element_fb[0].text

        # create filtered versions of title_text, title_text_h1, title_text_fb
        # for finer comparison
        filter_regex = re.compile(r'[^a-zA-Z0-9\ ]')
        filter_title_text = filter_regex.sub('', title_text).lower()
        filter_title_text_h1 = filter_regex.sub('', title_text_h1).lower()
        filter_title_text_fb = filter_regex.sub('', title_text_fb).lower()

        # check for better alternatives for title_text and possibly
        # skip splitting
        if title_text_h1 == title_text:
            title_xpath = title_element[0].xpath
        elif filter_title_text_h1 and \
                filter_title_text_h1 == filter_title_text_fb:
            title_xpath = title_element_h1_list[0].xpath
        elif filter_title_text_h1 and \
                filter_title_text_h1 in filter_title_text \
                and filter_title_text_fb and \
                filter_title_text_fb in filter_title_text \
                and len(title_text_h1) > len(title_text_fb):
            title_xpath = title_element_h1_list[0].xpath
        elif filter_title_text_fb and \
                filter_title_text_fb != filter_title_text \
                and filter_title_text.startswith(filter_title_text_fb):
            title_xpath = title_element_fb[0].xpath

        return title_xpath

    def get_authors(self, doc):
        """Fetch the authors of the article, return as a list
        Only works for english articles
        """
        _digits = re.compile('\d')

        def contains_digits(d):
            return bool(_digits.search(d))

        def uniqify_list(lst):
            """Remove duplicates from provided list but maintain original order.
              Derived from http://www.peterbe.com/plog/uniqifiers-benchmark
            """
            seen = {}
            result = []
            for item in lst:
                if item.text.lower() in seen:
                    continue
                seen[item.text.lower()] = 1
                result.append(item.xpath)
            return result

        def parse_byline(obj):
            """Takes a candidate line of html or text and
            extracts out the name(s) in list form
            search_str('<div>By: <strong>Lucas Ou-Yang</strong>, \
                       <strong>Alex Smith</strong></div>')
            ['Lucas Ou-Yang', 'Alex Smith']
            """
            search_str = obj.text
            # Remove HTML boilerplate
            search_str = re.sub('<[^<]+?>', '', search_str)

            # Remove original By statement
            search_str = re.sub('[bB][yY][\:\s]|[fF]rom[\:\s]', '', search_str)

            search_str = search_str.strip()

            # Chunk the line by non alphanumeric tokens (few name exceptions)
            name_tokens = re.split("[^\w\'\-\.]", search_str)
            name_tokens = [s.strip() for s in name_tokens]

            _authors = []
            # List of first, last name tokens
            curname = []
            DELIM = ['and', ',', '']

            for token in name_tokens:
                if token in DELIM:
                    if curname:
                        _authors.append(obj)
                        curname = []

                elif not contains_digits(token):
                    curname.append(token)

            # One last check at end
            valid_name = (len(curname) >= 2)
            if valid_name:
                _authors.append(obj)

            return _authors

        # Try 1: Search popular author tags for authors

        ATTRS = ['name', 'rel', 'itemprop', 'class', 'id']
        VALS = ['author', 'byline', 'dc.creator']
        matches = []
        authors = []

        for attr in ATTRS:
            for val in VALS:
                # found = doc.xpath('//*[@%s="%s"]' % (attr, val))
                found = self.parser.getElementsByTag(doc, attr=attr, value=val)
                matches.extend(found)

        for match in matches:
            if match.ele.tag == 'meta':
                match.xpath += '/@content'
                match.text = match.ele.xpath(match.xpath)[0]

            if match.text:
                authors.extend(parse_byline(match))

        return uniqify_list(authors)

        # TODO(hieulq) Method 2: Search raw html for a by-line
        # match = re.search('By[\: ].*\\n|From[\: ].*\\n', html)
        # try:
        #    # Don't let zone be too long
        #    line = match.group(0)[:100]
        #    authors = parse_byline(line)
        # except:
        #    return [] # Failed to find anything
        # return authors

    def get_meta_lang(self, doc):
        """Extract content language from meta
        """
        # we have a lang attribute in html
        attr = self.parser.getAttribute(doc, attr='lang')
        if not attr:
            # look up for a Content-Language in meta
            items = [
                {'tag': 'meta', 'attr': 'http-equiv',
                    'value': 'content-language'},
                {'tag': 'meta', 'attr': 'name', 'value': 'lang'}
            ]
            for item in items:
                meta = self.parser.getElementsByTag(doc, **item)
                if meta:
                    meta = meta[0]
                    meta.xpath += '/@content'
                    meta.text = meta.ele.xpath(meta.xpath)[0]
                    attr = meta
                    return attr.text.lower(), attr.xpath

            return '', ''
        return attr.lower(), '/html/@lang'

    def get_favicon(self, doc):
        """Extract the favicon from a website
        <link rel="shortcut icon" type="image/png" href="favicon.png" />
        <link rel="icon" type="image/png" href="favicon.png" />
        """
        kwargs = {'tag': 'link', 'attr': 'rel', 'value': 'icon'}
        meta = self.parser.getElementsByTag(doc, **kwargs)
        if meta:
            favicon = meta[0].xpath + '/@href'
            return favicon
        return ''

    def get_meta_content(self, doc, meta_name):
        """Extract a given meta content form document.
        Example metaNames:
            "meta[name=description]"
            "meta[name=keywords]"
            "meta[property=og:type]"
        """
        meta = self.parser.css_select(doc, meta_name)
        if meta:
            return meta[0].xpath + '/@content'
        return ''

    def get_canonical_link(self, doc):
        """
        Return the article's canonical URL

        Gets the first available value of:
        1. The rel=canonical tag
        2. The og:url tag
        """
        canonical, og_url = '', ''
        link, og = None, None
        links = self.parser.getElementsByTag(doc, tag='link', attr='rel',
                                             value='canonical')
        if links:
            link = links[0]
            link.xpath += '/@href'
            link.text = self.parser.getAttribute(link.ele, 'href')
            canonical = link.text

        ogs = self.parser.css_select(doc, 'meta[property="og:url"]')
        if ogs:
            og = ogs[0]
            og.xpath += '/@content'
            og.text += self.parser.getAttribute(og.ele, 'content')
            og_url = og.text

        if canonical:
            return link.xpath
        elif og_url:
            return og.xpath

        return ''

    def extract_tags(self, doc):
        if len(list(doc)) == 0:
            return NO_STRINGS
        elements = self.parser.css_select(
            doc, A_REL_TAG_SELECTOR)
        if not elements:
            elements = self.parser.css_select(
                doc, A_HREF_TAG_SELECTOR)
            if not elements:
                return NO_STRINGS

        tags = []
        for el in elements:
            tag = el.xpath
            if tag:
                tags.append(tag)
        return set(tags)

    def get_meta_data(self, doc):
        data = defaultdict(dict)
        properties = self.parser.css_select(doc, 'meta')
        for prop in properties:
            key = prop.ele.attrib.get('property') or \
                  prop.ele.attrib.get('name')
            value = None
            if prop.ele.attrib.get('content'):
                value = prop.xpath + '/@content'
            elif prop.ele.attrib.get('value'):
                value = prop.xpath + '/@value'

            if not key or not value:
                continue

            key, value = key.strip(), value.strip()

            if ':' not in key:
                data[key] = prop.xpath
                continue

            key = key.split(':')
            key_head = key.pop(0)
            ref = data[key_head]

            if isinstance(ref, str):
                data[key_head] = {key_head: ref}
                ref = data[key_head]

            for idx, part in enumerate(key):
                if idx == len(key) - 1:
                    ref[part] = value
                    break
                if not ref.get(part):
                    ref[part] = dict()
                elif isinstance(ref.get(part), str):
                    # Not clear what to do in this scenario,
                    # it's not always a URL, but an ID of some sort
                    ref[part] = {'identifier': ref[part]}
                ref = ref[part]
        return data

    def get_publishing_date(self, url, doc):
        """3 strategies for publishing date extraction. The strategies
        are descending in accuracy and the next strategy is only
        attempted if a preferred one fails.

        1. Pubdate from URL
        2. Pubdate from metadata
        3. Raw regex searches in the HTML + added heuristics
        """

        def parse_date_str(date_str):
            try:
                datetime_obj = date_parser(date_str)
                return datetime_obj
            except Exception:
                # near all parse failures are due to URL dates without a day
                # specifier, e.g. /2014/04/
                return None

        date_match = re.search(urls.DATE_REGEX, url)
        if date_match:
            date_str = date_match.group(0)
            datetime_obj = parse_date_str(date_str)
            if datetime_obj:
                return datetime_obj

        PUBLISH_DATE_TAGS = [
            {'attribute': 'property', 'value': 'rnews:datePublished',
             'content': 'content'},
            {'attribute': 'property', 'value': 'article:published_time',
             'content': 'content'},
            {'attribute': 'name', 'value': 'OriginalPublicationDate',
             'content': 'content'},
            {'attribute': 'itemprop', 'value': 'datePublished',
             'content': 'datetime'},
            {'attribute': 'property', 'value': 'og:published_time',
             'content': 'content'},
            {'attribute': 'name', 'value': 'article_date_original',
             'content': 'content'},
            {'attribute': 'name', 'value': 'publication_date',
             'content': 'content'},
            {'attribute': 'name', 'value': 'sailthru.date',
             'content': 'content'},
            {'attribute': 'name', 'value': 'PublishDate',
             'content': 'content'},
        ]
        for known_meta_tag in PUBLISH_DATE_TAGS:
            meta_tags = self.parser.getElementsByTag(
                doc,
                attr=known_meta_tag['attribute'],
                value=known_meta_tag['value'])
            if meta_tags:
                date_str = self.parser.getAttribute(
                    meta_tags[0].ele,
                    known_meta_tag['content'])
                datetime_obj = parse_date_str(date_str)
                if datetime_obj:
                    return meta_tags[0].xpath + '/@' + \
                           known_meta_tag['content']

        return None

    def calculate_best_node(self, doc):
        top_node = None
        nodes_to_check = self.nodes_to_check(doc)
        starting_boost = float(1.0)
        cnt = 0
        i = 0
        parent_nodes = []
        nodes_with_text = []

        for node in nodes_to_check:
            text_node = self.parser.getText(node.ele)
            word_stats = self.stopwords_class(language=self.language).\
                get_stopword_count(text_node)
            high_link_density = self.is_highlink_density(node.ele)
            if word_stats.get_stopword_count() > 2 and not high_link_density:
                nodes_with_text.append(node)

        nodes_number = len(nodes_with_text)
        negative_scoring = 0
        bottom_negativescore_nodes = float(nodes_number) * 0.25

        for node in nodes_with_text:
            boost_score = float(0)
            # boost
            if self.is_boostable(node.ele):
                if cnt >= 0:
                    boost_score = float((1.0 / starting_boost) * 50)
                    starting_boost += 1
            # nodes_number
            if nodes_number > 15:
                if (nodes_number - i) <= bottom_negativescore_nodes:
                    booster = float(
                        bottom_negativescore_nodes - (nodes_number - i))
                    boost_score = float(-pow(booster, float(2)))
                    negscore = abs(boost_score) + negative_scoring
                    if negscore > 40:
                        boost_score = float(5)

            text_node = self.parser.getText(node.ele)
            word_stats = self.stopwords_class(language=self.language).\
                get_stopword_count(text_node)
            upscore = int(word_stats.get_stopword_count() + boost_score)

            parent_node = self.parser.getParent(node)
            self.update_score(parent_node, upscore)
            self.update_node_count(parent_node, 1)

            if parent_node not in parent_nodes:
                parent_nodes.append(parent_node)

            # Parent of parent node
            parent_parent_node = self.parser.getParent(parent_node)
            if parent_parent_node is not None:
                self.update_node_count(parent_parent_node, 1)
                self.update_score(parent_parent_node, upscore / 2)
                if parent_parent_node not in parent_nodes:
                    parent_nodes.append(parent_parent_node)
            cnt += 1
            i += 1

        top_node_score = 0
        for e in parent_nodes:
            score = self.get_score(e)

            if score > top_node_score:
                top_node = e
                top_node_score = score

            if top_node is None:
                top_node = e

        # Add xpath text() function
        if top_node:
            top_node.xpath += '//text()'
        return top_node

    def _get_urls(self, doc, titles):
        """Return a list of urls or a list of (url, title_text) tuples
        if specified.
        """
        if doc is None:
            return []

        a_kwargs = {'tag': 'a'}
        a_tags = self.parser.getElementsByTag(doc, **a_kwargs)

        # TODO(hieulq): this should be refactored! We should have a seperate
        # method which siphones the titles our of a list of <a> tags.
        if titles:
            return [(a.ele.get('href'), a.ele.text) for a in a_tags
                    if a.ele.get('href') and '#' not in a.ele.get('href')]
        return [a.ele.get('href') for a in a_tags if a.ele.get('href') and
                '#' not in a.ele.get('href')]
