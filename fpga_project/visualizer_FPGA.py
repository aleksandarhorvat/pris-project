import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from .models import RRG


class FPGAVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 12))
        self.colors = {
            'SOURCE': 'crimson',
            'SINK': 'linen',
            'OPIN': 'black',
            'IPIN': 'white',
            'CHANX': 'navy',
            'CHANY': 'brown'
        }

        # Node type opis
        self.node_descriptions = {
            'OPIN': 'Izlazni pin',
            'IPIN': 'Ulazni pin',
            'CHANX': 'Horizontalni kanal',
            'CHANY': 'Vertikalni kanal'
        }

    def visualize_fpga_matrix(self, rrg: RRG):
        self.ax.clear()

        # dimenzije FPGA
        max_x, max_y = self.get_fpga_dimensions(rrg)

        # plotovanje
        self.ax.set_xlim(-1, max_x + 1)
        self.ax.set_ylim(-1, max_y + 1)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Matrični prikaz FPGA arhitekture',
                          fontsize=16, pad=20)
        self.ax.set_xlabel('X koordinata')
        self.ax.set_ylabel('Y koordinata')

        self.draw_fpga_grid(max_x, max_y)

        self.draw_nodes(rrg)

        self.draw_detailed_legend()

        plt.tight_layout()

    # povlacimo iz parsiranog nodes dimenzije i odredjujemo maksimalne
    def get_fpga_dimensions(self, rrg: RRG):
        max_x, max_y = 0, 0
        for node in rrg.nodes.values():
            max_x = max(max_x, node.xhigh)
            max_y = max(max_y, node.yhigh)
        return max_x + 1, max_y + 1

    def draw_fpga_grid(self, max_x: int, max_y: int):
        for x in range(max_x + 1):
            for y in range(max_y + 1):
                rect = patches.Rectangle(
                    (x - 0.5, y - 0.5), 1, 1,
                    linewidth=1, edgecolor='gray',
                    facecolor='lightgray', alpha=0.3
                )
                self.ax.add_patch(rect)

    def draw_nodes(self, rrg: RRG):
        for node in rrg.nodes.values():
            x_center = (node.xlow + node.xhigh) / 2
            y_center = (node.ylow + node.yhigh) / 2

            color = self.colors.get(node.type, 'black')

            # za drugacije vrste node drugacije predstavljamo
            if node.type in ['SOURCE', 'SINK']:
                # blokovi su kvadrati
                size = 0.4
                rect = patches.Rectangle(
                    (x_center - size / 2, y_center - size / 2),
                    size, size,
                    facecolor=color, edgecolor='black',
                    linewidth=1, alpha=0.8
                )
                self.ax.add_patch(rect)

            elif node.type in ['OPIN', 'IPIN']:
                # pins su trouglici
                marker = '^' if node.type == 'OPIN' else 'v'
                self.ax.scatter(x_center, y_center, color=color,
                                marker=marker, s=150, edgecolor='black')

            elif node.type in ['CHANX', 'CHANY']:
                # kanali za rutiranje strelice
                dx = 0.3 if node.type == 'CHANX' else 0
                dy = 0.3 if node.type == 'CHANY' else 0
                self.ax.arrow(x_center - dx, y_center - dy,
                              dx * 2, dy * 2,
                              head_width=0.05, head_length=0.05,
                              fc=color, ec=color, alpha=0.5)

    def draw_detailed_legend(self):
        legend_elements = []

        # Prvo dodajemo source i sink cvorove rute na vrh legende
        legend_elements.extend([
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightblue', markersize=8,
                       label='SOURCE - Početni čvor rute', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', markersize=8,
                       label='SINK - Krajnji čvor rute', markeredgecolor='black'),
            plt.Line2D([0], [0], color='black', lw=2,
                       label='Ruta signala'),
            plt.Line2D([0], [0], marker='o', color='red', markersize=6,
                       label='Čvor rute', linestyle='None')
        ])

        # Zatim dodajemo ostale elemente
        for node_type in ['OPIN', 'IPIN', 'CHANX', 'CHANY']:
            color = self.colors[node_type]
            description = self.node_descriptions.get(node_type, node_type)

            if node_type in ['OPIN', 'IPIN']:
                marker = '^' if node_type == 'OPIN' else 'v'
                legend_elements.append(
                    plt.Line2D([0], [0], marker=marker, color='w',
                               markerfacecolor=color, markersize=10,
                               markeredgecolor='black',
                               label=f'{node_type}: {description}')
                )
            else:
                legend_elements.append(
                    plt.Line2D([0], [0], color=color, lw=3,
                               label=f'{node_type}: {description}')
                )

        legend = self.ax.legend(handles=legend_elements,
                                loc='center left',
                                bbox_to_anchor=(1.05, 0.5),
                                fontsize=10,
                                title="LEGENDA",
                                title_fontsize=11,
                                frameon=True,
                                fancybox=True,
                                shadow=True,
                                ncol=1)

    def visualize_routing(self, rrg: RRG, route):
        self.visualize_fpga_matrix(rrg)

        for net_id, net in route.nets.items():
            if net.nodes:
                x_coords = []
                y_coords = []
                for node in net.nodes:
                    x_center = (node.xlow + node.xhigh) / 2
                    y_center = (node.ylow + node.yhigh) / 2
                    x_coords.append(x_center)
                    y_coords.append(y_center)

                # ruta i cvorovi
                self.ax.plot(x_coords, y_coords, 'k-',
                             linewidth=1.5, alpha=0.7)
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

    def show(self):
        plt.tight_layout()
        plt.show()

    def save(self, filename: str, format='png'):
        plt.savefig(filename, dpi=300, bbox_inches='tight', format=format)