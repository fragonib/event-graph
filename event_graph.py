import argparse
import collections
import json
import os
import re
import sys
import yaml
from os.path import basename
from pathlib import Path
from blessings import Terminal


term = Terminal()

Node = collections.namedtuple('Node', 'subject event')
Transition = collections.namedtuple('Transition', 'source event target')


def parse_options(args):
    parser = argparse.ArgumentParser(description="Script to generate event graph of HS modular")
    parser.add_argument('-f', '--folder', help="An optional argument")
    parser.add_argument('-m', '--marker', help="Marker file subfolder to be considered a module root")
    options = parser.parse_args(args)
    return options.folder, options.marker


def readfile(filename):
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()
    return filetext


def find_projects(root_dir, marker_file):
    for dirName, subdirList, fileList in os.walk(root_dir):
        if marker_file in fileList:
            del subdirList[:]  # Once found marker file don't go on depth on FS
            yield dirName


def find_event_subscriptions(module_dir):
    target = module_name(module_dir)
    for filename in Path(module_dir).rglob('*.kt'):
        filetext = readfile(filename)
        for event in extract_event_subscriptions(filetext):
            yield Node(subject=target, event=event)


def module_name(module_dir):
    return basename(module_dir).upper()


def extract_event_subscriptions(filetext):
    subscribe_regex = r'eventsEngine\s*?\.subscribe\(.*?\)\s*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(subscribe_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_event_publications(module_dir):
    origin = module_name(module_dir)
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


def found_nodes_and_edges(root_dir, marker_file):

    # Find project dirs
    print(term.blue('Found projects:'))
    for project_dir in find_projects(root_dir, marker_file):
        print('  ' + module_name(project_dir))
    print()

    # Find event subscribers
    print(term.blue('Event subscribers:'))
    for project_dir in find_projects(root_dir, marker_file):
        print(term.green(module_name(project_dir)))
        subscriptions = find_event_subscriptions(project_dir)
        for node in subscriptions:
            print(f'  - {node.event}')
        print()

    # Find event publishers
    print(term.blue('Event publishers:'))
    for project_dir in find_projects(root_dir, marker_file):
        print(term.green(module_name(project_dir)))
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


def generate_event_graph(root_dir, marker_file):

    receivers = {}
    for project_dir in find_projects(root_dir, marker_file):
        for (receiver, event) in find_event_subscriptions(project_dir):
            receivers.setdefault(event, []).append(receiver)

    emitters = []
    for project_dir in find_projects(root_dir, marker_file):
        for node in find_event_publications(project_dir):
            emitters.append(node)
    for node in find_ui_publications(root_dir):
        emitters.append(node)

    transitions = []
    for (source, event) in emitters:
        try:
            for target in receivers[event]:
                transitions.append(Transition(source=source, event=event, target=target))
        except KeyError as e:
            print(f'There is no receiver of {event}')

    return transitions


def graphviz_exporter(transitions):
    print(term.blue('Graphviz:'))
    print('digraph {')
    for source, transition, target in transitions:
        print(f'   {source} -> {target}[label="{transition}"]')
    print('}')
    print()


def json_exporter(graph):
    print(term.blue('Json graph:'))
    edges = [trans._asdict() for trans in graph]
    print(json.dumps(edges, indent=2))
    print()


if __name__ == '__main__':
    root_dir, marker_file = parse_options(sys.argv[1:])
    graph = generate_event_graph(root_dir, marker_file)
    graphviz_exporter(graph)
    json_exporter(graph)


