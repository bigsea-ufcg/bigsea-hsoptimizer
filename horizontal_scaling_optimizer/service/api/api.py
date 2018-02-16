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
import time
import horizontal_scaling_optimizer as hso

from horizontal_scaling_optimizer.service.horizontal_scaling import r_predictor
from horizontal_scaling_optimizer.utils.logger import Log
from horizontal_scaling_optimizer.utils import monasca
from horizontal_scaling_optimizer.utils import openstack
from horizontal_scaling_optimizer.utils import shell


LOG = Log("HS_Servicev10", '%(log_dir)s/hs_optimizer.log' % {'log_dir':
                                                             hso.LOG_DIR})
predictor = r_predictor.RPredictor()
monasca_monitor = monasca.MonascaMonitor()


def get_cluster_size(hosts, dummy=False):
    print ("%(time)s | Getting cluster size based on hosts utilization" %
           {'time': time.strftime("%H:%M:%S")})
    util_info = _populate_host_utilization_files(hosts)
    return _get_new_cluster_size(hosts, util_info, dummy)


def get_preemtible_instances(username, password, project_id, auth_ip, domain):
    connector = openstack.OpenStackConnector(LOG)
    sahara = connector.get_sahara_client(username, password, project_id,
                                         auth_ip, domain)
    clusters = connector.list_cluster_with_name(sahara, 'osahara')
    preemtible = {}
    for cluster in clusters:
        preemtible[cluster.id] = _get_preemtible_instances(cluster)

    return preemtible


def _get_preemtible_instances(cluster):
    preemtible = {1: [], 2: [], 3: []}
    for ng in cluster.node_groups:
        if 'master' in ng['name'].lower():
            preemtible[1] = _add_instance_id(ng['instances'])
        elif ('slave' in ng['name'].lower() and
                'opportunistic' not in ng['name'].lower()):
            preemtible[2] = _add_instance_id(ng['instances'])
        elif ('slave' in ng['name'].lower() and
              'opportunistic' in ng['name'].lower()):
            preemtible[3] = _add_instance_id(ng['instances'])
    return preemtible


def _add_instance_id(instances):
    result = []
    for instance in instances:
        result.append(instance['instance_id'])
    return result


def _get_new_cluster_size(hosts, util_info=None, dummy=False):
    print ("%(time)s | Calculating cluster size" %
           {'time': time.strftime("%H:%M:%S")})
    if not dummy:
        return predictor.predict(hosts)
    else:
        if not util_info:
            return -1
        return _calculate_available_instances(util_info)


def _calculate_available_instances(util_info):
    total_vms = 0
    for host in util_info:
        free_cores = host['total_cpu'] * ((1 - host['cpu']) * 4)
        free_mem = host['total_mem'] * ((1 - host['mem']) * 1)

        hadoop_cores = 4
        hadoop_mem = 2

        num_vms_cores = free_cores / hadoop_cores
        num_vms_mem = free_mem / hadoop_mem

        total_vms += max(0, min(num_vms_cores, num_vms_mem))

    return total_vms


def _get_start_time(time_diff):
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(hours=time_diff)
    return (now - delta).strftime('%Y-%m-%dT%H:%M:%SZ')


def _from_mb_to_gb(size, precision=2):
    size = size/1024.0
    return "%.*f" % (precision, size)


def _get_used_mem(value):
    return (100 - value) / 100.0


def _populate_host_utilization_files(hosts, dummy=False):
    util_info = {}
    for host in hosts:
        print ("%(time)s | Getting CPU and RAM utilization for host %(host)s"
               % {'time': time.strftime("%H:%M:%S"), 'host': host})

        time.sleep(5)
        output_file = '%(hosts_dir)s/%(host)s.txt' % (
            {'hosts_dir': hso.HOSTS_DIR, 'host': host})

        dimensions = {'hostname': host}

        cpu_info = monasca_monitor.get_stats_measurements(
            'cpu.percent', dimensions, _get_start_time(2))

        mem_info = monasca_monitor.get_stats_measurements(
            'mem.usable_perc', dimensions, _get_start_time(2))

        total_cpu = monasca_monitor.last_measurement(
            'cpu.total_logical_cores', dimensions, _get_start_time(1))[1]

        total_mem = _from_mb_to_gb(monasca_monitor.last_measurement(
            'mem.total_mb', dimensions, _get_start_time(1))[1])

        counter = 0
        index = 0
        shell.clean_file(output_file)
        if not dummy:
            for i in range(len(cpu_info)):
                if counter % 3 == 0:
                    index += 1
                cpu = cpu_info[i][1]/100
                mem = _get_used_mem(mem_info[i][1])

                line = '%s;%s;%s;%s;%s\n' % (cpu, mem, total_cpu, total_mem,
                                             index)
                counter += 1

            shell.write_to_file(output_file, line)
        else:
            cpu = cpu_info[-1][1]/100
            mem = _get_used_mem(mem_info[-1][1])
            util_info[host] = {'cpu': cpu, 'mem': mem, 'total_cpu': total_cpu,
                               'total_mem': total_mem}
    return util_info


