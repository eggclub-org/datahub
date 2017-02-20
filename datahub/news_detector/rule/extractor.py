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

from newspaper import extractors
import re

RE_LANG = r'^[A-Za-z]{2}$'


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
        title_xpath = None
        title_element = self.parser.getElementsByTag(doc, tag='title')
        # no title found
        if title_element is None or len(title_element) == 0:
            return title_xpath

        # title elem found
        title_text = title_element[0].text

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
                result.append(item)
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
                    if len(curname) > 0:
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

            if len(match.text) > 0:
                authors.extend(parse_byline(match))

        return uniqify_list(authors)

        # TODO Method 2: Search raw html for a by-line
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
                    break
        return attr.xpath

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
