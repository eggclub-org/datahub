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

from newspaper import configuration

from datahub.news_detector.rule.parser import Parser


class SourceConfig(configuration.Configuration):

    def __init__(self):
        super(SourceConfig, self).__init__()

        self.set_language("vi")
        self.fetch_images = False
        self.browser_user_agent = 'datahub/1.0'

    def get_parser(self):
        return Parser
