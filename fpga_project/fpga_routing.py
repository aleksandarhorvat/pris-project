import matplotlib.pyplot as plt
from bokeh.colors.named import lemonchiffon
import random
from matplotlib import patches

from .fpga_matrix import FPGAMatrix
from .models import RRG


class FPGARouting(FPGAMatrix):
    def __init__(self):
        super().__init__()

    def visualize_routing_on_grid(self, rrg: RRG, routing_path, net_id=None):
        self.routing_path = routing_path
        self.net_id = net_id

        self.draw_routing_path_on_grid(rrg)

    def draw_routing_path_on_grid(self, rrg: RRG):
        if not self.routing_path:
            print("Nemamo rutu")
            return

        # pratimo edges da bi izbegli duplikate
        drawn_edges = set()
        x_coords = []
        y_coords = []
        node_ids = []
        arrow_positions = []

        # pratimo putanju signala, tj. lista nodova
        signal_flow = {}

        # pravimo rutu
        for i in range(len(self.routing_path) - 1):
            node_id1 = self.routing_path[i]
            node_id2 = self.routing_path[i + 1]

            if node_id1 not in signal_flow:
                signal_flow[node_id1] = []
            signal_flow[node_id1].append(node_id2)

        # skupljamo sve sinkove
        sink_nodes = []
        for node_id in self.routing_path:
            if rrg.nodes[node_id].type == "SINK":
                if node_id in self.coord_map:
                    sink_nodes.append((node_id, self.coord_map[node_id]))

        for i in range(len(self.routing_path) - 1):
            node_id1 = self.routing_path[i]
            node_id2 = self.routing_path[i + 1]

            if (rrg.nodes[node_id1].type == "SINK" or
                    rrg.nodes[node_id2].type == "SINK"):
                continue

            if node_id1 not in self.coord_map or node_id2 not in self.coord_map:
                print(f"Upozorenje: Node {node_id1} ili {node_id2} nije na coord_map")
                continue

            x1, y1 = self.coord_map[node_id1]
            x2, y2 = self.coord_map[node_id2]

            node1 = rrg.nodes[node_id1]
            node2 = rrg.nodes[node_id2]

            # ovaj deo dole se bavi onim preskakanjem kada imamo povratnu putanju
            if i == 0:
                x_coords.append(x1)
                y_coords.append(y1)
                node_ids.append(node_id1)
            x_coords.append(x2)
            y_coords.append(y2)
            node_ids.append(node_id2)

            edge_key = (node_id1, node_id2)
            if edge_key in drawn_edges:
                continue
            drawn_edges.add(edge_key)

            # racunamo vektor u kom smeru cemo nacrtati strelice
            dx = x2 - x1
            dy = y2 - y1
            length = (dx ** 2 + dy ** 2) ** 0.5
            if length > 0:
                dx_norm = dx / length
                dy_norm = dy / length
            else:
                dx_norm, dy_norm = 0, 0

            # ovde nam je crtanje rute podeljeno po segmentima u zavisnosti sta se povezuje, isto vazi i za crtanje strelica
            # io veze - direktna linija
            if node1.type == 'IO' or node2.type == 'IO':
                self.ax.plot([x1, x2], [y1, y2],
                             color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.9)
                # dodajemo strelice na 70% ovog segementa
                arrow_x = x1 + 0.7 * dx
                arrow_y = y1 + 0.7 * dy
                arrow_positions.append((arrow_x, arrow_y, dx_norm, dy_norm))

            # kanal-kanal veza
            if node1.type in ['CHANX', 'CHANY'] and node2.type in ['CHANX', 'CHANY']:
                # ista vrsta kanala - direktna linija
                if node1.type == node2.type:
                    self.ax.plot([x1, x2], [y1, y2],
                                 color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.9)
                    # dodajemo strelice na 70% ovog segementa
                    arrow_x = x1 + 0.7 * dx
                    arrow_y = y1 + 0.7 * dy
                    arrow_positions.append((arrow_x, arrow_y, dx_norm, dy_norm))
                else:
                    # razlicita vrsta kanala - L-oblik
                    # Pronađi tačku preseka (sredinu kanala)
                    if node1.type == 'CHANX':  # horizontalni -> vertikalni
                        # Koristimo x koordinatu vertikalnog kanala i y koordinatu horizontalnog kanala
                        turn_x = x2
                        turn_y = y1
                    else:  # vertikalni -> horizontalni
                        # Koristimo x koordinatu vertikalnog kanala i y koordinatu horizontalnog kanala
                        turn_x = x1
                        turn_y = y2

                    # Crtamo L-oblik: prvi segment do tačke okreta, pa drugi segment
                    self.ax.plot([x1, turn_x], [y1, turn_y],
                                 color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.9)
                    self.ax.plot([turn_x, x2], [turn_y, y2],
                                 color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.9)

                    # dodajemo strelice za oba smera crtanja
                    # prvi smer - do okreta
                    seg1_dx = turn_x - x1
                    seg1_dy = turn_y - y1
                    seg1_length = (seg1_dx ** 2 + seg1_dy ** 2) ** 0.5
                    if seg1_length > 0:
                        seg1_dx_norm = seg1_dx / seg1_length
                        seg1_dy_norm = seg1_dy / seg1_length
                    else:
                        seg1_dx_norm, seg1_dy_norm = 0, 0

                    arrow_x1 = x1 + 0.7 * seg1_dx
                    arrow_y1 = y1 + 0.7 * seg1_dy
                    arrow_positions.append((arrow_x1, arrow_y1, seg1_dx_norm, seg1_dy_norm))

                    # drugi smer - od okreta
                    seg2_dx = x2 - turn_x
                    seg2_dy = y2 - turn_y
                    seg2_length = (seg2_dx ** 2 + seg2_dy ** 2) ** 0.5
                    if seg2_length > 0:
                        seg2_dx_norm = seg2_dx / seg2_length
                        seg2_dy_norm = seg2_dy / seg2_length
                    else:
                        seg2_dx_norm, seg2_dy_norm = 0, 0

                    arrow_x2 = turn_x + 0.7 * seg2_dx
                    arrow_y2 = turn_y + 0.7 * seg2_dy
                    arrow_positions.append((arrow_x2, arrow_y2, seg2_dx_norm, seg2_dy_norm))

            else:
                # pin-kanal ili kanal-pin veza - direktna linija
                self.ax.plot([x1, x2], [y1, y2],
                             color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.9)
                # dodajemo strelice na 70% ovog segementa
                arrow_x = x1 + 0.7 * dx
                arrow_y = y1 + 0.7 * dy
                arrow_positions.append((arrow_x, arrow_y, dx_norm, dy_norm))

        # sve strelice
        for arrow_x, arrow_y, dx_norm, dy_norm in arrow_positions:
            # crtamo samo ako imamo dobar smer
            if dx_norm != 0 or dy_norm != 0:
                # duzina repa strelice da ne bude predugacko
                tail_length = 0.05
                self.ax.arrow(arrow_x, arrow_y, dx_norm * tail_length, dy_norm * tail_length, head_width=0.09,
                              head_length=0.09,
                              fc=self.colors['ROUTED_PATH'],
                              ec=self.colors['ROUTED_PATH'])

        # labele za source
        if len(node_ids) >= 2:
            self.ax.text(x_coords[0], y_coords[0] - 0.3, f'{node_ids[0]}',
                         ha='center', va='center', fontsize=7,
                         bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue"))

        # labele za sve sink
        for node_id, (x, y) in sink_nodes:
            self.ax.text(x, y - 0.3, f'{node_id}',
                         ha='center', va='center', fontsize=7,
                         bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen"))

    def visualize_routing_by_branching(self, rrg: RRG, route_data, branching_factor: int):
        if not route_data.nets:
            print("Nema netova")
            return
            # lista svih routing pathova za crtanje
        all_routing_paths = []

        for net_id, net in route_data.nets.items():
            num_sinks = sum(1 for node in net.nodes if node.type == "SINK")
            if num_sinks != branching_factor:
                continue  # preskocimo netove koji ne zadovoljavaju faktor

            routing_path = [node.id for node in net.nodes]
            all_routing_paths.append((routing_path, net_id))

        # pozivamo draw metodu sa svim routing pathovima
        self.draw_branching_paths_on_grid(rrg, all_routing_paths)

    def draw_branching_paths_on_grid(self, rrg: RRG, all_routing_paths: list):
        if not all_routing_paths:
            print("Nema ruta za crtanje")
            return

        labeled_positions = {}

        colors = {}
        for _, net_id in all_routing_paths:
            colors[net_id] = (random.random(), random.random(), random.random())

        for routing_path, net_id in all_routing_paths:
            drawn_edges = set()
            arrow_positions = []
            x_coords, y_coords = [], []

            for i in range(len(routing_path) - 1):
                node_id1 = routing_path[i]
                node_id2 = routing_path[i + 1]

                node1 = rrg.nodes[node_id1]
                node2 = rrg.nodes[node_id2]

                if (rrg.nodes[node_id1].type == "SINK" or
                        rrg.nodes[node_id2].type == "SINK"):
                    continue

                if node_id1 not in self.coord_map or node_id2 not in self.coord_map:
                    print(f"Upozorenje: Node {node_id1} ili {node_id2} nije na coord_map")
                    continue

                x1, y1 = self.coord_map[node_id1]
                x2, y2 = self.coord_map[node_id2]

                if node2.type == "SINK":
                    self.ax.plot([x1, x2], [y1, y2], color=colors[net_id], linewidth=2, alpha=0.9)
                    dx, dy = x2 - x1, y2 - y1
                    length = (dx ** 2 + dy ** 2) ** 0.5
                    if length > 0:
                        dx_norm, dy_norm = dx / length, dy / length
                        self.ax.arrow(x1 + 0.7 * dx, y1 + 0.7 * dy, dx_norm * 0.05, dy_norm * 0.05,
                                      head_width=0.09, head_length=0.09, fc=colors[net_id], ec=colors[net_id])
                    # dodavanje koordinata za source/sink label
                    if i == 0:
                        x_coords.append(x1)
                        y_coords.append(y1)
                    x_coords.append(x2)
                    y_coords.append(y2)
                    break  # preskoci dalje, ne crtamo iz SINK-a

                dx = x2 - x1
                dy = y2 - y1
                length = (dx ** 2 + dy ** 2) ** 0.5
                dx_norm, dy_norm = (dx / length, dy / length) if length > 0 else (0, 0)

                if node1.type in ['CHANX', 'CHANY'] and node2.type in ['CHANX', 'CHANY'] and node1.type != node2.type:

                    turn_x = x2 if node1.type == 'CHANX' else x1
                    turn_y = y1 if node1.type == 'CHANX' else y2
                    self.ax.plot([x1, turn_x], [y1, turn_y], color=colors[net_id], linewidth=2, alpha=0.9)
                    self.ax.plot([turn_x, x2], [turn_y, y2], color=colors[net_id], linewidth=2, alpha=0.9)

                    # strelice za L-shape
                    seg1_dx, seg1_dy = turn_x - x1, turn_y - y1
                    seg1_length = (seg1_dx ** 2 + seg1_dy ** 2) ** 0.5
                    seg1_dx_norm = seg1_dx / seg1_length if seg1_length > 0 else 0
                    seg1_dy_norm = seg1_dy / seg1_length if seg1_length > 0 else 0
                    arrow_positions.append((x1 + 0.7 * seg1_dx, y1 + 0.7 * seg1_dy, seg1_dx_norm, seg1_dy_norm))

                    seg2_dx, seg2_dy = x2 - turn_x, y2 - turn_y
                    seg2_length = (seg2_dx ** 2 + seg2_dy ** 2) ** 0.5
                    seg2_dx_norm = seg2_dx / seg2_length if seg2_length > 0 else 0
                    seg2_dy_norm = seg2_dy / seg2_length if seg2_length > 0 else 0
                    arrow_positions.append((turn_x + 0.7 * seg2_dx, turn_y + 0.7 * seg2_dy, seg2_dx_norm, seg2_dy_norm))
                else:

                    self.ax.plot([x1, x2], [y1, y2], color=colors[net_id], linewidth=2, alpha=0.9)
                    arrow_positions.append((x1 + 0.7 * dx, y1 + 0.7 * dy, dx_norm, dy_norm))

                if i == 0:
                    x_coords.append(x1)
                    y_coords.append(y1)
                x_coords.append(x2)
                y_coords.append(y2)
                drawn_edges.add((node_id1, node_id2))

            for arrow_x, arrow_y, dx_norm, dy_norm in arrow_positions:
                if dx_norm != 0 or dy_norm != 0:
                    tail_length = 0.05
                    self.ax.arrow(arrow_x, arrow_y, dx_norm * tail_length, dy_norm * tail_length,
                                  head_width=0.09, head_length=0.09, fc=colors[net_id], ec=colors[net_id])

            # po jedan samo ispise
            # self.ax.text(x_coords[0], y_coords[0]-0.3, f"S-{net_id}",
            #             ha='center', va='center', fontsize=7,
            #             bbox=dict(boxstyle="round,pad=0.2", facecolor="lightblue"))

            # sink_nodes = [node_id for node_id in routing_path if rrg.nodes[node_id].type == "SINK"]
            # for node_id in sink_nodes:
            #     x, y = self.coord_map[node_id]
            #     self.ax.text(x, y-0.3, f"E-{net_id}",
            #                 ha='center', va='center', fontsize=7,
            #                 bbox=dict(boxstyle="round,pad=0.2", facecolor="lightgreen"))

            # deo sa offsetom - nabaca sve nodes koji su tu
            nodes_list = [rrg.nodes[node_id] for node_id in routing_path]
            for i, node in enumerate(nodes_list):
                if node.type in ['SOURCE', 'SINK']:
                    x_pos = self.coord_map[node.id][0]
                    y_pos = self.coord_map[node.id][1]
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
                                 ha="center", va="center", fontsize=6,
                                 bbox=dict(boxstyle="round,pad=0.1", facecolor=facecolor))



    def visualize_first_n_routings(self, rrg: RRG, routing_paths, n):
        # paleta boja (možeš proširiti po želji)
        color_palette = [
            'red', 'blue', 'green', 'orange', 'purple',
            'brown', 'pink', 'cyan', 'magenta', 'yellow'
        ]

        n = min(n, len(routing_paths))

        for i in range(n):
            routing_path = routing_paths[i]

            # postavi boju za trenutni signal
            self.colors['ROUTED_PATH'] = color_palette[i % len(color_palette)]

            # iscrtaj signal
            self.visualize_routing_on_grid(rrg, routing_path, net_id=i)
