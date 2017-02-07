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


class VnexpressItem(scrapy.Item):
    url = scrapy.Field()
    date = scrapy.Field()
    intro = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    comments = scrapy.Field()
    tags = scrapy.Field()
