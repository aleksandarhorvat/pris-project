import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from .models import RRG


class FPGAVisualizer:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 12))
        self.colors = {
            'SOURCE': 'green',
            'SINK': 'red',
            'OPIN': 'blue',
            'IPIN': 'cyan',
            'CHANX': 'orange',
            'CHANY': 'purple'
        }

        # Node type descriptions for legend
        self.node_descriptions = {
            'SOURCE': 'Output port (izlaz logičkog bloka)',
            'SINK': 'Input port (ulaz logičkog bloka)',
            'OPIN': 'Output pin (izlazni pin)',
            'IPIN': 'Input pin (ulazni pin)',
            'CHANX': 'Horizontal channel (horizontalni kanal)',
            'CHANY': 'Vertical channel (vertikalni kanal)'
        }

    def visualize_fpga_matrix(self, rrg: RRG):
        """Visualize the complete FPGA matrix"""
        self.ax.clear()

        # Find the overall FPGA dimensions
        max_x, max_y = self._get_fpga_dimensions(rrg)

        # Set up the plot
        self.ax.set_xlim(-1, max_x + 1)
        self.ax.set_ylim(-1, max_y + 1)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('FPGA Architecture Matrix - Matrični prikaz FPGA arhitekture', fontsize=16, pad=20)
        self.ax.set_xlabel('X Coordinate (X koordinata)')
        self.ax.set_ylabel('Y Coordinate (Y koordinata)')

        # Draw the FPGA grid
        self._draw_fpga_grid(max_x, max_y)

        # Draw all nodes
        self._draw_nodes(rrg)

        # Draw comprehensive legend
        self._draw_detailed_legend()

        plt.tight_layout()

    def _get_fpga_dimensions(self, rrg: RRG):
        """Get the maximum dimensions of the FPGA"""
        max_x, max_y = 0, 0
        for node in rrg.nodes.values():
            max_x = max(max_x, node.xhigh)
            max_y = max(max_y, node.yhigh)
        return max_x + 1, max_y + 1

    def _draw_fpga_grid(self, max_x: int, max_y: int):
        """Draw the basic FPGA grid"""
        for x in range(max_x + 1):
            for y in range(max_y + 1):
                # Draw grid cell
                rect = patches.Rectangle(
                    (x - 0.5, y - 0.5), 1, 1,
                    linewidth=1, edgecolor='gray',
                    facecolor='lightgray', alpha=0.5
                )
                self.ax.add_patch(rect)

                # Add coordinate labels
                if x == 0 or y == 0:
                    self.ax.text(x, y, f'({x},{y})',
                                 ha='center', va='center',
                                 fontsize=8, color='darkblue')

    def _draw_nodes(self, rrg: RRG):
        """Draw all nodes with appropriate symbols"""
        for node in rrg.nodes.values():
            x_center = (node.xlow + node.xhigh) / 2
            y_center = (node.ylow + node.yhigh) / 2

            color = self.colors.get(node.type, 'black')

            # Different markers for different node types
            if node.type in ['SOURCE', 'SINK']:
                # Logic blocks - squares
                size = 0.4
                rect = patches.Rectangle(
                    (x_center - size / 2, y_center - size / 2),
                    size, size,
                    facecolor=color, edgecolor='black',
                    linewidth=1, alpha=0.8
                )
                self.ax.add_patch(rect)

            elif node.type in ['OPIN', 'IPIN']:
                # Pins - triangles
                marker = '^' if node.type == 'OPIN' else 'v'
                self.ax.scatter(x_center, y_center, color=color,
                                marker=marker, s=100, edgecolor='black')

            elif node.type in ['CHANX', 'CHANY']:
                # Routing channels - arrows
                dx = 0.3 if node.type == 'CHANX' else 0
                dy = 0.3 if node.type == 'CHANY' else 0
                self.ax.arrow(x_center - dx, y_center - dy,
                              dx * 2, dy * 2,
                              head_width=0.1, head_length=0.1,
                              fc=color, ec=color, alpha=0.7)

            # Add node ID for debugging
            self.ax.text(x_center, y_center + 0.15, str(node.id),
                         ha='center', va='center', fontsize=6, color='darkred')

    def _draw_detailed_legend(self):
        """Draw comprehensive legend with symbols and descriptions"""
        legend_elements = []

        # Create legend items with both symbols and descriptions
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

        # Add routing path legend
        legend_elements.extend([
            plt.Line2D([0], [0], color='red', lw=2,
                       label='Routed path (ruta signala)'),
            plt.Line2D([0], [0], marker='o', color='red', markersize=6,
                       label='Routing node (čvor rute)', linestyle='None')
        ])

        # Create legend with two columns for better layout
        legend = self.ax.legend(handles=legend_elements,
                                loc='center left',
                                bbox_to_anchor=(1.05, 0.5),
                                fontsize=10,
                                title="LEGENDA - Objašnjenje simbola\n" +
                                      "LEGEND - Symbol explanations",
                                title_fontsize=11,
                                frameon=True,
                                fancybox=True,
                                shadow=True,
                                ncol=1)

        # Make legend background slightly transparent
        legend.get_frame().set_alpha(0.9)

    def visualize_routing(self, rrg: RRG, route):
        """Visualize specific routing on top of FPGA matrix"""
        self.visualize_fpga_matrix(rrg)

        # Draw the routed paths
        for net_id, net in route.nets.items():
            if net.nodes:
                # Extract coordinates from nodes
                x_coords = []
                y_coords = []
                for node in net.nodes.values():
                    x_center = (node.xlow + node.xhigh) / 2
                    y_center = (node.ylow + node.yhigh) / 2
                    x_coords.append(x_center)
                    y_coords.append(y_center)

                # Draw the path
                self.ax.plot(x_coords, y_coords, 'r-', linewidth=2, alpha=0.8, label='_Routed path')
                self.ax.plot(x_coords, y_coords, 'ro', markersize=4, label='_Routing node')

                # Label the net
                if x_coords:
                    self.ax.text(x_coords[0], y_coords[0] + 0.2, f'Net{net_id}',
                                 ha='center', va='center', fontsize=8,
                                 bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow"))

    def create_pdf_report(self, rrg: RRG, route=None, filename="fpga_report.pdf"):
        """Create a comprehensive PDF report with visualization"""
        with PdfPages(filename) as pdf:
            # Page 1: FPGA Architecture
            self.visualize_fpga_matrix(rrg)
            plt.suptitle("FPGA Architecture Report - Izvještaj o FPGA arhitekturi", fontsize=18, y=0.98)
            pdf.savefig(bbox_inches='tight')
            plt.close()

            # Page 2: Routing visualization (if route is provided)
            if route:
                self.visualize_routing(rrg, route)
                plt.suptitle("FPGA Routing Visualization - Vizualizacija rutiranja", fontsize=18, y=0.98)
                pdf.savefig(bbox_inches='tight')
                plt.close()

            # Page 3: Statistics and information
            self._create_statistics_page(rrg, route, pdf)

        print(f"PDF report saved as {filename}")

    def _create_statistics_page(self, rrg: RRG, route, pdf):
        """Create a statistics page for the PDF report"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        # Title
        ax.text(0.5, 0.95, "FPGA Statistics - Statistika FPGA",
                ha='center', va='center', fontsize=16, fontweight='bold',
                transform=ax.transAxes)

        # Architecture statistics
        stats_text = [
            "ARCHITECTURE STATISTICS - STATISTIKA ARHITEKTURE:",
            f"Total nodes: {len(rrg.nodes)}",
            f"Total edges: {len(rrg.edges)}",
            f"SOURCES: {sum(1 for n in rrg.nodes.values() if n.type == 'SOURCE')}",
            f"SINKS: {sum(1 for n in rrg.nodes.values() if n.type == 'SINK')}",
            f"OPINS: {sum(1 for n in rrg.nodes.values() if n.type == 'OPIN')}",
            f"IPINS: {sum(1 for n in rrg.nodes.values() if n.type == 'IPIN')}",
            f"CHANX: {sum(1 for n in rrg.nodes.values() if n.type == 'CHANX')}",
            f"CHANY: {sum(1 for n in rrg.nodes.values() if n.type == 'CHANY')}",
            ""
        ]

        # Routing statistics (if available)
        if route:
            stats_text.extend([
                "ROUTING STATISTICS - STATISTIKA RUTIRANJA:",
                f"Total nets: {len(route.nets)}",
                f"Total routed nodes: {sum(len(net.nodes) for net in route.nets.values())}",
                ""
            ])

        # Add coordinate range
        max_x, max_y = self._get_fpga_dimensions(rrg)
        stats_text.extend([
            "FPGA DIMENSIONS - DIMENZIJE FPGA:",
            f"X range: 0 - {max_x - 1}",
            f"Y range: 0 - {max_y - 1}",
            f"Grid size: {max_x} x {max_y}",
            ""
        ])

        # Add the text to the page
        y_position = 0.85
        for line in stats_text:
            ax.text(0.1, y_position, line, fontsize=12, transform=ax.transAxes)
            y_position -= 0.05

        # Add conclusion
        ax.text(0.1, 0.2,
                "This report was automatically generated from FPGA routing files.\n"
                "Ovaj izvještaj je automatski generiran iz FPGA routing datoteka.",
                fontsize=10, style='italic', transform=ax.transAxes)

        pdf.savefig(bbox_inches='tight')
        plt.close()

    def show(self):
        """Display the visualization"""
        plt.tight_layout()
        plt.show()

    def save(self, filename: str, format='png'):
        """Save the visualization to file (PNG, PDF, SVG, etc.)"""
        plt.savefig(filename, dpi=300, bbox_inches='tight', format=format)