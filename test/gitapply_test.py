import unittest
import subprocess
import os
import shutil
import sys

from gitapply.client import git_status, GitFileModeModify, GitFileModeNew, read_file
from gitapply import git, server

TEST_GIT_PROJECT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '__test_git_path')
TEST_GIT_PROJECT_SERVER_PATH = TEST_GIT_PROJECT_PATH + '_server'


def init_test_git_project():
    if not os.path.isdir(TEST_GIT_PROJECT_PATH):
        os.mkdir(TEST_GIT_PROJECT_PATH)
    
    return subprocess.run(['git', 'init'], cwd=TEST_GIT_PROJECT_PATH).returncode is 0


def clean_test_git_project():
    if os.path.isdir(TEST_GIT_PROJECT_PATH):
        shutil.rmtree(TEST_GIT_PROJECT_PATH)


def make_git_commit():
    files = ['ab', 'abb', 'abc', 'abd']

    for f in files:
        with open(os.path.join(TEST_GIT_PROJECT_PATH, f), 'wt') as test_file:
            test_file.write('file %s content' % f)

    stash_process = subprocess.run(['git', 'add', 'ab', 'abb'], cwd=TEST_GIT_PROJECT_PATH)
    if stash_process.returncode is not 0:
        raise Exception('stash files failed')
    subprocess.run(['git', 'commit', '-m', 'add two files'], cwd=TEST_GIT_PROJECT_PATH)

    basepath = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(basepath, 'py.png'), os.path.join(TEST_GIT_PROJECT_PATH, 'py.png'))

    subprocess.run(['git', 'add', 'py.png'], cwd=TEST_GIT_PROJECT_PATH)
    subprocess.run(['git', 'commit', '-m', 'add py.png'], cwd=TEST_GIT_PROJECT_PATH)

    shutil.copy(os.path.join(basepath, 'py2.png'), os.path.join(TEST_GIT_PROJECT_PATH, 'py.png'))


def change_ab():
    with open(os.path.join(TEST_GIT_PROJECT_PATH, 'ab'), 'wt') as ab:
        ab.write('changed ab content')


def create_ac():
    with open(os.path.join(TEST_GIT_PROJECT_PATH, 'ac'), 'wt') as ac:
        ac.write('file ac content')


def make_copy():
    if os.path.isdir(TEST_GIT_PROJECT_SERVER_PATH):
        shutil.rmtree(TEST_GIT_PROJECT_SERVER_PATH)
    
    shutil.copytree(TEST_GIT_PROJECT_PATH, TEST_GIT_PROJECT_SERVER_PATH)


def clean_server_git_project():
    if os.path.isdir(TEST_GIT_PROJECT_SERVER_PATH):
        shutil.rmtree(TEST_GIT_PROJECT_SERVER_PATH)


class ClientTest(unittest.TestCase):
    def setUp(self):
        if not init_test_git_project():
            raise Exception('init test project "%s" filed' % TEST_GIT_PROJECT_PATH)

        make_git_commit()
        make_copy()
        change_ab()
        create_ac()

    def tearDown(self):
        clean_test_git_project()
        clean_server_git_project()
        pass

    def test_client(self):
        print('git status test')
        file_exists = False
        for f in git_status(cwd=TEST_GIT_PROJECT_PATH):
            if f.file == 'ab':
                self.assertIsInstance(f.mode, GitFileModeModify)
                file_exists = True
            elif f.file == 'abc':
                self.assertIsInstance(f.mode, GitFileModeNew)
                file_exists = True
            elif f.file == 'abd':
                self.assertIsInstance(f.mode, GitFileModeNew)
                file_exists = True
            elif f.file == 'ac':
                self.assertIsInstance(f.mode, GitFileModeNew)
                file_exists = True
            else:
                file_exists = False

        self.assertTrue(file_exists, 'ab, abc, abd, ac should exists')
        diff = git.diff(cwd=TEST_GIT_PROJECT_PATH)
        self.assertIn('-file ab content', diff)
        self.assertIn('+changed ab content', diff)

    def _copy_new_file_to_server(self, client_file):
        server.new_file(client_file, read_file(client_file, cwd=TEST_GIT_PROJECT_PATH), cwd=TEST_GIT_PROJECT_SERVER_PATH)
        self.assertTrue(os.path.isfile(os.path.join(TEST_GIT_PROJECT_SERVER_PATH, client_file)), 'file "%s" should exist in server' % client_file)

    def test_server_apply(self):
        print('git server apply')
        server.apply_change(git.diff('--binary', cwd=TEST_GIT_PROJECT_PATH), cwd=TEST_GIT_PROJECT_SERVER_PATH)
        diff = git.diff('--binary', cwd=TEST_GIT_PROJECT_SERVER_PATH)
        self.assertIn('-file ab content', diff)
        self.assertIn('+changed ab content', diff)

        self._copy_new_file_to_server('abc')
        self._copy_new_file_to_server('abd')
        self._copy_new_file_to_server('ac')

        md5_command = 'md5sum'
        if sys.platform == 'darwin':
            md5_command = 'md5'

        py1md5 = subprocess.run([md5_command, os.path.join(TEST_GIT_PROJECT_PATH, 'py.png')], stdout=subprocess.PIPE).stdout.decode('utf8')
        py2md5 = subprocess.run([md5_command, os.path.join(TEST_GIT_PROJECT_SERVER_PATH, 'py.png')], stdout=subprocess.PIPE).stdout.decode('utf8')

        self.assertEqual(py1md5.split(' ')[0], py2md5.split(' ')[0])


if __name__ == "__main__":
    unittest.main()
