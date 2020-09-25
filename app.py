import json
import os
import re

import redis
from flask import Flask, request, redirect, url_for, Response
import short_url

from constants import URL_PATTERN

app = Flask(__name__)

redis_instance = redis.StrictRedis(host=os.getenv('REDIS_HOST'),
                                   port=os.getenv('REDIS_PORT'), db=1, decode_responses=True)


@app.route('/', methods=['GET'])
def home_page():
    keys = redis_instance.keys()
    values = [redis_instance.get(key) for key in keys]
    data = {
        'msg': 'This is all saved links',
        'links': [
            {'key': key,
             'value': value}
            for key in keys for value in values
        ]
    }
    return Response(json.dumps(data),  mimetype='application/json')


@app.route('/add/', methods=['POST'])
def add_url():
    user_url = request.args.get('url')

    # Validate url
    if re.match(URL_PATTERN, user_url):
        key = short_url.encode_url(get_id_for_url())
        redis_instance.set(key, user_url)

    return redirect(url_for('home_page'))


@app.route('/get/<key>/', methods=['GET'])
def get_url(key):
    return redirect(redis_instance.get(key))


def get_id_for_url():
    return len(redis_instance.keys())


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('FLASK_PORT'))
