from __future__ import division
from mailgun import *
from pagerduty import *
from redis import Redis
import time
from functools import update_wrapper
from models import Base, User
from flask import Flask, jsonify, request, url_for, abort, g


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

import json

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()



engine = create_engine('sqlite:///users.db')


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)


app = Flask(__name__)
redis = Redis()



@auth.verify_password
def verify_password(username, password):
    user = session.query(User).filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

class RateLimit(object):
    expiration_window = 10


    def __init__(self, key_prefix, limit, per, send_x_headers):
        self.reset = (int(time.time()) // per) * per + per
        self.key = key_prefix + str(self.reset)
        self.limit = limit
        self.per = per
        self.send_x_headers = send_x_headers
        p = redis.pipeline()
        p.incr(self.key)
        p.expireat(self.key, self.reset + self.expiration_window)
        self.current = min(p.execute()[0], limit)


    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)


def get_view_rate_limit():
    return getattr(g, '_view_rate_limit', None)


def on_over_limit(limit):
    send_simple_message()
    notify_pagerduty()
    return (jsonify({'data':'You hit the rate limit','error':'429'}),429)

def ratelimit(limit, per=300, send_x_headers=True, over_limit=on_over_limit, scope_func=lambda: request.remote_addr, key_func=lambda: request.endpoint):
    def decorator(f):
        def rate_limited(*args, **kwargs):
            key = 'rate-limit/%s/%s/' % (key_func(), scope_func())
            rlimit = RateLimit(key, limit, per, send_x_headers)
            g._view_rate_limit = rlimit
            if over_limit is not None and rlimit.over_limit:
                return over_limit(rlimit)
            return f(*args, **kwargs)
        return update_wrapper(rate_limited, f)
    return decorator

def decorator(f):
    def rate_limited(*args, **kwargs):
        over_limit = on_over_limit
        key = ''+g.user.username
        if(g.user.id%2):
            rlimit = RateLimit(key, 5, 300, True)
        else:
            rlimit = RateLimit(key, 10, 300, True)
        g._view_rate_limit = rlimit
        if over_limit is not None and rlimit.over_limit:
            return over_limit(rlimit)
        return f(*args, **kwargs)
    return update_wrapper(rate_limited, f)


@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@app.route('/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        print "missing arguments"
        abort(400) 
        
    if session.query(User).filter_by(username = username).first() is not None:
        print "existing user"
        user = session.query(User).filter_by(username=username).first()
        return jsonify({'message':'user already exists'}), 200
        
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201


@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


#Rate Limited on basis of IP Address.
@app.route('/api/resource')
@ratelimit(10)
@auth.login_required
def get_resource():
    return jsonify({ 'data': 'Hello, %s!' % g.user.username })

#Rate Limited on basis of Logged in user.
@app.route('/home')
@auth.login_required
@decorator
def getPlayers():
    return jsonify({'message':'You are visiting rate limiting content %s' %g.user.username})

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)



#To access '/home' with valid credentials.
#curl -u Rishabh:Rishabh -i -X Get http://localhost:5000/home
 
#To register a user with username as "Rishabh" and password as "Rishabh"
#curl -i -X POST -H "Content-Type: application/json" -d '{"username":"Rishabh","password":"Rishabh"}' http://localhost:5000/users

