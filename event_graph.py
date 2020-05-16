import collections
import getopt
import os
import re
import sys
import yaml
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
    for dirName, subdirList, fileList in os.walk(root_dir):
        if marker_file in fileList:
            del subdirList[:]  # Don't go on depth
            yield dirName


def find_event_subscriptions(module_dir):
    target = basename(module_dir)
    for filename in Path(module_dir).rglob('*Handler.kt'):
        filetext = readfile(filename)
        for event in extract_event_subscriptions(filetext):
            yield Node(subject=target, event=event)


def extract_event_subscriptions(filetext):
    subscribe_regex = r'eventsEngine\s*?\.subscribe.*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(subscribe_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_event_publications(module_dir):
    origin = basename(module_dir)
    for filename in Path(module_dir).rglob('*.kt'):
        filetext = readfile(filename)
        for event in extract_event_publications(filetext):
            yield Node(subject=origin, event=event)


def extract_event_publications(filetext):
    publish_regex = r'eventsEngine\s*?\.publish.*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(publish_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_ui_publications(root_dir):
    resources_dir = '../edge/api-gateway/src/main/resources'
    with open(os.path.join(root_dir, resources_dir, "apidoc.yml"), 'r') as stream:
        doc = yaml.safe_load(stream)
        for path, ops in doc['paths'].items():
            for op, data in ops.items():
                yield Node(subject='UI', event=data['operationId'])


if __name__ == '__main__':

    # Parse CLI options
    root_dir, marker_file = parse_options(sys.argv[1:])
    print(term.blue('Options:'))
    print(term.green('  Root folder: ') + root_dir)
    print(term.green('  Marker file: ') + marker_file)
    print()

    # Find project dirs
    print(term.blue('Found projects:'))
    for project_dir in find_projects(root_dir, marker_file):
        print('  ' + basename(project_dir))
    print()

    # Find event subscribers
    print(term.blue('Event subscribers:'))
    for project_dir in find_projects(root_dir, marker_file):
        print(term.green(basename(project_dir)))
        subscriptions = find_event_subscriptions(project_dir)
        for node in subscriptions:
            print(f'  - {node.event}')
        print()

    # Find event publishers
    print(term.blue('Event publishers:'))
    for project_dir in find_projects(root_dir, marker_file):
        print(term.green(basename(project_dir)))
        publications = find_event_publications(project_dir)
        for node in publications:
            print(f'  - {node.event}')
        print()

    # Find UI events
    print(term.blue('UI events:'))
    publications = find_ui_publications(root_dir)
    for node in publications:
        print(f'  - {node.event}')
    print()


