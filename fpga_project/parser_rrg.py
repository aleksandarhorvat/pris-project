import xml.etree.ElementTree as ET
from .models import *

def parse_rrg():
    rrg = RRG()
    tree = ET.parse('b9/rrg.xml')
    root = tree.getroot()

    for node in root.findall("rr_nodes/node"):
        node_id = int(node.get("id"))
        ntype = node.get("type")

        loc = node.find("loc")
        xhigh = int(loc.get("xhigh"))
        xlow = int(loc.get("xlow"))
        yhigh = int(loc.get("yhigh"))
        ylow = int(loc.get("ylow"))
        ptc = int(loc.get("ptc"))
        rrg.add_node(Node(node_id, ntype, ptc, xhigh, xlow, yhigh, ylow))

    for edge in root.findall("rr_edges/edge"):
        src = int(edge.get("src_node"))
        sink = int(edge.get("sink_node"))
        rrg.add_edge(Edge(sink, src))

    return rrg