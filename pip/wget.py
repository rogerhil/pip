import re

from pip.shell import ShellClient


class Wget(object):

    status_regex = re.compile(r'^\s*\w+/[\w\.]+ (\d+) \w+\s*$')

    def __init__(self, shell=None):
        self.shell = shell or ShellClient()

    def download(self, url, location):
        output = self.shell.run('wget -Sq %s -P %s' % (url, location))
        all_lines = [l for l in output.splitlines() if l and l.startswith('  ')]
        header_blocks = []
        header_lines = []
        for line in all_lines:
            match = self.status_regex.match(line)
            if match:
                http_status = int(match.group(1))
                header_lines = []
                header_blocks.append((http_status, header_lines))
                continue
            header_lines.append(line)

        last_http_status, last_header_lines = header_blocks[-1]
        header = dict([[i.strip() for i in l.split(':', 1)]
                       for l in last_header_lines if l and l.startswith('  ')])
        if last_http_status != 200:
            raise Exception('Failed to to download %s. %s' % (url, output))
        return header, output
