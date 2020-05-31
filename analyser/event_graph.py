import collections

Graph = collections.namedtuple('Graph', 'transitions')
Transition = collections.namedtuple('Transition', 'source_node edge target_node')

EventExchanges = collections.namedtuple('EventExchanges', 'emitters receivers')
EventTravel = collections.namedtuple('EventTravel', 'subject event')
