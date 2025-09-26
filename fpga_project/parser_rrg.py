import xml.etree.ElementTree as ET
from .models import *


class RRGParser:
    def __init__(self):
        self.file = None
        self.rrg = RRG()

    def parse(self, route_file: str):
        self.file = route_file
        tree = ET.parse(self.file)
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

    #dobije id pin-a i vraca sa koje je strane "TOP", "TOP_RIGHT" itd.
    def get_pin_side(self, node_id: int) -> str:
        tree = ET.parse(self.file)
        root = tree.getroot()

        xpath = f"rr_nodes/node[@id='{node_id}']"
        node_elem = root.find(xpath)
        if node_elem is None:
            return None

        if node_elem.get("type") not in ("IPIN", "OPIN"):
            return None

        loc_elem = node_elem.find("loc")
        if loc_elem is not None:
            return loc_elem.get("side")
        return None

    #dobija id zice i vraca sa koje je strane ali mora da bude samo jedna strana "TOP", ne moze da bude "TOP_RIGHT"
    #proverava sa kojim pinovima je povezana i proverava na kojoj strani su ti pinovi
    #dolazi do problema gde su svi pinovi sa kojima je povezana imaju duplu stranu i onda vraca None
    def get_wire_side(self, wire_id: int) -> str:
        # proveri da li cvor postoji i da li je zica
        wire_node = self.rrg.nodes.get(wire_id)
        if not wire_node or wire_node.type not in ("CHANX", "CHANY"):
            return None

        # gledamo sve veze gde se pojavljuje ova zica
        for edge in self.rrg.edges:
            # ako je zica izvor
            if edge.src == wire_id and edge.sink in self.rrg.nodes:
                sink_node = self.rrg.nodes[edge.sink]
                if sink_node.type in ("IPIN", "OPIN"):
                    side = self.get_pin_side(sink_node.id)
                    if side and "_" not in side:  # samo jednoznacan side
                        return side

            # ako je zica odredište
            if edge.sink == wire_id and edge.src in self.rrg.nodes:
                src_node = self.rrg.nodes[edge.src]
                if src_node.type in ("IPIN", "OPIN"):
                    side = self.get_pin_side(src_node.id)
                    if side and "_" not in side:
                        return side

        return None

    def get_rrg(self) -> RRG:
        return self.rrg
