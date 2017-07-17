# Copyright (c) 2017 UFCG-LSD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import horizontal_scaling_optimizer as hso
from horizontal_scaling_optimizer.utils import shell
from horizontal_scaling_optimizer.utils.logger import Log

LOG = Log("HS_RPredictor", '%(log_dir)s/hs_predictor.log' % {'log_dir':
                                                             hso.LOG_DIR})

class RPredictor():
    def __init__(self):
        self.pred_file = hso.HORIZONTAL_SCALING_DIR + '/resources/predictor.R'
        self.pred_unit = 2  # 2 horizons of 15 minutes = 30 minutes prediction

    def get_title(self):
        return 'R Predictor'

    def predict(self, hosts):
        cluster_size = 0
        for host in hosts:
            host_path = ('%(host_dir)s/%(host)s.txt' %
                         {'host_dir': hso.HOSTS_DIR, 'host': host})
            machines = shell.execute_r_script(
                self.pred_file, ['%s' % host_path, "%s" % self.pred_unit])
            print ("%(time)s | Prediction returned %(machines)s machines for "
                   "host %(host)s" % {'time': time.strftime("%H:%M:%S"),
                                      'machines': machines, 'host': host})
            cluster_size += machines
        return cluster_size
