import os
import re

from gitapply import git


class CommandNonZeroReturnCodeException(Exception):
    def __init__(self, returncode):
        super().__init__("Non zero return code: %d" % returncode)
        self.returncode = returncode


def list_all_the_files_in_dir(dir):
    files = []
    if os.path.isdir(dir):
        for next_dir in os.listdir(dir):
            files.extend(list_all_the_files_in_dir(os.path.join(dir, next_dir)))
    else:
        files.append(dir)

    return files


def git_status(cwd=None):
    for line in git.status('--short', '--porcelain', cwd=cwd).split('\n'):
        if line and line.strip():
            status = GitFileStatus(line)
            filepath = os.path.join(cwd, status.file)
            if isinstance(status.mode, GitFileModeNew) and os.path.isdir(filepath):
                for f in list_all_the_files_in_dir(filepath):
                    yield GitFileStatus("A " + f.replace(cwd + '/', ''))
            else:
                yield status


class GitFileMode:
    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __repr__(self):
        return "<%s:%d>" % (self.name, self.code)


class GitFileModeModify(GitFileMode):
    def __init__(self):
        super().__init__(0, "Modify")


class GitFileModeNew(GitFileMode):
    def __init__(self):
        super().__init__(1, 'New')


class GitFileStatus:
    def __init__(self, text):
        self.mode = GitFileModeModify()
        self.file = ''

        self.update_attr_from_text(text)

    def update_attr_from_text(self, text):
        mode, file = re.split(r'\s+', text.lstrip())
        if mode == '??' or mode == 'A':
            self.mode = GitFileModeNew()
        elif mode == 'M':
            self.mode = GitFileModeModify()

        self.file = file

    def __repr__(self):
        return "<gitFileStatus>(file=\"%s\", mode=%s)" % (self.file, repr(self.mode))


def read_file(path, cwd=None):
    if cwd:
        path = os.path.join(cwd, path)

    with open(path, 'rb') as f:
        return f.read()


def get_project_changes(cwd=None):
    changes = []
    news = []

    for f in git_status(cwd):
        if isinstance(f.mode, GitFileModeModify):
            changes.append(f)
        elif isinstance(f.mode, GitFileModeNew):
            news.append(f)

    return changes, news
