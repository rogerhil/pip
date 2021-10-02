from pip.shell import ShellClient


class Wget(object):

    def __init__(self, shell=None):
        self.shell = shell or ShellClient()

    def download(self, url, location):
        output = self.shell.run('wget -Sq %s -P %s' % (url, location))
        lines = [l for l in output.splitlines() if l and l.startswith('  ')]
        http_status = int(lines.pop(0).split()[1])
        header = dict([[i.strip() for i in l.split(':', 1)]
                       for l in lines if l and l.startswith('  ')])
        if http_status != 200:
            raise Exception('Failed to to download %s. %s' % (url, output))
        return header, output
