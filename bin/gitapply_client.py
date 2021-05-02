#!/usr/bin/env python3

import requests
import json
import os
import base64
import sys
import argparse

from gitapply import client
from gitapply import git


def do_request(url, payload, authorization=None):
    headers = {'content-type': 'application/json'}
    if authorization:
        headers['authorization'] = 'Basic ' + authorization

    res = requests.post(url, headers=headers, data=json.dumps(payload))
    res.close()

    return json.loads(res.content)


def main(endpoint, local_repository, server_repository, user=None, password=None):
    changes, news = client.get_project_changes(cwd=local_repository)
    authorization = None
    if user and password:
        authorization = base64.b64encode(('%s:%s' % (user, password)).encode('utf8')).decode('utf8')

    print('Changes')
    for change in changes:
        print('    ', change.file)
    
    if changes:
        apply_res = do_request(
            '%s/api/apply' % endpoint,
            {
                'repository': server_repository,
                'content': git.diff('--binary', cwd=local_repository)
            },
            authorization=authorization
        )

        if apply_res['error']:
            print('apply changes failed', apply_res['msg'])
        else:
            print('change applyed')
    
    if news:
        print('New files')
    else:
        print('No new files add')

    for new_file in news:
        print('    ', 'create file', new_file.file, end=' ')
        with open(os.path.join(local_repository, new_file.file), 'rb') as nf:
            content = nf.read()
            content = base64.b64encode(content)
        new_file_res = do_request(
            '%s/api/new' % endpoint,
            {
                'repository': server_repository,
                'content': content.decode('utf8'),
                'file': new_file.file,
                'encoding': 'base64'
            },
            authorization=authorization,
        )

        if not new_file_res.get('error'):
            print('created')
        else:
            print('failed', new_file_res.get('msg'))
        
    
if __name__ == "__main__":
    prog = argparse.ArgumentParser("git changes sync tool client")
    prog.add_argument('--server', required=True, type=str, help='服务器url')
    prog.add_argument('--repository', type=str, help='本地仓库路径，默认为当前路径', default=os.environ.get('PWD'))
    prog.add_argument('--remote-repository', type=str, required=True, help='服务器仓库名称，不是路径')
    prog.add_argument('--user', type=str, help='username')
    prog.add_argument('--password', type=str, help='password')

    args = prog.parse_args()
    if not args.remote_repository:
        prog.print_help()
        sys.exit(1)

    if not args.repository:
        prog.print_help()
        sys.exit(1)

    if args.user and not args.password:
        print('invalid password for user')
        sys.exit(1)

    if args.password and not args.user:
        print('user name required')
        sys.exit(1)

    main(args.server, args.repository, args.remote_repository, args.user, args.password)

