import getopt
import os
import re
import sys
from os.path import basename
from pathlib import Path

from blessings import Terminal

MVN_DEPENDENCY_TREE_COMMAND = ['mvn', 'dependency:tree']

term = Terminal()


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


def find_event_receivers(root_dir):
    candidates = []
    files = Path(root_dir).rglob('*Handler.kt')
    for path in files:
        event = extract_event_subscription(path)
        if event:
            candidates.append(event)
    return candidates


def extract_event_subscription(filename):

    filetext = readfile(filename)

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
        for event in received:
            print('  - {event}'.format(event=event))
        print()
