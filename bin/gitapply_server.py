import flask
import re
import json
import traceback
import base64
import argparse

from gitapply import server, user

app = flask.Flask('gitapply_server')

api = flask.Blueprint('api', import_name='gitapply_server_api', url_prefix='/api')

repositories = {
    'test': '/tmp/gittest_server'
}

users = None


def get_json_payload():
    if 'application/json' in flask.request.headers.get('content-type', ''):
        try:
            return json.loads(flask.request.data)
        except Exception as e:
            raise Exception('invalid json payload: ' + str(e))
    else:
        raise Exception('invalid content-type: "%s"' % flask.request.headers.get('content-type', ''))

    
def check_payload_field(payload, field, validate=None, msg=None):
    if not payload:
        raise Exception('payload required')

    if type(payload) is not dict:
        raise Exception('payload must is type of dict')

    if not field:
        raise Exception('field required')
    
    if not validate:
        if field not in payload:
            raise Exception('field "%s" not in payload' % field)
    
    if callable(validate):
        if not validate(payload, field):
            raise Exception(msg if msg else 'validate failed')
    
    if isinstance(validate, str) or isinstance(validate, int) or isinstance(validate, bool):
        if payload.get(field) != validate:
            raise Exception(msg if msg else 'payload["%s"] != %s' % (field, validate))
    

def json_response(msg=None, error=False, data=None, status=None, headers=None):
    content = {'error': error}
    if msg:
        error = True
        content['error'] = error
        content['msg'] = msg

        if not status:
            status = 400
    
    if data:
        content['data'] = data
    
    if not status:
        status = 200
        
    return flask.Response(
        json.dumps(content),
        status=status,
        content_type='application/json',
        headers=headers
    )


def check_user(name):
    def wrap1(handler):
        def wrap(*args, **kwargs):
            authorization = flask.request.headers.get('authorization')
            if users:
                headers = {'WWW-Authenticate': 'Basic realm="Authenticate to access"'}
                if not authorization:
                    return json_response(msg='need authorization', status=401, headers=headers)

                auth_type, authorization = re.split(r'\s+', authorization)
                if auth_type != 'Basic':
                    return json_response(msg='invalid auth type', status=401, headers=headers)

                auth = base64.b64decode(authorization).decode('utf8')
                username, password = auth.split(':')
                try:
                    users.check(username, password)
                except user.UserNotFoundException as e:
                    return json_response(msg='user not found', status=401, headers=headers)
                except user.UserPasswordIncorrectException as e:
                    return json_response(msg='incorrect password', status=401, headers=headers)
                except user.UserNotEnabledException as e:
                    return json_response(msg='user not enabled', status=401, headers=headers)
                except Exception as e:
                    return json_response(msg=str(e), status=500)

            return handler(*args, **kwargs)

        setattr(wrap, '__name__', name)
        return wrap

    return wrap1


@api.route('/new', methods=['POST'])
@check_user('new')
def new():
    try:
        payload = get_json_payload()
        check_payload_field(payload, 'repository', lambda p, f: f in p and p[f], msg='repository required')
        check_payload_field(payload, 'file', lambda p, f: f in p and p[f], msg='file required')
        check_payload_field(payload, 'content', lambda p, f: f in p, msg='content required')

        if payload.get('repository') not in repositories:
            raise Exception('Undefined repository: "%s"' % payload.get('repository'))

        if 'encoding' in payload and payload.get('encoding') != 'base64':
            raise Exception('Invalid encoding: "%s"' % payload.get('encoding'))

        if 'encoding' in payload:
            payload['content'] = base64.b64decode(payload['content'].encode('utf8'))
    except Exception as ex:
        return json_response(msg=str(ex), error=True, status=400)

    try:
        repository = repositories[payload.get('repository')]
        server.new_file(payload.get('file'), payload.get('content'), repository)
        return json_response(data='applyed')
    except Exception as ex:
        return json_response(msg=str(ex), error=True)


@api.route('/apply', methods=['POST'])
@check_user('apply')
def apply():
    try:
        payload = get_json_payload()
        check_payload_field(payload, 'repository', lambda p, f: f in p and p[f], msg='repository required')
        check_payload_field(payload, 'content', lambda p, f: f in p and p[f], msg='content required')

        if payload.get('repository') not in repositories:
            raise Exception('Undefined repository: "%s"' % payload.get('repository'))
    except Exception as e:
        return json_response(msg=str(e))

    try:
        repository = repositories[payload.get('repository')]
        server.apply_change(payload.get('content'), cwd=repository)
        return json_response(data='ok')
    except Exception as e:
        traceback.print_exc()
        return json_response(msg=str(e), status=500)


app.register_blueprint(api)


if __name__ == "__main__":
    import os
    prog = argparse.ArgumentParser('git changes sync tool server')
    prog.add_argument('--repository-map', required=True, action='append', help='添加映射，仓库名：仓库路径')
    prog.add_argument('--user-file', required=False, type=str, help='指定用户文件')

    args = prog.parse_args()
    for m in args.repository_map:
        name, repository = m.split(':')
        if not os.path.isdir(os.path.join(repository, '.git')):
            raise Exception('invalid repository map: %s, no such repository' % m)
        repositories[name] = repository

    if args.user_file:
        if not os.path.isfile(args.user_file):
            raise FileNotFoundError('user file not exists')
        users = user.Users.from_file(args.user_file)

    app.run()
