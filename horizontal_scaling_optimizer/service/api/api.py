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

import datetime

from horizontal_scaling_optimizer.service.horizontal_scale import r_predictor
from horizontal_scaling_optimizer.utils.logger import Log
from horizontal_scaling_optimizer.utils import monasca
from horizontal_scaling_optimizer.utils import shell


LOG = Log("HS_Servicev10", "hs_optimizer.log")
predictor = r_predictor.RPredictor()
monasca_monitor = monasca.MonascaMonitor()


def get_cluster_size(hosts):
    _populate_host_utilization_files(hosts)
    return _get_new_cluster_size(hosts)

def _get_new_cluster_size(hosts):
    return predictor.predict(hosts)


def _get_start_time(time_diff):
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(hours=time_diff)
    return (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')


def _from_mb_to_gb(size, precision=2):
    size = size/1024.0
    return "%.*f" % (precision, size)


def _get_used_mem(value):
    return (100 - value) / 100.0


def _populate_host_utilization_files(hosts):
    for host in hosts:
        output_file = '%s.txt' % host
        dimensions = {'hostname': host}

        cpu_info = monasca_monitor.get_stats_measurements('cpu.percent',
                                                          dimensions,
                                                          _get_start_time(2))
        mem_info = monasca_monitor.get_stats_measurements('mem.usable_perc',
                                                          dimensions,
                                                          _get_start_time(2))
        total_cpu = monasca_monitor.last_measurement('cpu.total_logical_cores',
                                                     dimensions,
                                                     _get_start_time(1))[1]
        total_mem = _from_mb_to_gb(
            monasca_monitor.last_measurement('mem.total_mb', dimensions,
                                             _get_start_time(1))[1])

        counter = 0
        index = 0
        for i in range(len(cpu_info)):
            if counter % 3 == 0:
                index += 1
            cpu = cpu_info[i][1]/100
            mem = _get_used_mem(mem_info[i][1])

            line = '%s;%s;%s;%s;%s\n' % (cpu, mem, total_cpu, total_mem, index)
            counter += 1

            shell.write_to_file(output_file, line)