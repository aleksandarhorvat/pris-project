from typing import Dict, List


class Node:
    def __init__(self, node_id, node_type, ptc, xhigh, xlow, yhigh, ylow):
        self.id = node_id
        # IPIN, sto oznacava ulazni pin (u arhitekturama koje cemo mi koristiti, ulazni pin klastera ili IO bloka),
        # OPIN, sto oznacava izlazni pin (u arhitekturama koje cemo mi koristiti, izlazni pin klastera ili IO bloka),
        # CHANX, sto oznacava horizontalnu prefabrikovanu zicu,
        # CHANY, sto oznacava vertikalnu prefabrikovanu zicu,
        # SOURCE, sto je virtuelni cvor koji predstavlja pocetak signala koji moze koristiti vise ekvivalentnih OPIN cvorova,
        # SINK, sto je virtuelni cvor koji predstavlja kraj signala koji moze koristiti vise ekvivalentnih IPIN cvorova
        self.type = node_type
        # oznacava redni broj pina, odnosno zice u kanalu
        self.ptc = ptc
        # xhigh, xlow, yhigh i ylow odredjuju koordinate koje dati cvor zauzima u 2D FPGA matrici. xhigh = xlow i yhigh = ylow.
        self.xhigh = xhigh
        self.xlow = xlow
        self.yhigh = yhigh
        self.ylow = ylow

    def __str__(self):
        return (f"Node(id={self.id}, type={self.type}, ptc={self.ptc}, "
                f"xhigh={self.xhigh}, xlow={self.xlow}, "
                f"yhigh={self.yhigh}, ylow={self.ylow})")


class Edge:
    def __init__(self, sink, src):
        # id uvorisnog cvora
        self.sink = sink
        # id izvorisnog cvora
        self.src = src

    def __str__(self):
        return f"Edge(sink={self.sink}, src={self.src})"


class RRG:
    def __init__(self):
        self.nodes: Dict[int, Node] = {}
        self.edges: List[Edge] = []

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)

    def __str__(self):
        result = ["RRG:"]
        result.append("Nodes:")
        for node_id, node in self.nodes.items():
            result.append(f"  Node {node_id}: {node}")
        result.append("Edges:")
        for edge in self.edges:
            result.append(f"  Edge: {edge}")
        return "\n".join(result)


class Net:
    def __init__(self, net_id):
        #id signala
        self.id = net_id
        self.nodes: Dict[int, Node] = {}

    def __str__(self):
        result = [f"Net {self.id}:"]
        for node_id, node in self.nodes.items():
            result.append(f"  {node}")
        return "\n".join(result)


class Route:
    def __init__(self):
        # redni broj signala u route : signal
        self.nets: Dict[int, Net] = {}

    def __str__(self):
        result = ["Route:"]
        for net_serial_numb, net in self.nets.items():
            result.append(f"Net {net_serial_numb} {net.id}:")
            net_lines = str(net).splitlines()
            for line in net_lines:
                if line.startswith(f"Net {net.id}:"):
                    continue
                result.append(f"    {line}")
        return "\n".join(result)
