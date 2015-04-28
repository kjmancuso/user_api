# -*- coding: utf-8 -*-
import flask
# Probably should have used flask-restful for this

from functools import wraps

app = flask.Flask(__name__)

USERS = {}
# Question: Should I have cared about empty groups created by other methods and
# then emptied?
GROUPS = {}


# Decorators
# TODO add more decorators for increasing code reuse for user exists/not found
def validate_user_form(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        form = flask.request.get_json()
        if not form:
            return 'No JSON request body sent.\n', 400
        if not all(x in form.keys() for x in ['first_name', 'last_name',
                                              'userid', 'groups']):
            return 'Malformed user entity\n', 400
        if not isinstance(form['groups'], list):
            return 'Group not dict\n', 400
        return func(*args, **kwargs)
    return decorated_view


# Helper funcs
def get_user(userid):
    if userid not in USERS:
        return None
    membership = []
    for g in GROUPS:
        if userid in GROUPS[g]:
            membership.append(g)
    user = USERS[userid]
    user['groups'] = membership

    return user


def create_user(fname, lname, uid, groups):
    app.logger.debug('Created user %s' % uid)
    USERS[uid] = {'first_name': fname, 'last_name': lname, 'userid': uid}
    for g in groups:
        if g not in GROUPS:
            app.logger.debug('Created group %s' % g)
            GROUPS[g] = []
        app.logger.debug('Adding user %s to group %s' % (uid, g))
        GROUPS[g].append(uid)

    return True


def delete_user(uid):
    app.logger.debug('Deleted user %s' % uid)
    USERS.pop(uid)
    for g in GROUPS:
        if uid in GROUPS[g]:
            app.logger.debug('Removed user %s from group %s' % (uid, g))
            GROUPS[g].remove(uid)

    return True


def broke_jsonify(r):
    tmp = flask.json.dumps(r)
    resp = flask.Response(tmp)
    resp.headers['Content-Type'] = 'application/json'

    return resp


# Routes!
@app.route('/')
def index():
    return 'Well, hello there.\n'


@app.route('/users/<userid>', methods=['GET'])
def users_get(userid):
        user = get_user(userid)
        if not user:
            return 'User not found.\n', 404

        return flask.jsonify(USERS[userid])


@app.route('/users/<userid>', methods=['DELETE'])
def users_delete(userid):
    user = get_user(userid)
    if not user:
        return 'User not found\n', 404
    delete_user(userid)
    return 'User %s has been deleted\n' % userid


@app.route('/users/<userid>', methods=['PUT'])
@validate_user_form
def users_put(userid):
    if userid not in USERS:
        return 'User not found\n', 404
    delete_user(userid)
    form = flask.request.get_json()
    fname = form['first_name']
    lname = form['last_name']
    uid = form['userid']
    groups = form['groups']
    # The most literal implementation of PUT, even allowing for changing
    # usernames, feels weird. The brain makes valid argument for it, though.
    create_user(fname, lname, uid, groups)
    user = get_user(uid)

    return flask.jsonify(user)


@app.route('/users', methods=['POST'])
@validate_user_form
def users_post():
    form = flask.request.get_json()
    if form['userid'] in USERS:
        return 'User already exists!\n', 400
    # lazy way, suspect additional data which could possibly break contract
    # users[form['userid']] = form
    fname = form['first_name']
    lname = form['last_name']
    uid = form['userid']
    groups = form['groups']
    create_user(fname, lname, uid, groups)

    user = get_user(uid)

    return flask.jsonify(user)


@app.route('/groups/<group>', methods=['GET'])
def groups_get(group):
    if group not in GROUPS:
        return 'Group not found.\n', 404

    # TIL: http://flask.pocoo.org/docs/0.10/security/#json-security
    # Well played.

    members = GROUPS[group]

    resp = broke_jsonify(members)

    return resp


@app.route('/groups', methods=['POST'])
def groups_post():
    form = flask.request.get_json()
    if not form:
        return 'No JSON request body sent.\n', 400
    if not form['name']:
        return 'No name parameter sent.\n', 400

    name = form['name']
    if name in GROUPS:
        return 'Group %s already exists' % name, 400

    app.logger.debug('Created group %s' % name)
    GROUPS[name] = []

    return flask.jsonify({'name': name})


@app.route('/groups/<group>', methods=['PUT'])
def groups_put(group):
    form = flask.request.get_json()
    if not isinstance(form, list):
        return 'Request body not a list.\n', 400
    if group not in GROUPS:
        return 'Group not found.\n', 400

    app.logger.debug('Replaced user data for group %s' % group)
    GROUPS[group] = form

    return broke_jsonify(GROUPS[group])


@app.route('/groups/<group>', methods=['DELETE'])
def groups_delete(group):
    if group not in GROUPS:
        return 'Group not found.\n', 404
    app.logger.debug('Deleted group %s' % group)
    GROUPS.pop(group)
    return 'Group %s has been deleted\n' % group


if __name__ == '__main__':
    app.run(debug=False, port=5101)
