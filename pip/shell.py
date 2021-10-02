from subprocess import Popen, PIPE


class CommandFailed(Exception):
    """ This exception is raised every time a command execution return a status
    code different than zero.
    """

    def __init__(self, message, output=None, status_code=None, cmd=None):
        super(CommandFailed, self).__init__(message, output, status_code, cmd)
        self.msg = message
        self.output = output
        self.status_code = status_code
        self.cmd = cmd

    def __str__(self):
        error_msg = str(self.msg)
        if self.status_code is not None:
            error_msg = "%s. Status code: %s. Command: %s" % \
                        (error_msg.strip().rstrip('.'),
                         self.status_code, self.cmd)
        if self.msg != self.output:
            return "%s. Error: %s" % (error_msg, self.output)
        return error_msg


class ShellClient(object):

    def run(self, cmd):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        stdout, stderr = p.communicate()
        output = stdout + stderr
        if p.returncode != 0:
            raise CommandFailed('Command failed', output, p.returncode, cmd)
        return output
