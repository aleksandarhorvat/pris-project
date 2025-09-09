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
            'ROUTED_PATH': 'black',
            'SOURCE': 'lightblue',
            'SINK': 'lightgreen'
        }

        self.clb_size = 0.5
        self.io_size = 0.5
        self.channel_spacing = 0.12
        self.num_channels = 8
        self.channel_width = self.num_channels * self.channel_spacing
        self.clb_channel_gap = 1.25
        self.io_clb_gap = 1.25

    def visualize_matrix(self, rrg, num_rows=6, num_cols=6):
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.draw_fpga_grid(num_rows, num_cols)

        self.map_rrg_to_grid(rrg, num_rows, num_cols)

        self.draw_detailed_legend()

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
                                        color=self.colors['CLB'])
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


        self.draw_io_clb_channels(num_rows, num_cols, start_clb_x, start_clb_y)

    def draw_io_blocks(self, num_rows, num_cols, start_clb_x, start_clb_y):
        for col in range(num_cols):
            # donji IO
            x_io = start_clb_x + col * (self.clb_size + self.clb_channel_gap)
            y_io = 0
            io = patches.Rectangle((x_io, y_io), self.clb_size, self.clb_size,
                                   color=self.colors['IO'])
            self.ax.add_patch(io)
            self.ax.text(x_io + self.clb_size / 2, y_io + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

            # gornji IO
            y_io_top = start_clb_y + num_rows * (self.clb_size + self.clb_channel_gap)
            io_top = patches.Rectangle((x_io, y_io_top), self.clb_size, self.clb_size,
                                       color=self.colors['IO'])
            self.ax.add_patch(io_top)
            self.ax.text(x_io + self.clb_size / 2, y_io_top + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

        for row in range(num_rows):
            # levi IO
            x_io_left = 0
            y_io_left = start_clb_y + row * (self.clb_size + self.clb_channel_gap)
            io_left = patches.Rectangle((x_io_left, y_io_left), self.clb_size, self.clb_size,
                                        color=self.colors['IO'])
            self.ax.add_patch(io_left)
            self.ax.text(x_io_left + self.clb_size / 2, y_io_left + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

            # desni IO
            x_io_right = start_clb_x + num_cols * (self.clb_size + self.clb_channel_gap)
            io_right = patches.Rectangle((x_io_right, y_io_left), self.clb_size, self.clb_size,
                                         color=self.colors['IO'])
            self.ax.add_patch(io_right)
            self.ax.text(x_io_right + self.clb_size / 2, y_io_left + self.clb_size / 2, 'IO',
                         ha='center', va='center', color='black', fontweight='bold')

    def draw_io_clb_channels(self, num_rows, num_cols, start_clb_x, start_clb_y):
        # donji io i clb kanali
        for col in range(num_cols):
            x_io_bottom = start_clb_x + col * (self.clb_size + self.clb_channel_gap)
            channel_y = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
            self.draw_channels(x_io_bottom, channel_y, self.io_size, is_horizontal=True)

        # gornji io i clb kanali
        for col in range(num_cols):
            x_io_top = start_clb_x + col * (self.clb_size + self.clb_channel_gap)
            y_io_top = start_clb_y + num_rows * (self.clb_size + self.clb_channel_gap)
            channel_y = y_io_top - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
            self.draw_channels(x_io_top, channel_y, self.io_size, is_horizontal=True)

        # levi io i clb kanali
        for row in range(num_rows):
            y_io_left = start_clb_y + row * (self.clb_size + self.clb_channel_gap)
            channel_x = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
            self.draw_channels(channel_x, y_io_left, self.io_size, is_horizontal=False)

        # desni io i clb kanali
        for row in range(num_rows):
            y_io_right = start_clb_y + row * (self.clb_size + self.clb_channel_gap)
            x_io_right = start_clb_x + num_cols * (self.clb_size + self.clb_channel_gap)
            channel_x = x_io_right - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
            self.draw_channels(channel_x, y_io_right, self.io_size, is_horizontal=False)

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

    # popravljeno, radi za sada
    def map_rrg_to_grid(self, rrg: RRG, num_rows=6, num_cols=6):
        self.coord_map = {}
        self.num_rows = num_rows
        self.num_cols = num_cols

        start_clb_x = self.io_size + self.io_clb_gap
        start_clb_y = self.io_size + self.io_clb_gap

        cell_w = self.clb_size + self.clb_channel_gap
        cell_h = self.clb_size + self.clb_channel_gap

        # unutrašnji offset kanala (isti koji koristiš u draw_fpga_grid)
        channel_x_inner_offset = (self.clb_channel_gap / 2) - (self.channel_width / 2)
        channel_y_inner_offset = (self.clb_channel_gap / 2) - (self.channel_width / 2)

        for node in rrg.nodes.values():
            try:
                vx, vy = self.calculate_node_position(node, start_clb_x, start_clb_y)
            except Exception:
                vx = vy = None

            if vx is not None and vy is not None:
                self.coord_map[node.id] = (vx, vy)
                continue

            # fallback — eksplicitna mapiranja koja repliciraju draw_* logiku
            if node.type not in ['CHANX', 'CHANY']:
                # CLB/IPIN/OPIN/SOURCE/SINK: koristi centar CLB polja
                # (RRG xlow/ylow su 1-based za CLB polja — zato -1)
                visual_x = start_clb_x + (node.xlow - 1) * cell_w + self.clb_size / 2
                visual_y = start_clb_y + (node.ylow - 1) * cell_h + self.clb_size / 2

            elif node.type == 'CHANX':
                # IO<->CLB horizontalni kanali (ylow == 0 ili ylow == num_rows)
                if node.ylow == 0 or node.ylow == self.num_rows:
                    coord = self.calculate_io_clb_channel_position(node, start_clb_x, start_clb_y)
                    if coord is not None:
                        self.coord_map[node.id] = coord
                    continue

                # horizontalni kanal između redova CLB
                # Centar kanala je na sredini CLB širine (x) i na odgovarajućoj y poziciji kanala
                x_base = start_clb_x + (node.xlow - 1) * cell_w
                y_channel = start_clb_y + (node.ylow - 1) * cell_h + self.clb_size + channel_y_inner_offset
                # Stavimo CHANX tačku u centar horizontalnog segmenta (sredina CLB širine)
                visual_x = x_base + self.clb_size / 2
                visual_y = y_channel + node.ptc * self.channel_spacing

            elif node.type == 'CHANY':
                # IO<->CLB vertikalni kanali (xlow == 0 ili xlow == num_cols)
                if node.xlow == 0 or node.xlow == self.num_cols:
                    coord = self.calculate_io_clb_channel_position(node, start_clb_x, start_clb_y)
                    if coord is not None:
                        self.coord_map[node.id] = coord
                    continue

                # vertikalni kanal između kolona CLB
                # Centar kanala je na sredini CLB visine (y) i na odgovarajućoj x poziciji kanala
                x_channel = start_clb_x + (node.xlow - 1) * cell_w + self.clb_size + channel_x_inner_offset
                y_base = start_clb_y + (node.ylow - 1) * cell_h
                visual_x = x_channel + node.ptc * self.channel_spacing
                visual_y = y_base + self.clb_size / 2

            else:
                continue

            self.coord_map[node.id] = (visual_x, visual_y)

    def calculate_node_position(self, node, start_clb_x, start_clb_y):
        if node.type in ['SOURCE', 'SINK', 'OPIN', 'IPIN']:
            # offset +1 po koordinatama
            if 1 <= node.xlow <= self.num_cols and 1 <= node.ylow <= self.num_rows:
                visual_x = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)
                visual_y = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)

                # na centar bloka
                visual_x += self.clb_size / 2
                visual_y += self.clb_size / 2

                return visual_x, visual_y

        elif node.type in ['CHANX', 'CHANY']:
            # odvojeno ovde se resava offset
            return self.calculate_channel_position(node, start_clb_x, start_clb_y)

        elif node.type == 'IO':
            # odvojeno ovde se resava offset
            return self.calculate_io_position(node, start_clb_x, start_clb_y)

        return None, None

    def calculate_channel_position(self, node, start_clb_x, start_clb_y):
        # moramo proveriti da li su ovo kanali izmedju clb blokova
        if (node.type == 'CHANX' and (node.ylow == 0 or node.ylow == self.num_rows)) or \
                (node.type == 'CHANY' and (node.xlow == 0 or node.xlow == self.num_cols)):
            return self.calculate_io_clb_channel_position(node, start_clb_x, start_clb_y)

        # horizontalni kanali
        if node.type == 'CHANX':
            if 1 <= node.ylow < self.num_rows:
                # osnovna y pozicija
                y_pos = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap) + self.clb_size
                y_pos += (self.clb_channel_gap / 2) - (self.channel_width / 2)

                x_pos = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)


                track_offset = node.ptc * self.channel_spacing
                return x_pos, y_pos + track_offset

        # vertikalni kanali
        elif node.type == 'CHANY':
            if 1 <= node.xlow < self.num_cols:
                # osnovna x pozicija
                x_pos = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap) + self.clb_size
                x_pos += (self.clb_channel_gap / 2) - (self.channel_width / 2)

                # osnovna y pozicija
                y_pos = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)

                track_offset = node.ptc * self.channel_spacing
                return x_pos + track_offset, y_pos

        return None, None

    # ovde je sve zbog offseta opet stavljeno da se krece od 0,0 pozicije..
    def calculate_io_position(self, node, start_clb_x, start_clb_y):
        # donji io red (ylow = 0, yhigh = 0)
        if node.ylow == 0 and node.yhigh == 0:
            x_io = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)
            return x_io + self.clb_size / 2, self.io_size / 2

        # gornji io red (ylow = num_rows, yhigh = num_rows)
        elif node.ylow == self.num_rows and node.yhigh == self.num_rows:
            x_io = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)
            y_io_top = start_clb_y + self.num_rows * (self.clb_size + self.clb_channel_gap)
            return x_io + self.clb_size / 2, y_io_top + self.io_size / 2

        # levi io red (xlow = 0, xhigh = 0)
        elif node.xlow == 0 and node.xhigh == 0:
            y_io_left = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)
            return self.io_size / 2, y_io_left + self.clb_size / 2

        # desni io red (xlow = num_cols, xhigh = num_cols)
        elif node.xlow == self.num_cols and node.xhigh == self.num_cols:
            x_io_right = start_clb_x + self.num_cols * (self.clb_size + self.clb_channel_gap)
            y_io_right = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)
            return x_io_right + self.io_size / 2, y_io_right + self.clb_size / 2

        return None, None

    def calculate_io_clb_channel_position(self, node, start_clb_x, start_clb_y):
        # horizontani kanali
        if node.type == 'CHANX':
            # gornji
            if node.ylow == 0:
                y_pos = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
                x_base = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)

                track_offset = node.ptc * self.channel_spacing
                return x_base, y_pos + track_offset
            # donji
            elif node.ylow == self.num_rows:
                y_io_top = start_clb_y + self.num_rows * (self.clb_size + self.clb_channel_gap)
                y_pos = y_io_top - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
                x_base = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)

                track_offset = node.ptc * self.channel_spacing
                return x_base, y_pos + track_offset

        # vertikalni kanali
        elif node.type == 'CHANY':
            # levi
            if node.xlow == 0:
                x_pos = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
                y_base = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)

                track_offset = node.ptc * self.channel_spacing
                return x_pos + track_offset, y_base

            # desni
            elif node.xlow == self.num_cols:
                x_io_right = start_clb_x + self.num_cols * (self.clb_size + self.clb_channel_gap)
                x_pos = x_io_right - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
                y_base = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)

                track_offset = node.ptc * self.channel_spacing
                return x_pos + track_offset, y_base

        return None, None

    # samo debug da vidim jel sve lepo, mozemo kasnije obrisati
    def debug_coordinate_mapping(self, rrg: RRG):

        io_clb_count = 0
        total_count = 0

        for node_id, node in rrg.nodes.items():
            visual_x, visual_y = self.calculate_node_position(
                node, self.io_size + self.io_clb_gap, self.io_size + self.io_clb_gap
            )

            # samo proveravamo da li su kanali izmedju io i clb blokova
            if visual_x is not None and visual_y is not None:
                is_io_clb_channel = False
                if node.type in ['CHANX', 'CHANY']:
                    if (node.ylow == 0 or node.ylow == self.num_rows or
                            node.xlow == 0 or node.xlow == self.num_cols):
                        is_io_clb_channel = True
                        io_clb_count += 1

                self.ax.scatter(visual_x, visual_y, color='red', s=20, zorder=20)
                total_count += 1

    def debug_io_nodes(self, rrg: RRG):
        print("IO:")
        for node_id, node in rrg.nodes.items():
            if node.type == 'IO':
                print(
                    f"Node {node_id}: type={node.type}, xlow={node.xlow}, xhigh={node.xhigh}, ylow={node.ylow}, yhigh={node.yhigh}")

    # ovo izignorisite, naknadno cu samo prepraviti, nije bitno
    def draw_detailed_legend(self):
        legend_elements = []

        # Prvo dodajemo source i sink cvorove rute na vrh legende
        legend_elements.extend([
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightblue', markersize=8,
                       label='SOURCE - Početni čvor rute(node_id)', markeredgecolor='black'),
            plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='lightgreen', markersize=8,
                       label='SINK - Krajnji čvor rute(node_id)', markeredgecolor='black'),
            plt.Line2D([0], [0], color='black', lw=2,
                       label='Ruta signala'),
            plt.Line2D([0], [0], marker='v', color='black', markersize=6,
                       label='Putanja rute', linestyle='None')
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