import argparse
import os
import sys

from event_exchanges import extract_event_exchanges
from event_graph import generate_event_graph, graphviz_exporter, custom_json_exporter


def parse_options(args):
    parser = argparse.ArgumentParser(description="Script to generate event graph of vertx coded domains")
    parser.add_argument('-f', '--folder', help="An optional argument", required=True)
    parser.add_argument('-m', '--marker', help="Marker file subfolder to be considered a module root", required=True)
    options = parser.parse_args(args)
    return os.path.expanduser(options.folder), options.marker


# Analyse, generate and export event graph
if __name__ == '__main__':

    root_dir, marker_file = parse_options(sys.argv[1:])

    exchanges = extract_event_exchanges(marker_file, root_dir)

    graph = generate_event_graph(exchanges)
    graphviz_exporter(graph)
    custom_json_exporter(graph)


