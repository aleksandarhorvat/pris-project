import xml.etree.ElementTree as ET
from .models import *


class RRGParser:
    def __init__(self):
        self.rrg = RRG()

    def parse(self, route_file: str):
        tree = ET.parse(route_file)
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
            self.rrg.add_node(
                Node(node_id, ntype, ptc, xhigh, xlow, yhigh, ylow))

        for edge in root.findall("rr_edges/edge"):
            sink = int(edge.get("sink_node"))
            src = int(edge.get("src_node"))
            self.rrg.add_edge(Edge(sink, src))

    def get_rrg(self) -> RRG:
        return self.rrg
