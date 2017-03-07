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

from oslo_log import log as logging
from oslo_utils import importutils

import datahub.conf

DTREE_ENGINE = 'datahub.news_detector.dtree.engine.Engine'
READABILITY_ENGINE = 'datahub.news_detector.rule.engine.Engine'

LOG = logging.getLogger(__name__)
CONF = datahub.conf.CONF


def engine():
    engine_class = None
    engine_conf = CONF.news_detector.engine
    if engine_conf == 'd-tree':
        engine_class = DTREE_ENGINE
    elif engine_conf == 'rule':
        engine_class = READABILITY_ENGINE

    if engine_class:
        cls = importutils.import_class(engine_class)
    else:
        LOG.error('The configuration options for news news_detector engine is '
                  'wrong! Please identify the correct news detector engine in '
                  'supported engine list.')
        raise NotImplementedError

    return cls()
