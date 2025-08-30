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
            'SOURCE': 'Izlaz logičkog bloka',
            'SINK': 'Ulaz logičkog bloka',
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
        self.ax.set_title('Matrični prikaz FPGA arhitekture', fontsize=16, pad=20)
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

        for node_type, color in self.colors.items():
            description = self.node_descriptions.get(node_type, node_type)

            if node_type in ['SOURCE', 'SINK']:
                legend_elements.append(
                    patches.Patch(facecolor=color,
                                  edgecolor='black',
                                  label=f'{node_type}: {description}')
                )
            elif node_type in ['OPIN', 'IPIN']:
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

        # putanja rutiranja i pocetni i krajnji cvorovi
        legend_elements.extend([
            plt.Line2D([0], [0], color='black', lw=2,
                       label='Ruta signala'),
            plt.Line2D([0], [0], marker='o', color='red', markersize=6,
                       label='Čvor rute', linestyle='None'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightblue', markersize=8,
                       label='S - Početni čvor rute', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', markersize=8,
                       label='E - Krajnji čvor rute', markeredgecolor='black')
        ])


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
                for node in net.nodes.values():
                    x_center = (node.xlow + node.xhigh) / 2
                    y_center = (node.ylow + node.yhigh) / 2
                    x_coords.append(x_center)
                    y_coords.append(y_center)

                # ruta i cvorovi
                self.ax.plot(x_coords, y_coords, 'k-', linewidth=1.5, alpha=0.7)
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

    def show(self):
        plt.tight_layout()
        plt.show()

    def save(self, filename: str, format='png'):
        plt.savefig(filename, dpi=300, bbox_inches='tight', format=format)

