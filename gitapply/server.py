import os
import subprocess
import hashlib

from gitapply import git


def _mkdir(path):
    if not path:
        return

    path_parts = list(filter(lambda item: item and item.strip(), path.split('/')))
    i = 1

    while i <= len(path_parts):
        dir = "/" + "/".join(path_parts[0:i])
        i += 1

        if not os.path.isdir(dir):
            print('create dir', dir)
            os.mkdir(dir)


def new_file(filename, content, cwd):
    filename = os.path.join(cwd, filename)
    if not os.path.isdir(os.path.join(cwd, '.git')):
        raise Exception('not a git repository')

    _mkdir(os.path.dirname(filename))
    with open(filename, 'wb') as file:
        file.write(content)


def _discard_git_change(cwd=None):
    git.checkout('--', '.', cwd=cwd)
    

def apply_change(content, cwd):
    if not content:
        return

    _discard_git_change(cwd)
    patch = '/tmp/___gitapply_patch_' + hashlib.md5(content.encode('utf8')).hexdigest()[0:5]
    with open(patch, 'w') as patch_file:
        patch_file.write(content)
    
    try:
        print('apply patch: "%s"' % patch)
        git.apply(patch, cwd=cwd)
    finally:
        if os.path.isfile(patch):
            os.unlink(patch)