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


class Extractor(extractors.ContentExtractor):

    def _get_xpath(self, element):
        return 1

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
        title_text_fb = (self.parser.xpath_re(doc,
                            '//meta[@property="og:title"]/@content') or
                         self.parser.xpath_re(doc,
                            '//meta[@name="og:title"]/@content') or '')

        # create filtered versions of title_text, title_text_h1, title_text_fb
        # for finer comparison
        filter_regex = re.compile(r'[^a-zA-Z0-9\ ]')
        filter_title_text = filter_regex.sub('', title_text).lower()
        filter_title_text_h1 = filter_regex.sub('', title_text_h1).lower()
        filter_title_text_fb = filter_regex.sub('', title_text_fb).lower()

        # check for better alternatives for title_text and possibly
        # skip splitting
        if title_text_h1 == title_text:
            title_xpath = self._get_xpath(title_element)
        elif filter_title_text_h1 and \
                filter_title_text_h1 == filter_title_text_fb:
            title_text = title_text_h1
            used_delimeter = True
        elif filter_title_text_h1 and filter_title_text_h1 in filter_title_text \
                and filter_title_text_fb and filter_title_text_fb in filter_title_text \
                and len(title_text_h1) > len(title_text_fb):
            title_text = title_text_h1
            used_delimeter = True
        elif filter_title_text_fb and filter_title_text_fb != filter_title_text \
                and filter_title_text.startswith(filter_title_text_fb):
            title_xpath = self._get_xpath(title_element)

        return title_xpath
