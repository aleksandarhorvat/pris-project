import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D
from .models import RRG


class FPGAMatrix:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 12))
        self.routing_path = []
        self.colors = {
            'CLB': 'linen',
            'IO': 'brown',
            'ROUTED_PATH': 'red',
            'SOURCE' : 'lightblue',
            'SINK' : 'lightyellow'
        }

        self.clb_size = 0.5
        self.io_size = 0.5
        self.channel_spacing = 0.12
        self.num_channels = 8
        self.channel_width = self.num_channels * self.channel_spacing
        self.clb_channel_gap = 1.25
        self.io_clb_gap = 1.25

    def draw_fpga_grid(self, num_rows=6, num_cols=6):
        self.ax.clear()

        # racunanje velicine za dobro skaliranje
        total_width = num_cols * (self.clb_size + self.clb_channel_gap) + self.io_clb_gap * 2
        total_height = num_rows * (self.clb_size + self.clb_channel_gap) + self.io_clb_gap * 2

        self.ax.set_xlim(-1, total_width)
        self.ax.set_ylim(-1, total_height)
        self.ax.set_aspect('equal')
        self.ax.set_title('Matrični prikaz FPGA arhitekture', fontsize=16)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

        start_clb_x = self.io_size + self.io_clb_gap
        start_clb_y = self.io_size + self.io_clb_gap

        # crtamo CLB blokove
        for row in range(num_rows):
            for col in range(num_cols):
                # pozicija CLB bloka
                x_clb = start_clb_x + col * (self.clb_size + self.clb_channel_gap)
                y_clb = start_clb_y + row * (self.clb_size + self.clb_channel_gap)

                # crtamo CLB blok
                clb = patches.Rectangle((x_clb, y_clb), self.clb_size, self.clb_size,
                                        color=self.colors['CLB'], edgecolor='black', linewidth=1)
                self.ax.add_patch(clb)
                self.ax.text(x_clb + self.clb_size / 2, y_clb + self.clb_size / 2, 'CLB',
                             ha='center', va='center', color='black', fontweight='bold')

                # vertikalni kanali desno od CLB bloka
                if col < num_cols - 1:
                    channel_x = x_clb + self.clb_size + (self.clb_channel_gap / 2) - (self.channel_width / 2)
                    self.draw_channels(channel_x, y_clb, self.clb_size, is_horizontal=False)

                # horizontalni kanali iznad CLB bloka
                if row < num_rows - 1:
                    channel_y = y_clb + self.clb_size + (self.clb_channel_gap / 2) - (self.channel_width / 2)
                    self.draw_channels(x_clb, channel_y, self.clb_size, is_horizontal=True)


        self.draw_io_blocks(num_rows, num_cols, start_clb_x, start_clb_y)

        self.draw_detailed_legend()

    # vise kanala
    def draw_channels(self, x, y, length, is_horizontal):
        if is_horizontal:
            for i in range(self.num_channels):
                line = Line2D([x, x + length],
                              [y + i * self.channel_spacing, y + i * self.channel_spacing],
                              color='gray', linewidth=1, alpha=0.7)
                self.ax.add_line(line)
        else:
            for i in range(self.num_channels):
                line = Line2D([x + i * self.channel_spacing, x + i * self.channel_spacing],
                              [y, y + length],
                              color='gray', linewidth=1, alpha=0.7)
                self.ax.add_line(line)

    def draw_io_blocks(self, num_rows, num_cols, start_clb_x, start_clb_y):
        for col in range(num_cols):

            # donji IO
            x_io = start_clb_x + col * (self.clb_size + self.clb_channel_gap)
            y_io = 0
            io = patches.Rectangle((x_io, y_io), self.clb_size, self.clb_size,
                                   color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io)
            self.ax.text(x_io + self.clb_size / 2, y_io + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

            # gornji IO
            y_io_top = start_clb_y + num_rows * (self.clb_size + self.clb_channel_gap)
            io_top = patches.Rectangle((x_io, y_io_top), self.clb_size, self.clb_size,
                                       color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_top)
            self.ax.text(x_io + self.clb_size / 2, y_io_top + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

        for row in range(num_rows):
            # levi IO
            x_io_left = 0
            y_io_left = start_clb_y + row * (self.clb_size + self.clb_channel_gap)
            io_left = patches.Rectangle((x_io_left, y_io_left), self.clb_size, self.clb_size,
                                        color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_left)
            self.ax.text(x_io_left + self.clb_size / 2, y_io_left + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

            # desni IO
            x_io_right = start_clb_x + num_cols * (self.clb_size + self.clb_channel_gap)
            io_right = patches.Rectangle((x_io_right, y_io_left), self.clb_size, self.clb_size,
                                         color=self.colors['IO'], edgecolor='black', linewidth=1)
            self.ax.add_patch(io_right)
            self.ax.text(x_io_right + self.clb_size / 2, y_io_left + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

    def map_rrg_to_grid(self, rrg: RRG, num_rows=6, num_cols=6):
        """Map RRG coordinates to visual grid coordinates"""
        self.coord_map = {}
        self.num_rows = num_rows
        self.num_cols = num_cols

        start_clb_x = self.io_size + self.io_clb_gap
        start_clb_y = self.io_size + self.io_clb_gap

        # Map RRG coordinates to visual positions
        for node in rrg.nodes.values():
            visual_x, visual_y = self._calculate_node_position(node, start_clb_x, start_clb_y)

            if visual_x is not None and visual_y is not None:
                self.coord_map[node.id] = (visual_x, visual_y)

    def _calculate_node_position(self, node, start_clb_x, start_clb_y):
        """Calculate the visual position for a node based on its type and coordinates"""
        if node.type in ['SOURCE', 'SINK', 'OPIN', 'IPIN']:
            # These are typically located at CLB positions
            if 0 <= node.xlow < self.num_cols and 0 <= node.ylow < self.num_rows:
                visual_x = start_clb_x + node.xlow * (self.clb_size + self.clb_channel_gap)
                visual_y = start_clb_y + node.ylow * (self.clb_size + self.clb_channel_gap)

                # Adjust for center of the block
                visual_x += self.clb_size / 2
                visual_y += self.clb_size / 2

                return visual_x, visual_y

        elif node.type in ['CHANX', 'CHANY']:
            # Routing channels - need special handling
            return self._calculate_channel_position(node, start_clb_x, start_clb_y)

        elif node.type == 'IO':
            # IO blocks - need special handling
            return self._calculate_io_position(node, start_clb_x, start_clb_y)

        return None, None

    def _calculate_channel_position(self, node, start_clb_x, start_clb_y):
        """Calculate position for channel nodes"""
        if node.type == 'CHANX':  # Horizontal channel
            # Position in the horizontal channel between rows
            if 0 <= node.ylow < self.num_rows - 1:
                y_pos = start_clb_y + node.ylow * (self.clb_size + self.clb_channel_gap) + self.clb_size
                y_pos += (self.clb_channel_gap / 2) - (self.channel_width / 2)

                # X position based on track number
                x_pos = start_clb_x + node.xlow * (self.clb_size + self.clb_channel_gap)
                x_pos += (node.ptc % self.num_channels) * self.channel_spacing

                return x_pos, y_pos + (self.channel_spacing * node.ptc)

        elif node.type == 'CHANY':  # Vertical channel
            # Position in the vertical channel between columns
            if 0 <= node.xlow < self.num_cols - 1:
                x_pos = start_clb_x + node.xlow * (self.clb_size + self.clb_channel_gap) + self.clb_size
                x_pos += (self.clb_channel_gap / 2) - (self.channel_width / 2)

                # Y position based on track number
                y_pos = start_clb_y + node.ylow * (self.clb_size + self.clb_channel_gap)
                y_pos += (node.ptc % self.num_channels) * self.channel_spacing

                return x_pos + (self.channel_spacing * node.ptc), y_pos

        return None, None

    def _calculate_io_position(self, node, start_clb_x, start_clb_y):
        """Calculate position for IO nodes"""
        # Bottom IO row
        if node.ylow == 0 and node.yhigh == 0:
            x_pos = start_clb_x + node.xlow * (self.clb_size + self.clb_channel_gap)
            return x_pos + self.clb_size / 2, self.io_size / 2

        # Top IO row
        elif node.ylow == self.num_rows and node.yhigh == self.num_rows:
            x_pos = start_clb_x + node.xlow * (self.clb_size + self.clb_channel_gap)
            y_pos = start_clb_y + self.num_rows * (self.clb_size + self.clb_channel_gap)
            return x_pos + self.clb_size / 2, y_pos + self.clb_size / 2

        # Left IO column
        elif node.xlow == 0 and node.xhigh == 0:
            y_pos = start_clb_y + node.ylow * (self.clb_size + self.clb_channel_gap)
            return self.io_size / 2, y_pos + self.clb_size / 2

        # Right IO column
        elif node.xlow == self.num_cols and node.xhigh == self.num_cols:
            x_pos = start_clb_x + self.num_cols * (self.clb_size + self.clb_channel_gap)
            y_pos = start_clb_y + node.ylow * (self.clb_size + self.clb_channel_gap)
            return x_pos + self.clb_size / 2, y_pos + self.clb_size / 2

        return None, None

    def visualize_routing_on_grid(self, rrg: RRG, routing_path, num_rows=6, num_cols=6):
        """Visualize routing path on the grid"""
        # Store dimensions for later use
        self.num_rows = num_rows
        self.num_cols = num_cols

        # Set routing path
        self.routing_path = routing_path

        # Redraw the grid
        self.draw_fpga_grid(num_rows, num_cols)

        # Map RRG coordinates to visual grid
        self.map_rrg_to_grid(rrg, num_rows, num_cols)

        # Draw the routing path
        self.draw_routing_path_on_grid(rrg)

    def draw_routing_path_on_grid(self, rrg: RRG):
        """Draw routing path on the visual grid"""
        if not self.routing_path:
            print("No routing path to visualize")
            return

        # Draw all connections first
        for i in range(len(self.routing_path) - 1):
            node_id1 = self.routing_path[i]
            node_id2 = self.routing_path[i + 1]

            if node_id1 in self.coord_map and node_id2 in self.coord_map:
                x1, y1 = self.coord_map[node_id1]
                x2, y2 = self.coord_map[node_id2]

                # Draw connection
                self.ax.plot([x1, x2], [y1, y2],
                             color=self.colors['ROUTED_PATH'], linewidth=2, alpha=0.8, zorder=5)

        # Then draw all nodes on top
        for node_id in self.routing_path:
            if node_id not in self.coord_map or node_id not in rrg.nodes:
                continue

            node = rrg.nodes[node_id]
            visual_x, visual_y = self.coord_map[node_id]

            # Draw node marker with different styles based on type
            if node.type in ['CHANX', 'CHANY']:
                # For channels, draw a circle
                self.ax.scatter(visual_x, visual_y, color=self.colors['ROUTED_PATH'],
                                s=80, edgecolor='black', zorder=6)
            elif node.type == 'SOURCE':
                # For source nodes, draw a special marker
                self.ax.scatter(visual_x, visual_y, color=self.colors['SOURCE'],
                                s=100, edgecolor='black', marker='s', zorder=7)
            elif node.type == 'SINK':
                # For sink nodes, draw a special marker
                self.ax.scatter(visual_x, visual_y, color=self.colors['SINK'],
                                s=100, edgecolor='black', marker='s', zorder=7)
            else:
                # For other nodes, draw a square
                size = 0.1
                rect = patches.Rectangle((visual_x - size / 2, visual_y - size / 2),
                                         size, size,
                                         facecolor=self.colors['ROUTED_PATH'],
                                         edgecolor='black', zorder=6)
                self.ax.add_patch(rect)

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

    def show(self):
        plt.tight_layout()
        plt.show()

    def save(self, filename: str, format='png'):
        plt.savefig(filename, dpi=300, bbox_inches='tight', format=format)