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

import copy
from newspaper import article
from newspaper.cleaners import DocumentCleaner

from datahub.news_detector.rule.extractor import VideoExtractor


class Article(article.Article):

    def __init__(self, url, title='', source_url='', config=None,
                 extractor=None, **kwargs):
        super(Article, self).__init__(url, title, source_url, config, **kwargs)
        self.link_hash = None
        self.extractor = extractor

    def parse(self):
        if not self.is_downloaded:
            print('Something wrong with network!'
                  'You must `download()` an article before '
                  'calling `parse()` on it!')
            raise article.ArticleException()

        self.doc = self.config.get_parser().fromstring(self.html)
        self.clean_doc = copy.deepcopy(self.doc)

        if self.doc is None:
            # `parse` call failed, return nothing
            return

        # TODO: Fix this, sync in our fix_url() method
        parse_candidate = self.get_parse_candidate()
        self.link_hash = parse_candidate.link_hash  # MD5

        document_cleaner = DocumentCleaner(self.config)

        title = self.extractor.get_title(self.clean_doc)
        self.set_title(title)

        authors = self.extractor.get_authors(self.clean_doc)
        self.set_authors(authors)

        meta_lang = self.extractor.get_meta_lang(self.clean_doc)
        self.set_meta_language(meta_lang)

        if self.config.use_meta_language:
            self.extractor.update_language(self.meta_lang)

        meta_favicon = self.extractor.get_favicon(self.clean_doc)
        self.set_meta_favicon(meta_favicon)

        meta_description = \
            self.extractor.get_meta_description(self.clean_doc)
        self.set_meta_description(meta_description)

        canonical_link = self.extractor.get_canonical_link(
            self.url, self.clean_doc)
        self.set_canonical_link(canonical_link)

        tags = self.extractor.extract_tags(self.clean_doc)
        self.set_tags(tags)

        meta_keywords = self.extractor.get_meta_keywords(
            self.clean_doc)
        self.set_meta_keywords(meta_keywords)

        meta_data = self.extractor.get_meta_data(self.clean_doc)
        self.set_meta_data(meta_data)

        self.publish_date = self.extractor.get_publishing_date(
            self.url,
            self.clean_doc)

        # Before any computations on the body, clean DOM object
        self.doc = document_cleaner.clean(self.doc)

        self.top_node = self.extractor.calculate_best_node(self.doc)
        if self.top_node is not None:
            video_extractor = VideoExtractor(self.config, self.top_node)
            self.set_movies(video_extractor.get_videos())
            self.set_text(self.top_node.xpath)

        if self.config.fetch_images:
            self.fetch_images()

        self.is_parsed = True
        self.release_resources()

    def process(self):
        self.download()
        self.parse()
