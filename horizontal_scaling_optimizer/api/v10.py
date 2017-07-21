from flask import Blueprint
from flask import jsonify
from flask import request
from horizontal_scaling_optimizer.service.api import api

hso_api = Blueprint('hso_api', __name__)


@hso_api.route('/optimizer/get_cluster_size', methods=['GET'])
def get_cluster_size():
    data = request.get_json()
    try:
        hosts = data['hosts']
        result = api.get_cluster_size(hosts)
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
