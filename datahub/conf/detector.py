# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy
# of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from oslo_config import cfg

detector_group = cfg.OptGroup(name='news_detector',
                              title='Options for the datahub news_detector'
                                    'service')

detector_engine_opts = [
    cfg.StrOpt('engine',
               default='d-tree',
               help='Decide which engine the datahub news_detector will use'
                    'for auto-detect article format. The list of option is:'
                    'd-tree, hybrid, readability'
                    'Default is d-tree engine.'),
]


def register_opts(conf):
    conf.register_group(detector_group)
    conf.register_opts(detector_engine_opts, group=detector_group)


def list_opts():
    return {
        detector_group: detector_engine_opts
    }
