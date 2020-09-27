import json
import os
import re

import redis
from flask import Flask, request, redirect, url_for, Response, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
import short_url

from constants import URL_PATTERN

app = Flask(__name__)

redis_instance = redis.StrictRedis(host=os.getenv('REDIS_HOST'),
                                   port=os.getenv('REDIS_PORT'), db=1, decode_responses=True)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/')
def base():
    return redirect(request.base_url + 'swagger/')


@app.route('/get/all/', methods=['GET'])
def get_all_url():
    keys = redis_instance.keys()
    values = [redis_instance.get(key) for key in keys]
    data = {
        'links': [
            {'key': get_short_url(key),
             'value': value}
            for key in keys for value in values
        ]
    }
    return Response(json.dumps(data), mimetype='application/json')


@app.route('/add/', methods=['POST'])
def add_url():
    user_url = request.args.get('url')

    # Validate url
    if re.match(URL_PATTERN, user_url):
        key = request.args.get('key')
        if key in redis_instance.keys():
            return "Your key is already used", 400
        if not key:
            key = short_url.encode_url(get_id_for_url())
        redis_instance.set(key, user_url)
        data = {
            'key': get_short_url(key),
            'value': user_url
        }
        return Response(json.dumps(data), mimetype='application/json')

    return "Bad url", 400


@app.route('/<key>/', methods=['GET'])
def get_url(key):
    return redirect(redis_instance.get(key))


@app.route('/get/<key>/', methods=['GET'])
def redirect_to_url(key):
    value = redis_instance.get(key)
    data = {
        "key": get_short_url(key),
        "value": value
    }
    return Response(json.dumps(data), mimetype='application/json')


def get_id_for_url():
    return len(redis_instance.keys())


def get_short_url(key):
    return request.host_url + key


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('FLASK_PORT'))
