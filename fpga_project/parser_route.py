import re
from .models import Node, Net, Route


class RouteParser:
    def __init__(self):
        self.route = Route()

    def parse(self, route_file: str):
        current_net = None

        with open(route_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Pocetak neta: Net 0 (c0)
                if line.startswith("Net"):
                    match = re.match(r"Net\s+(\d+)\s+\((.+)\)", line)
                    if match:
                        net_serial_numb = int(match.group(1))
                        net_id = match.group(2)
                        # kreiraj novi Net i ubaci ga u Route
                        self.route.nets[net_serial_numb] = Net(net_id)
                        current_net = net_serial_numb
                    continue

                # Node linija
                if line.startswith("Node") and current_net is not None:
                    match = re.match(
                        r"Node:\s*(\d+)\s+(\w+)\s+\((\d+),(\d+),\d+\)\s+.*?(\d+)",
                        line
                    )
                    if match:
                        node_id = int(match.group(1))
                        node_type = match.group(2)
                        x = int(match.group(3))
                        y = int(match.group(4))
                        # broj posle koordinata (Pad/Track/Pin/Class)
                        ptc = int(match.group(5))

                        node = Node(
                            node_id=node_id,
                            node_type=node_type,
                            ptc=ptc,
                            xhigh=x, xlow=x,
                            yhigh=y, ylow=y
                        )

                        # dodaj node u trenutni Net
                        self.route.nets[current_net].nodes.append(node)

    def get_route(self) -> Route:
        return self.route
