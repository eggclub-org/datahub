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


class UrlFetcher(object):
    def __init__(self):
        self.load_rules()

    def load_rules(self):
        None

    def get_domain(self, url):
        None

    def get_full_links(self, url):
        None

    def standardize_url(self, url):
        None

    def check_url_in_blacklist(self, domain, url):
        None

    def fetch(self, url):
        None
