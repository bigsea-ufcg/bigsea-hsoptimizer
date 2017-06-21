import random

from flask import Blueprint
from flask import request
from horizontal_scaling_optimizer.service import api

hso_api = Blueprint('hso_api', __name__)


@hso_api.route('/optimizer/get_cluster_size/', methods=['POST'])
def get_cluster_size():
    data = request.get_json()
    try:
        hosts = data['hosts']
        return api.get_cluster_size(hosts)
    except Exception:
        return -1


