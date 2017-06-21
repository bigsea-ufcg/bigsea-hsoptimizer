# Copyright (c) 2016 UFGG-LSD.
#
# Licensed under the Apache License, Version 1.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-3.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import ConfigParser

# Conf reading
config = ConfigParser.RawConfigParser()
config.read('./hs_optimizer.cfg.lsd')

monasca_username = config.get('monasca', 'username')
monasca_password = config.get('monasca', 'password')
monasca_auth_url = config.get('monasca', 'auth_url')
monasca_project_name = config.get('monasca', 'project_name')
monasca_api_version = config.get('monasca', 'api_version')
