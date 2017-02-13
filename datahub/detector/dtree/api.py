# -*- coding: utf-8 -*-
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

from url_fetcher import UrlFetcher
from extractor import Extractor


def extract_url(url, depth):
    fetcher = UrlFetcher()
    domain = fetcher.get_domain(url)
    links = fetcher.getFullLinks(url, depth)
    extractor = Extractor()
    for url in links:
        std_url = fetcher.standardize_url(url)
        if fetcher.check_url_in_blacklist(domain, url) is False:
            doc = fetcher.get_domain(url)
            if doc:
                article = extractor.extract_content(doc, domain, std_url)
                print(article)
