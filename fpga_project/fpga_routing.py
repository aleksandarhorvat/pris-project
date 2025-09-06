import matplotlib.pyplot as plt
from .fpga_matrix import FPGAMatrix
from .models import RRG

class FPGARouting(FPGAMatrix):
    def __init__(self):
        super().__init__()

    def visualize_routing(self, rrg: RRG, route):
        self.visualize_fpga_matrix(rrg)

        for net_id, net in route.nets.items():
            nodes_list = net.nodes
            if not nodes_list:
                continue

            x_coords = []
            y_coords = []

            drawn_edges = set()

            for i in range(len(nodes_list) - 1):
                src = nodes_list[i]
                dst = nodes_list[i + 1]

                # ako je source == SINK, ne crtamo edge ali nastavljamo dalje
                if src.type == "SINK":
                    continue

                x_src = (src.xlow + src.xhigh) / 2
                y_src = (src.ylow + src.yhigh) / 2
                x_dst = (dst.xlow + dst.xhigh) / 2
                y_dst = (dst.ylow + dst.yhigh) / 2

                edge_key = (src.id, dst.id)
                if edge_key not in drawn_edges:
                    self.ax.plot([x_src, x_dst], [y_src, y_dst],
                                 'k-', linewidth=2, alpha=0.8)
                    drawn_edges.add(edge_key)

            for node in nodes_list:
                x_center = (node.xlow + node.xhigh) / 2
                y_center = (node.ylow + node.yhigh) / 2
                x_coords.append(x_center)
                y_coords.append(y_center)

            # ruta i cvorovi
            self.ax.plot(x_coords, y_coords, 'ro', markersize=7, alpha=0.7)

            # belezimo samo pocetni i krajnji cvor rute
            if len(x_coords) >= 2:
                # pocetni
                self.ax.text(x_coords[0], y_coords[0] - 0.3, f'S{net_id}',
                             ha='center', va='center', fontsize=7,
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue"))
                # krajnji
                self.ax.text(x_coords[-1], y_coords[-1] - 0.3, f'E{net_id}',
                             ha='center', va='center', fontsize=7,
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen"))

    # prikazivanje jednog signala ciji id je prosledjen
    def visualize_signal(self, route, net_id: int):
        # dodajemo podnaslov
        subtitle = f"Prikaz signala sa ID = {net_id}"
        self.ax.text(0.5, 1.0, subtitle, transform=self.ax.transAxes,
                     ha='center', va='bottom', fontsize=12, style='italic', color='gray')

        net = route.nets[net_id]

        x_coords, y_coords = [], []
        nodes_list = net.nodes

        drawn_edges = set()

        for i in range(len(nodes_list) - 1):
            src = nodes_list[i]
            dst = nodes_list[i + 1]

            # ako je source == SINK, ne crtamo edge ali nastavljamo dalje
            if src.type == "SINK":
                continue

            x_src = (src.xlow + src.xhigh) / 2
            y_src = (src.ylow + src.yhigh) / 2
            x_dst = (dst.xlow + dst.xhigh) / 2
            y_dst = (dst.ylow + dst.yhigh) / 2

            edge_key = (src.id, dst.id)
            if edge_key not in drawn_edges:
                self.ax.plot([x_src, x_dst], [y_src, y_dst],
                             'k-', linewidth=2, alpha=0.8)
                drawn_edges.add(edge_key)

        # uzimamo koordinate
        for node in nodes_list:
            x_center = (node.xlow + node.xhigh) / 2
            y_center = (node.ylow + node.yhigh) / 2
            x_coords.append(x_center)
            y_coords.append(y_center)

        self.ax.plot(x_coords, y_coords, 'ro', markersize=7, alpha=0.8)

        # obelezimo cvorove
        for i, node in enumerate(nodes_list):
            if node.type == 'SOURCE':
                # pocetni cvor
                self.ax.text(x_coords[i], y_coords[i] - 0.3, f"S-{net_id}",
                             ha="center", va="center", fontsize=8,
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue"))
            elif node.type == 'SINK':
                # krajni cvor
                self.ax.text(x_coords[i], y_coords[i] - 0.3, f"E-{net_id}",
                             ha="center", va="center", fontsize=8,
                             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen"))

    def visualize_signals_by_branching(self, route, branching_factor: int):
        # dodajemo podnaslov
        subtitle = f"Signali sa faktorom grananja = {branching_factor}"
        self.ax.text(0.5, 1.0, subtitle, transform=self.ax.transAxes,
                     ha='center', va='bottom', fontsize=12, style='italic', color='gray')

        # pratimo koje pozicije su zauzete
        labeled_positions = {}

        for net_id, net in route.nets.items():
            # prebrojimo koliko ima sink cvorova
            num_sinks = sum(1 for node in net.nodes
                            if node.type == 'SINK')
            if num_sinks != branching_factor:
                continue  # preskocimo netove koji ne odgovaraju

            x_coords, y_coords = [], []
            nodes_list = net.nodes

            drawn_edges = set()

            for i in range(len(nodes_list) - 1):
                src = nodes_list[i]
                dst = nodes_list[i + 1]

                # ako je source == SINK, ne crtamo edge ali nastavljamo dalje
                if src.type == "SINK":
                    continue

                x_src = (src.xlow + src.xhigh) / 2
                y_src = (src.ylow + src.yhigh) / 2
                x_dst = (dst.xlow + dst.xhigh) / 2
                y_dst = (dst.ylow + dst.yhigh) / 2

                edge_key = (src.id, dst.id)
                if edge_key not in drawn_edges:
                    self.ax.plot([x_src, x_dst], [y_src, y_dst],
                                 'k-', linewidth=2, alpha=0.8)
                    drawn_edges.add(edge_key)

            for node in nodes_list:
                x_center = (node.xlow + node.xhigh) / 2
                y_center = (node.ylow + node.yhigh) / 2
                x_coords.append(x_center)
                y_coords.append(y_center)

            self.ax.plot(x_coords, y_coords, 'ro', markersize=7, alpha=0.8)

            #
            for i, node in enumerate(nodes_list):
                if node.type in ['SOURCE', 'SINK']:
                    x_pos = x_coords[i]
                    y_pos = y_coords[i]
                    position_key = (x_pos, y_pos)

                    # proverimo da li je pozicija vec koriscena
                    if position_key in labeled_positions:
                        # ako jeste, pomerimo na dole malo da ne dodje do preklapanja
                        offset = labeled_positions[position_key] * -0.25
                        labeled_positions[position_key] += 1
                    else:
                        # ako nije samo postavimo
                        offset = 0
                        labeled_positions[position_key] = 1

                    label_text = f"S-{net_id}" if node.type == 'SOURCE' else f"E-{net_id}"
                    facecolor = "lightblue" if node.type == 'SOURCE' else "lightgreen"

                    self.ax.text(x_pos, y_pos + offset - 0.3, label_text,
                                 ha="center", va="center", fontsize=8,
                                 bbox=dict(boxstyle="round,pad=0.2", facecolor=facecolor))