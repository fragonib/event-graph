import collections
import json

Graph = collections.namedtuple('Graph', 'transitions')
Transition = collections.namedtuple('Transition', 'source_node edge target_node')


def generate_event_graph(exchanges):

    indexed_receivers = collections.defaultdict(list)
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
