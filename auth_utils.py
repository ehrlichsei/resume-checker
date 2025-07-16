# auth_utils.py
import os, jwt, datetime
from flask import request, g, jsonify
from functools import wraps

JWT_SECRET = os.environ.get('JWT_SECRET', 'change-me')
EXP_MIN = int(os.environ.get('JWT_EXP_MIN', 15))


def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=EXP_MIN)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=['HS256'])


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing token'}), 401
        token = auth_header[7:]
        try:
            payload = decode_token(token)
            g.user_id = payload['user_id']
        except Exception:
            return jsonify({'error': 'Invalid or expired token'}), 401
        return fn(*args, **kwargs)
    return wrapper
