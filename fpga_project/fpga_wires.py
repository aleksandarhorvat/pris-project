import matplotlib.cm as cm
import matplotlib.patches as mpatches
from .fpga_matrix import FPGAMatrix
from .models import RRG


class FPGAWires(FPGAMatrix):

    def __init__(self):
        super().__init__()

    def visualize_wire_congestion(self, rrg, route, iteration):
        # izdvojimo sve zice (CHANX/CHANY cvorove)
        wires = {node.id: node for node in rrg.nodes.values() if node.type in [
            'CHANX', 'CHANY']}

        # brojanje zagusenja po zicama
        wire_load = {wire_id: 0 for wire_id in wires.keys()}
        wire_signals = {wire_id: set()
                        for wire_id in wires.keys()}  # set za signale po zici

        for net_id, net in route.nets.items():
            # svaki wire u ruti signala evidentiramo samo jednom
            wire_ids = set(node.id for node in net.nodes if node.type in [
                           'CHANX', 'CHANY'])
            for wire_id in wire_ids:
                if net_id not in wire_signals[wire_id]:
                    wire_signals[wire_id].add(net_id)
                    wire_load[wire_id] += 1  # brojimo signal samo jednom

        max_load = max(wire_load.values()) if wire_load else 1

        # crtanje zagusenja na matrici
        for wire_id, load in wire_load.items():
            x, y = self.coord_map.get(wire_id, (None, None))
            if x is None or y is None:
                continue
            color = cm.Blues(load / max_load)
            self.ax.scatter(
                x, y,
                color=[color],
                edgecolors='gray',
                linewidths=1,
                s=20,
                zorder=10
            )

            node_type = rrg.nodes[wire_id].type

            # podesavanje offseta za tip zice
            offset = 0.101

            if node_type == 'CHANX':
                text_x = x - offset
                text_y = y
                ha = 'right'
                va = 'center'
            elif node_type == 'CHANY':
                text_x = x
                text_y = y - offset
                ha = 'center'
                va = 'top'

            self.ax.text(text_x, text_y, str(load), ha=ha,
                         va=va, fontsize=6, color='black')

        # naslov figure
        if iteration == 0:
            self.ax.set_title("Zagušenje po žicama - Finalna iteracija")
        else:
            self.ax.set_title(
                "Zagušenje po žicama - Iteracija broj " + str(iteration))

        # vracamo i mapu signala po žici ako bude potrebno
        return wire_signals

    def visualize_segment_wire_usage(self, rrg, route, iteration):
        # Dobavi wire_load iz visualize_wire_congestion logike
        wires = [node for node in rrg.nodes.values() if node.type in ['CHANX', 'CHANY']]
        wire_load = {wire.id: 0 for wire in wires}
        for net_id, net in route.nets.items():
            wire_ids = set(node.id for node in net.nodes if node.type in ['CHANX', 'CHANY'])
            for wire_id in wire_ids:
                wire_load[wire_id] += 1

        # Grupisi zice po koordinatama (segmentima)
        segment_wires = {}
        for wire in wires:
            coord = self.get_segment_coord(wire)
            if coord is None:
                continue
            if coord not in segment_wires:
                segment_wires[coord] = []
            segment_wires[coord].append(wire.id)

        # Za svaki segment prebroji zice sa wire_load > 0
        segment_usage = {}
        for coord, wire_ids in segment_wires.items():
            used_count = sum(1 for wid in wire_ids if wire_load[wid] > 0)
            total_count = len(wire_ids)
            segment_usage[coord] = (used_count, total_count)

        # Vizualizuj na gridu
        for coord, (used, total) in segment_usage.items():
            x, y = coord
            wire_ids = segment_wires[coord]
            wire_type = rrg.nodes[wire_ids[0]].type if wire_ids else 'CHANX'
            
            # IO kanali detektuj po xlow/ylow (ako imas pristup node-u)
            io_channel = False
            node = rrg.nodes[wire_ids[0]]
            num_rows = getattr(self, 'num_rows', 6)
            num_cols = getattr(self, 'num_cols', 6)
            if wire_type == 'CHANX' and (node.ylow == 0 or node.ylow == num_rows):
                io_channel = True
            if wire_type == 'CHANY' and (node.xlow == 0 or node.xlow == num_cols):
                io_channel = True

            if wire_type == 'CHANX':
                if io_channel:
                    # IO horizontalni kanal: pomeri tekst iznad i centriraj
                    rect_x = x - self.clb_size / 2 + 0.25
                    rect_y = y - self.channel_width / 2 + 0.4
                    rect_w = self.clb_size
                    rect_h = self.channel_width
                    text_x = x + 0.25
                    text_y = y + 0.25
                    ha = 'center'
                    va = 'bottom'
                else:
                    # CLB horizontalni kanal: više gore i malo levo
                    rect_x = x - self.clb_size / 2
                    rect_y = y - self.channel_width / 2 + 0.4
                    rect_w = self.clb_size
                    rect_h = self.channel_width
                    text_x = x
                    text_y = y + 0.25
                    ha = 'center'
                    va = 'bottom'
            elif wire_type == 'CHANY':
                if io_channel:
                    # IO vertikalni kanal: pomeri tekst desno i centriraj
                    rect_x = x - self.channel_width / 2 + 0.45
                    rect_y = y - self.clb_size / 2 + 0.25
                    rect_w = self.channel_width
                    rect_h = self.clb_size
                    text_x = x + 0.2
                    text_y = y + 0.25
                    ha = 'left'
                    va = 'center'
                else:
                    # CLB vertikalni kanal: desno od segmenta
                    rect_x = x - self.channel_width / 2 + 0.45
                    rect_y = y - self.clb_size / 2
                    rect_w = self.channel_width
                    rect_h = self.clb_size
                    text_x = x + 0.18
                    text_y = y
                    ha = 'left'
                    va = 'center'
            else:
                text_x = x
                text_y = y
                ha = 'center'
                va = 'center'

            usage_ratio = used / total if total else 0
            color = cm.Reds(usage_ratio)
            
            rect = mpatches.Rectangle(
                (rect_x, rect_y),
                rect_w, rect_h,
                linewidth=0, edgecolor=None,
                facecolor=color, alpha=0.38, zorder=6
            )
            self.ax.add_patch(rect)
            
            self.ax.text(
                text_x, text_y,
                f"{used}/{total}",
                ha=ha, va=va,
                fontsize=14, color='black', fontweight='bold'
            )

        if iteration == 0:
            self.ax.set_title("Broj zauzetih žica po segmentu - Finalna iteracija")
        else:
            self.ax.set_title(f"Broj zauzetih žica po segmentu - Iteracija broj {iteration}")

        return segment_usage
    
    def get_segment_coord(self, node):
        num_rows = getattr(self, 'num_rows', 6)
        num_cols = getattr(self, 'num_cols', 6)
        start_clb_x = self.io_size + self.io_clb_gap
        start_clb_y = self.io_size + self.io_clb_gap
        cell_w = self.clb_size + self.clb_channel_gap
        cell_h = self.clb_size + self.clb_channel_gap
        channel_x_inner_offset = (self.clb_channel_gap / 2) - (self.channel_width / 2)
        channel_y_inner_offset = (self.clb_channel_gap / 2) - (self.channel_width / 2)

        if node.type == 'CHANX':
            if node.ylow == 0 or node.ylow == num_rows:
                # IO<->CLB horizontalni kanali
                # koristi koordinate bez ptc offseta!
                if node.ylow == 0:
                    y_pos = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
                    x_base = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)
                    return (x_base, y_pos)
                elif node.ylow == num_rows:
                    y_io_top = start_clb_y + num_rows * (self.clb_size + self.clb_channel_gap)
                    y_pos = y_io_top - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
                    x_base = start_clb_x + (node.xlow - 1) * (self.clb_size + self.clb_channel_gap)
                    return (x_base, y_pos)
                return None
            x_base = start_clb_x + (node.xlow - 1) * cell_w
            y_channel = start_clb_y + (node.ylow - 1) * cell_h + self.clb_size + channel_y_inner_offset
            visual_x = x_base + self.clb_size / 2
            visual_y = y_channel
            return (visual_x, visual_y)
        elif node.type == 'CHANY':
            if node.xlow == 0 or node.xlow == num_cols:
                # IO<->CLB vertikalni kanali
                # koristi koordinate bez ptc offseta!
                if node.xlow == 0:
                    x_pos = self.io_size + (self.io_clb_gap / 2) - (self.channel_width / 2)
                    y_base = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)
                    return (x_pos, y_base)
                elif node.xlow == num_cols:
                    x_io_right = start_clb_x + num_cols * (self.clb_size + self.clb_channel_gap)
                    x_pos = x_io_right - self.io_clb_gap + (self.io_clb_gap / 2) - (self.channel_width / 2)
                    y_base = start_clb_y + (node.ylow - 1) * (self.clb_size + self.clb_channel_gap)
                    return (x_pos, y_base)
                return None
            x_channel = start_clb_x + (node.xlow - 1) * cell_w + self.clb_size + channel_x_inner_offset
            y_base = start_clb_y + (node.ylow - 1) * cell_h
            visual_x = x_channel
            visual_y = y_base + self.clb_size / 2
            return (visual_x, visual_y)
        return None
