import math

from flask import Blueprint
from flask import jsonify
from flask import request
from horizontal_scaling_optimizer.service.api import api
from horizontal_scaling_optimizer.utils import math_helper as mhelper
hso_api = Blueprint('hso_api', __name__)


@hso_api.route('/optimizer/get_cluster_size', methods=['GET'])
def get_cluster_size():
    data = request.get_json()
    try:
        hosts = data['hosts']
        percentage = data['percentage']
        dummy = data['dummy']
        cluster_size = api.get_cluster_size(hosts, dummy)
        result = mhelper.percentage(percentage, cluster_size)
        print ('New cluster size is: %(cluster_size)s' %
               {'cluster_size': result})
        return jsonify({'cluster_size': result})
    except Exception:
        return jsonify({'cluster_size': -1})


@hso_api.route('/optimizer/get_preemtible_instances', methods=['GET'])
def get_preemtible_instances():
    data = request.get_json()
    try:
        result = api.get_preemtible_instances(data['username'],
                                              data['password'],
                                              data['project_id'],
                                              data['auth_ip'], data['domain'])
        return jsonify(result)
    except Exception:
        return ('No instance available for deleting')
