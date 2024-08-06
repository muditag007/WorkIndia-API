from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def get_user_by_username(mysql, username):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    return user

# def token_required(f):
#     @wraps(f)
#     def decorator(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token:
#             return jsonify({'message': 'Token is missing'}), 403
#         try:
#             token = token.split()[1]
#             data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
#             request.user_id = data['user_id']
#         except:
#             return jsonify({'message': 'Token is invalid'}), 403
#         return f(*args, **kwargs)
#     return decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        
        try:
            data = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated
