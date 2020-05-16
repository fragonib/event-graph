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


def readfile(filename):
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()
    return filetext


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
    for filename in Path(module_dir).rglob('*Handler.kt'):
        filetext = readfile(filename)
        for event in extract_event_subscriptions(filetext):
            candidates.append(Node(subject=target, event=event))
    return candidates


def extract_event_subscriptions(filetext):
    subscribe_regex = r'eventsEngine\s*?\.subscribe.*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(subscribe_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_event_emitters(module_dir):
    candidates = []
    origin = basename(module_dir)
    for filename in Path(module_dir).rglob('*.kt'):
        filetext = readfile(filename)
        for event in extract_event_publications(filetext):
            candidates.append(Node(subject=origin, event=event))
    return candidates


def extract_event_publications(filetext):
    publish_regex = r'eventsEngine\s*?\.publish.*?\.to\(EventType\.(\w+)\)'
    m = re.finditer(publish_regex, filetext, flags=re.DOTALL)
    if m:
        return m.group(1)
    return None


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

    # Find event subscribers
    print(term.blue('Event subscribers:'))
    for project_dir in projects_dirs:
        print(term.green(basename(project_dir)))
        received = find_event_receivers(project_dir)
        for node in received:
            print(f'  - {node.event}')
        print()

    # Find event publishers
    print(term.blue('Event publishers:'))
    for project_dir in projects_dirs:
        print(term.green(basename(project_dir)))
        received = find_event_receivers(project_dir)
        for node in received:
            print(f'  - {node.event}')
        print()