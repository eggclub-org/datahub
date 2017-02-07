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

# NOTE(hieulq): this is just an example of scrapy spider

import json
import scrapy

from datahub.news_slave.core.items import VnexpressItem


class VneSpider(scrapy.Spider):
    name = "sohoa"
    allowed_domains = ["sohoa.vnexpress.net",
                       "usi.saas.vnexpress.net"]
    start_urls = (
        "http://sohoa.vnexpress.net/",
    )

    def parse(self, response):
        # Parse articles
        for article_url in response.xpath(
            '//a[contains(@href, "sohoa.vnexpress.net")]/@href'
        ).re(r'.*-\d{7,}\.html$'):
            yield scrapy.Request(article_url,
                                 callback=self.parse_contents)

        # Parse pages
        for page in response.xpath('//a[contains(@href, "page")]/@href'
                                   ).extract():
            yield scrapy.Request(page, self.parse)

    def parse_contents(self, response):
        item = VnexpressItem()
        # Parse all things we can parse immediately
        post_date = response.css('div.block_timer::text'
                                 ).extract()
        item['url'] = response.url
        item['date'] = [p.strip() for p in post_date[:2]]
        item['intro'] = response.css('div.short_intro::text'
                                     ).extract_first().strip()
        item['title'] = response.xpath('//div[@class="title_news"]/h1/text()'
                                       ).extract_first().strip()
        item['content'] = response.xpath(
            '//div[contains(@class, "fck_detail")]//p//text()'
        ).extract()
        item['tags'] = response.xpath('//a[@class="tag_item"]//text()'
                                      ).extract()

        # IDs to get comments
        site_id = response.xpath('//meta[@name="tt_site_id"]/@content'
                                 ).extract_first()
        article_id = response.xpath('//meta[@name="tt_article_id"]/@content'
                                    ).extract_first()
        # Set the limit
        limit = 24
        # URL for AJAX calling
        URL = ('http://usi.saas.vnexpress.net/index/get?offset=0&limit={limit}'
               '&sort=like&objectid={article_id}&objecttype=1&siteid={site_id}'
               ).format(limit=limit, article_id=article_id, site_id=site_id)
        # Queue comment request for parsing later
        request_comment = scrapy.Request(URL,
                                         callback=self.parse_comment)
        # Pass the incomplete item to callback
        request_comment.meta['item'] = item
        yield request_comment

    def parse_comment(self, response):
        # Now make the full item
        item = response.meta['item']
        item['comments'] = self._extract_comment(response.body)
        yield item

    @staticmethod
    def _extract_comment(cont):
        cont = json.loads(cont)
        # If error, return nothing
        if cont.get('error') != 0:
            return []
        # Else processing comments
        lis = []
        items = cont['data']['items']
        for i in items:
            lis.append(i['content'])
            if i.get('replys'):
                lis = lis + [r['content'] for r in i['replys']['items']]
        return lis
