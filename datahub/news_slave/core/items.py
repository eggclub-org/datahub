# -*- coding: utf-8 -*-
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

ORIGINAL = 0
CLONE = 1
TRANSLATED = 2


class NewsItem(scrapy.Item):
    # short title of article, required
    title = scrapy.Field()

    # author(s), nullable
    author = scrapy.Field()

    # 0: Original article, 1: Cloned, 2: Translated version, default is 0
    aflag = scrapy.Field()

    # Article's published time in epoch format, required
    publish_date = scrapy.Field()

    # Article category, nullable
    category = scrapy.Field()

    # Summary of article, nullable
    summary = scrapy.Field()

    # Main content of article, required
    content = scrapy.Field()

    # Image's URL of article, nullable
    url_image = scrapy.Field()

    # Keyword, tags of article which was identified by article's author(s).
    # Or top keyword identified by NLP tools
    # nullable
    tags = scrapy.Field()

    # Article URL, required
    url_page = scrapy.Field()

    # Article language, nullable
    language = scrapy.Field()

    # Article rating, nullable
    ratings = scrapy.Field()

    # Article comments, nullable
    comments = scrapy.Field()
