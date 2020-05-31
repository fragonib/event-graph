import argparse
import json
import os
import re
import sys
from collections import defaultdict

import yaml
from os.path import basename
from pathlib import Path

from event_graph import EventTravel, Transition, Graph, EventExchanges


def parse_options(args):
    parser = argparse.ArgumentParser(description="Script to generate event graph of vertx coded domains")
    parser.add_argument('-f', '--folder', help="An optional argument", required=True)
    parser.add_argument('-m', '--marker', help="Marker file subfolder to be considered a module root", required=True)
    options = parser.parse_args(args)
    return options.folder, options.marker


def readfile(filename):
    text_file = open(filename, 'r')
    filetext = text_file.read()
    text_file.close()
    return filetext


def find_domains(root_dir, marker_file):
    domains_path = os.path.join(root_dir, 'domains')
    for dirName, subdirList, fileList in os.walk(domains_path):
        if marker_file in fileList:
            del subdirList[:]  # Once found marker file don't go on depth on FS
            yield dirName


def module_domain_name(module_dir):
    return basename(module_dir).upper()


def find_event_subscriptions(module_dir):
    domain_name = module_domain_name(module_dir)
    for filename in Path(module_dir).rglob('*.kt'):
        filetext = readfile(filename)
        for event_name in extract_event_subscriptions(filetext):
            yield EventTravel(subject=domain_name, event=event_name)


def extract_event_subscriptions(filetext):
    subscribe_regex = r'eventsEngine\s*?\.subscribe\(.*?\)\s*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(subscribe_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_event_publications(module_dir):
    domain_name = module_domain_name(module_dir)
    for filename in Path(module_dir).rglob('*.kt'):
        filetext = readfile(filename)
        for event_name in extract_event_publications(filetext):
            yield EventTravel(subject=domain_name, event=event_name)


def extract_event_publications(filetext):
    publish_regex = r'eventsEngine\s*?\.publish.*?\.to\(EventType\.(\w+)\)'
    for m in re.finditer(publish_regex, filetext, flags=re.DOTALL):
        yield m.group(1)


def find_ui_publications(root_dir):
    resources_dir = 'edge/api-gateway/src/main/resources'
    apidoc_file = os.path.join(root_dir, resources_dir, "apidoc.yml")
    with open(apidoc_file, 'r') as stream:
        apidoc = yaml.safe_load(stream)
        for path, ops in apidoc['paths'].items():
            for op, data in ops.items():
                yield EventTravel(subject='UI', event=data['operationId'])


def event_exchanges(marker_file, root_dir):

    exchanges = EventExchanges(emitters=[], receivers=[])

    # Domain emitters
    for project_dir in find_domains(root_dir, marker_file):
        for travel in find_event_publications(project_dir):
            exchanges.emitters.append(travel)

    # UI emitters
    for travel in find_ui_publications(root_dir):
        exchanges.emitters.append(travel)

    # Domain receivers
    for project_dir in find_domains(root_dir, marker_file):
        for travel in find_event_subscriptions(project_dir):
            exchanges.receivers.append(travel)

    return exchanges


def generate_event_graph(root_dir, marker_file):

    exchanges = event_exchanges(marker_file, root_dir)

    indexed_receivers = defaultdict(list)
    for receiver in exchanges.receivers:
        indexed_receivers[receiver.event].append(receiver.subject)

    transitions = []
    for subject, event in exchanges.emitters:
        if not event in indexed_receivers:
            print(f'There is no receiver of event [{event}]')
            transitions.append(Transition(source_node=subject, edge=event, target_node='DEV_NULL'))
        for target in indexed_receivers[event]:
            transitions.append(Transition(source_node=subject, edge=event, target_node=target))

    return Graph(transitions=transitions)


def graphviz_exporter(graph):
    with open('events-graph.dot', 'w') as dot_file:
        dot_file.write('digraph {\n')
        for source_node, edge, target_node in graph.transitions:
            dot_file.write(f'   {source_node} -> {target_node}[label="{edge}"]\n')
        dot_file.write('}\n')


def custom_json_exporter(graph):
    with open('events-graph.json', 'w') as json_file:
        edges = [transition._asdict() for transition in graph.transitions]
        json_file.write(json.dumps(edges, indent=2))


# Analyse, generate and export event graph
if __name__ == '__main__':
    root_dir, marker_file = parse_options(sys.argv[1:])
    root_dir_expanded = os.path.expanduser(root_dir)
    graph = generate_event_graph(root_dir_expanded, marker_file)
    graphviz_exporter(graph)
    custom_json_exporter(graph)


