import collections
import getopt
import os
import re
import sys
from os.path import basename
from pathlib import Path
from blessings import Terminal


term = Terminal()

Node = collections.namedtuple('Node', 'subject event')


def parse_options(args):
    root_dir = None
    marker_file = None
    optlist, args = getopt.getopt(args, 'f:m:d:', '["folder=", "marker="]')
    for o, a in optlist:
        if o in ("-f", "--folder"):
            root_dir = a
        if o in ("-m", "--marker"):
            marker_file = a
    return root_dir, marker_file


def find_projects(root_dir, marker_file):
    candidates = []
    for dirName, subdirList, fileList in os.walk(root_dir):
        if marker_file in fileList:
            del subdirList[:]
            candidates.append(dirName)
    return candidates


def find_event_receivers(module_dir):
    candidates = []
    target = basename(module_dir)
    files = Path(module_dir).rglob('*Handler.kt')
    for filename in files:
        filetext = readfile(filename)
        event = extract_event_subscription(filetext)
        if event:
            candidates.append(Node(subject=target, event=event))
    return candidates


def extract_event_subscription(filetext):

    listen_regex = r'init.*?\.to\(EventType\.(\w+)\).*?\}'
    m = re.search(listen_regex, filetext, flags=re.DOTALL)
    if m:
        return m.group(1)
    return None


def readfile(filename):
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()
    return filetext


def find_event_emitters(module_dir):
    candidates = []
    files = Path(module_dir).rglob('*.kt')
    for path in files:
        event = extract_event_subscription(path)
        if event:
            candidates.append(event)
    return candidates


if __name__ == '__main__':

    # Parse CLI options
    root_dir, marker_file = parse_options(sys.argv[1:])
    print(term.blue('Options:'))
    print(term.green('  Root folder: ') + root_dir)
    print(term.green('  Marker file: ') + marker_file)
    print()

    # Find project dirs
    projects_dirs = find_projects(root_dir, marker_file)
    print(term.blue('Found projects:'))
    for project_dir in projects_dirs:
        print('  ' + basename(project_dir))
    print()

    # Check event receivers
    print(term.blue('Event receivers:'))
    for project_dir in projects_dirs:
        print(term.green(basename(project_dir)))
        received = find_event_receivers(project_dir)
        for node in received:
            print(f'  - {node.event}')
        print()
