import subprocess


class CommandNonZeroReturnCodeException(Exception):
    def __init__(self, returncode, stderr):
        super().__init__("Non zero return code: %d, %s" % (returncode, stderr))
        self.returncode = returncode


def _execute(*command, cwd=None):
    cmd = subprocess.Popen(['git', *command], stdout=subprocess.PIPE, cwd=cwd, stderr=subprocess.PIPE)
    stdout, stderr = cmd.communicate()

    if cmd.returncode != 0:
        raise CommandNonZeroReturnCodeException(cmd.returncode, stderr.decode('utf8').split('\n')[0])

    return stdout.decode('utf8')


def status(*params, cwd=None):
    return _execute('status', *params, cwd=cwd)


def checkout(*params, cwd=None):
    return _execute('checkout', *params, cwd=cwd)


def diff(*params, cwd=None):
    return _execute('diff', *params, cwd=cwd)


def apply(patch, cwd=None):
    return _execute('apply', patch, cwd=cwd)
