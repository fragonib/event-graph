import collections
import os
import re
import yaml
from os.path import basename
from pathlib import Path


EventExchanges = collections.namedtuple('EventExchanges', 'emitters receivers')
EventTravel = collections.namedtuple('EventTravel', 'subject event')


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


def extract_event_exchanges(marker_file, root_dir):

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
