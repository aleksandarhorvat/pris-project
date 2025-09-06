import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.lines import Line2D
from .models import RRG


class FPGAMatrix:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 12))
        self.colors = {
            'SOURCE': 'crimson',
            'SINK': 'linen',
            'OPIN': 'black',
            'IPIN': 'white',
            'CHANX': 'navy',
            'CHANY': 'brown',
            'CLB': '#e0d5d5',
            'IO': '#6b6b6b'
        }

        # Node type descriptions
        self.node_descriptions = {
            'OPIN': 'Output pin',
            'IPIN': 'Input pin',
            'CHANX': 'Horizontal channel',
            'CHANY': 'Vertical channel',
            'CLB': 'Configurable Logic Block',
            'IO': 'Input/Output Block'
        }

    def visualize_fpga_matrix(self, rrg: RRG):
        self.ax.clear()

        max_x, max_y = self.get_fpga_dimensions(rrg)

        self.ax.set_xlim(-1, max_x + 1)
        self.ax.set_ylim(-1, max_y + 1)
        self.ax.set_aspect('equal')
        self.ax.grid(False)
        self.ax.set_title('Matrični prikaz FPGA arhitekture',
                          fontsize=16, pad=20)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)

        # self.draw_optimized_fpga_grid(max_x, max_y)

        self.draw_channels_and_connections(rrg)
        self.draw_nodes(rrg)

        # self.draw_detailed_legend()

        plt.tight_layout()

    def get_fpga_dimensions(self, rrg: RRG):
        max_x, max_y = 0, 0
        for node in rrg.nodes.values():
            max_x = max(max_x, node.xhigh)
            max_y = max(max_y, node.yhigh)
        return max_x + 1, max_y + 1

    def draw_optimized_fpga_grid(self, max_x: int, max_y: int):

        # Draw CLB and IO blocks in a more efficient way
        clb_size = 0.5
        io_size = 0.5
        channel_spacing = 0.12
        num_channels = 8
        channel_width = num_channels * channel_spacing
        clb_channel_gap = 1.25
        io_clb_gap = 1.25

        # Determine CLB positions based on the RRG structure
        clb_positions = []
        io_positions = []

        # This would need to be adapted based on your actual RRG structure
        # For now, we'll place CLBs in a grid pattern
        num_rows = 6
        num_cols = 6

        start_clb_x = io_size + io_clb_gap
        start_clb_y = io_size + io_clb_gap

        for row in range(num_rows):
            for col in range(num_cols):
                x_clb = start_clb_x + col * (clb_size + clb_channel_gap)
                y_clb = start_clb_y + row * (clb_size + clb_channel_gap)

                # Draw CLB
                clb = patches.Rectangle((x_clb, y_clb), clb_size, clb_size,
                                        color=self.colors['CLB'], edgecolor='black', linewidth=1)
                self.ax.add_patch(clb)
                self.ax.text(x_clb + clb_size / 2, y_clb + clb_size / 2, 'CLB',
                             ha='center', va='center', color='black', fontweight='bold')

                # Draw channels around CLB
                if col < num_cols - 1:
                    channel_x = x_clb + clb_size + (clb_channel_gap / 2) - (channel_width / 2)
                    self.draw_channels(channel_x, y_clb, clb_size, is_horizontal=False)

                if row < num_rows - 1:
                    channel_y = y_clb + clb_size + (clb_channel_gap / 2) - (channel_width / 2)
                    self.draw_channels(x_clb, channel_y, clb_size, is_horizontal=True)

                clb_positions.append((x_clb, y_clb))

        # Draw IO blocks
        for col in range(num_cols):
            # Bottom IO
            x_io_bottom = start_clb_x + col * (clb_size + clb_channel_gap)
            y_io_bottom = 0
            io_bottom = patches.Rectangle((x_io_bottom, y_io_bottom), clb_size, clb_size,
                                          color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_bottom)
            self.ax.text(x_io_bottom + clb_size / 2, y_io_bottom + clb_size / 2, 'IO',
                         ha='center', va='center', color='white', fontweight='bold')

            # Top IO
            x_io_top = start_clb_x + col * (clb_size + clb_channel_gap)
            y_io_top = start_clb_y + num_rows * (clb_size + clb_channel_gap)
            io_top = patches.Rectangle((x_io_top, y_io_top), clb_size, clb_size,
                                       color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_top)
            self.ax.text(x_io_top + clb_size / 2, y_io_top + clb_size / 2, 'IO',
                         ha='center', va='center', color='white', fontweight='bold')

            io_positions.append((x_io_bottom, y_io_bottom))
            io_positions.append((x_io_top, y_io_top))

        for row in range(num_rows):
            # Left IO
            x_io_left = 0
            y_io_left = start_clb_y + row * (clb_size + clb_channel_gap)
            io_left = patches.Rectangle((x_io_left, y_io_left), clb_size, clb_size,
                                        color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_left)
            self.ax.text(x_io_left + clb_size / 2, y_io_left + clb_size / 2, 'IO',
                         ha='center', va='center', color='white', fontweight='bold')

            # Right IO
            x_io_right = start_clb_x + num_cols * (clb_size + clb_channel_gap)
            y_io_right = start_clb_y + row * (clb_size + clb_channel_gap)
            io_right = patches.Rectangle((x_io_right, y_io_right), clb_size, clb_size,
                                         color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_right)
            self.ax.text(x_io_right + clb_size / 2, y_io_right + clb_size / 2, 'IO',
                         ha='center', va='center', color='white', fontweight='bold')

            io_positions.append((x_io_left, y_io_left))
            io_positions.append((x_io_right, y_io_right))

    def draw_channels_and_connections(self, rrg: RRG):

        # Collect all elements for batch plotting
        connection_lines_x = []
        connection_lines_y = []

        # Channel parameters
        channel_spacing = 0.12
        num_channels = 8

        # Draw channels for each CHANX and CHANY node
        for node in rrg.nodes.values():
            if node.type == 'CHANX':
                # Horizontal channel
                x_center = (node.xlow + node.xhigh) / 2
                y_center = (node.ylow + node.yhigh) / 2
                length = 1.0  # Channel length

                for i in range(num_channels):
                    line = Line2D(
                        [x_center - length / 2, x_center + length / 2],
                        [y_center + i * channel_spacing, y_center + i * channel_spacing],
                        color='black', linewidth=1, alpha=0.7, zorder=1
                    )
                    self.ax.add_line(line)

            elif node.type == 'CHANY':
                # Vertical channel
                x_center = (node.xlow + node.xhigh) / 2
                y_center = (node.ylow + node.yhigh) / 2
                length = 1.0  # Channel length

                for i in range(num_channels):
                    line = Line2D(
                        [x_center + i * channel_spacing, x_center + i * channel_spacing],
                        [y_center - length / 2, y_center + length / 2],
                        color='black', linewidth=1, alpha=0.7, zorder=1
                    )
                    self.ax.add_line(line)

        # # Draw connections between nodes
        # for edge in rrg.edges:
        #     src_node = rrg.nodes.get(edge.src)
        #     sink_node = rrg.nodes.get(edge.sink)
        #
        #     if src_node and sink_node:
        #         x_src = (src_node.xlow + src_node.xhigh) / 2
        #         y_src = (src_node.ylow + src_node.yhigh) / 2
        #         x_sink = (sink_node.xlow + sink_node.xhigh) / 2
        #         y_sink = (sink_node.ylow + sink_node.yhigh) / 2
        #
        #         connection_lines_x.append([x_src, x_sink])
        #         connection_lines_y.append([y_src, y_sink])
        #
        # # Draw connections
        # for line_x, line_y in zip(connection_lines_x, connection_lines_y):
        #     self.ax.plot(line_x, line_y, 'gray', linewidth=0.5, alpha=0.2, linestyle='--', zorder=2)


    def draw_channels(self, x, y, length, is_horizontal):
        channel_spacing = 0.12
        num_channels = 8

        if is_horizontal:
            for i in range(num_channels):
                line = Line2D([x, x + length], [y + i * channel_spacing, y + i * channel_spacing],
                              color='black', linewidth=1)
                self.ax.add_line(line)
        else:
            for i in range(num_channels):
                line = Line2D([x + i * channel_spacing, x + i * channel_spacing], [y, y + length],
                              color='black', linewidth=1)
                self.ax.add_line(line)

    def draw_nodes(self, rrg: RRG):
        """Draw RRG nodes on top of the FPGA grid"""
        for node in rrg.nodes.values():
            x_center = (node.xlow + node.xhigh) / 2
            y_center = (node.ylow + node.yhigh) / 2

            color = self.colors.get(node.type, 'black')

            # Different representation for different node types
            if node.type in ['SOURCE', 'SINK']:
                # Blocks are squares
                size = 0.4
                rect = patches.Rectangle(
                    (x_center - size / 2, y_center - size / 2),
                    size, size,
                    facecolor=color, edgecolor='black',
                    linewidth=1, alpha=0.8
                )
                self.ax.add_patch(rect)

            elif node.type in ['OPIN', 'IPIN']:
                # Pins are triangles
                marker = '^' if node.type == 'OPIN' else 'v'
                self.ax.scatter(x_center, y_center, color=color,
                                marker=marker, s=150, edgecolor='black')

            # elif node.type in ['CHANX', 'CHANY']:
            #     # Routing channels as arrows
            #     dx = 0.3 if node.type == 'CHANX' else 0
            #     dy = 0.3 if node.type == 'CHANY' else 0
            #     self.ax.arrow(x_center - dx, y_center - dy,
            #                   dx * 2, dy * 2,
            #                   head_width=0.05, head_length=0.05,
            #                   fc=color, ec=color, alpha=0.5)


    def draw_detailed_legend(self):
        legend_elements = []

        legend_elements.extend([
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightblue', markersize=8,
                       label='SOURCE - Route start node', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', markersize=8,
                       label='SINK - Route end node', markeredgecolor='black'),
            plt.Line2D([0], [0], color='black', lw=2,
                       label='Signal route'),
            plt.Line2D([0], [0], marker='o', color='red', markersize=6,
                       label='Route node', linestyle='None'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=self.colors['CLB'], markersize=10,
                       label='CLB - Configurable Logic Block', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor=self.colors['IO'], markersize=10,
                       label='IO - Input/Output Block', markeredgecolor='black')
        ])

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
                                title="LEGEND",
                                title_fontsize=11,
                                frameon=True,
                                fancybox=True,
                                shadow=True,
                                ncol=1)

    def show(self):
        plt.tight_layout()
        plt.show()

    def save(self, filename: str, format='png'):
        plt.savefig(filename, dpi=300, bbox_inches='tight', format=format)