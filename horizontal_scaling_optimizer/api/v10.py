from flask import Blueprint
from flask import jsonify
from flask import request
from horizontal_scaling_optimizer.service.api import api

hso_api = Blueprint('hso_api', __name__)


@hso_api.route('/optimizer/get_cluster_size', methods=['POST'])
def get_cluster_size():
    data = request.get_json()
    try:
        hosts = data['hosts']
        result = api.get_cluster_size(hosts)
        print 'New cluster size is: %(cluster_size)s' % {'cluster_size': result}
        return jsonify({'cluster_size': result})
    except Exception:
        return jsonify({'cluster_size': -1})


@hso_api.route('/optimizer/get_preemtible_instances', methods=['GET'])
def get_preemtible_instances():
    try:
        result = api.get_preemtible_instances()
        return result
    except Exception:
        return ('No instance available for deleting')
