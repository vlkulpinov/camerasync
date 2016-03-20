#!/usr/bin/env python

async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
import string
import random
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

app = Flask(__name__, static_folder='Build')
app.config['SECRET_KEY'] = 'AJS2b323jad8bm3yj23bd4y4w'
socketio = SocketIO(app, async_mode=async_mode)


def create_random_name():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))


@app.route('/primary')
def primary():
    return render_template('primary.html', primary_name=create_random_name())

@app.route('/secondary')
def secondary():
    return render_template('secondary.html')


@socketio.on('primary connected', namespace='/test')
def primary_connect(message):
    join_room(message['primary_name'])
    # print 'primary connected', message['primary_name']


@socketio.on('secondary connected', namespace='/test')
def secondary_connect(message):
    join_room(message['primary_name'])
    emit('primary send', {}, room=message['primary_name'])
    # print 'secondary connected', message['primary_name']


@socketio.on('primary change', namespace='/test')
def primary_change(message):
    emit('secondary move', {'data': message['data']}, room=message['primary_name'])
    # print 'change'


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
