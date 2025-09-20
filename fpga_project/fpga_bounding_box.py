import math
import matplotlib.patches as patches
from .fpga_routing import FPGARouting
from .models import RRG
import matplotlib.cm as cm
import matplotlib.patches as mpatches

class FPGABoundingBox(FPGARouting):
    def __init__(self):
        super().__init__()

    def calculate_terminal_bounding_box_area(self, routing_path, rrg, include_padding=True, padding=0.4):
        if not hasattr(self, "coord_map"):
            raise RuntimeError(
                "coord_map missing; call visualize_matrix(rrg) or map_rrg_to_grid(rrg) first")

        # Pronađi samo SOURCE i SINK čvorove u ruti
        terminal_nodes = [
            n for n in routing_path
            if n in self.coord_map and getattr(rrg.nodes[n], "type", None) in ("SOURCE", "SINK")
        ]
        if not terminal_nodes:
            return {
                "area_cells_ceil": 0
            }

        coords = [self.coord_map[n] for n in terminal_nodes]
        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        width_no_pad = max_x - min_x
        height_no_pad = max_y - min_y

        pad = padding if include_padding else 0.0
        width_mpl = width_no_pad + 2 * pad
        height_mpl = height_no_pad + 2 * pad

        cell_w = self.clb_size + self.clb_channel_gap
        cell_h = self.clb_size + self.clb_channel_gap

        if cell_w == 0 or cell_h == 0:
            raise RuntimeError(
                "Invalid clb_size or clb_channel_gap (would divide by zero)")

        width_cells = width_mpl / cell_w
        height_cells = height_mpl / cell_h

        area_cells_ceil = math.ceil(width_cells) * math.ceil(height_cells)

        return {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "area_cells_ceil": area_cells_ceil
        }

    def visualize_terminal_bounding_box(self, rrg: RRG, routing_path, net_id=None, color="blue"):
        # Prvo nacrtaj signal kao i do sada
        self.visualize_routing_on_grid(rrg, routing_path, net_id)

        # Izračunaj bounding box oko terminala
        metrics = self.calculate_terminal_bounding_box_area(
            routing_path, rrg, include_padding=True, padding=0.4)
        min_x = metrics["min_x"]
        max_x = metrics["max_x"]
        min_y = metrics["min_y"]
        max_y = metrics["max_y"]

        rect = patches.Rectangle(
            (min_x - 0.4, min_y - 0.4),
            (max_x - min_x) + 0.8,
            (max_y - min_y) + 0.8,
            linewidth=2,
            edgecolor=color,
            facecolor="none",
            alpha=0.9,
            zorder=10
        )
        self.ax.add_patch(rect)

        label_area = f"{metrics['area_cells_ceil']} cells"
        label = f"Net {net_id} terminals, {label_area}" if net_id is not None else label_area
        self.ax.text(min_x, max_y + 0.5, label, fontsize=8,
                     color=color, ha="left", va="bottom", zorder=11)

        return metrics

    def visualize_top_n_terminal_bounding_box_nets(self, rrg: RRG, route_data, n=1):
        """
        Prikaži n najvećih terminal bounding boxova (samo SOURCE i SINK čvorovi).
        """
        if not route_data.nets:
            print("⚠️ No nets found in route_data.")
            return None

        colors = ["blue", "orange", "green", "purple", "brown", "magenta", "cyan", "olive", "black", "red"]

        net_metrics = []
        for net_id, net in route_data.nets.items():
            routing_path = [node.id for node in net.nodes]
            metrics = self.calculate_terminal_bounding_box_area(routing_path, rrg)
            net_metrics.append((net_id, metrics))

        net_metrics.sort(key=lambda x: x[1]["area_cells_ceil"], reverse=True)

        results = []
        for i, (net_id, metrics) in enumerate(net_metrics[:n]):
            color = colors[i % len(colors)]
            print(f"{i + 1}. Net {net_id} - Terminal bounding box area: {metrics['area_cells_ceil']} cells")
            routing_path = [node.id for node in route_data.nets[net_id].nodes]
            self.visualize_terminal_bounding_box(rrg, routing_path, net_id=net_id, color=color)
            results.append({"net_id": net_id, "metrics": metrics})

        return results

    def calculate_bounding_box_area(self, routing_path, include_padding=True, padding=0.4):
        if not hasattr(self, "coord_map"):
            raise RuntimeError(
                "coord_map missing; call visualize_matrix(rrg) or map_rrg_to_grid(rrg) first")

        coords = [self.coord_map[n]
                  for n in routing_path if n in self.coord_map]
        if not coords:
            return {
                "area_cells_ceil": 0
            }

        xs, ys = zip(*coords)
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # sizes in matplotlib units
        width_no_pad = max_x - min_x
        height_no_pad = max_y - min_y

        pad = padding if include_padding else 0.0
        width_mpl = width_no_pad + 2 * pad
        height_mpl = height_no_pad + 2 * pad

        area_mpl = width_mpl * height_mpl

        # convert to CLB grid units (cell width/height)
        cell_w = self.clb_size + self.clb_channel_gap
        cell_h = self.clb_size + self.clb_channel_gap

        # protect against zero cell size
        if cell_w == 0 or cell_h == 0:
            raise RuntimeError(
                "Invalid clb_size or clb_channel_gap (would divide by zero)")

        width_cells = width_mpl / cell_w
        height_cells = height_mpl / cell_h

        area_cells_ceil = math.ceil(width_cells) * math.ceil(height_cells)

        return {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "area_cells_ceil": area_cells_ceil  # povrsina
        }

    def visualize_signal_with_bounding_box(self, rrg: RRG, routing_path, net_id=None, color="red"):
        # draw signal first
        self.visualize_routing_on_grid(rrg, routing_path, net_id)

        # compute bbox
        metrics = self.calculate_bounding_box_area(
            routing_path, include_padding=True, padding=0.4)
        min_x = metrics["min_x"]
        max_x = metrics["max_x"]
        min_y = metrics["min_y"]
        max_y = metrics["max_y"]

        rect = patches.Rectangle(
            (min_x - 0.4, min_y - 0.4),
            (max_x - min_x) + 0.8,
            (max_y - min_y) + 0.8,
            linewidth=2,
            edgecolor=color,
            facecolor="none",
            alpha=0.9,
            zorder=10
        )
        self.ax.add_patch(rect)

        label_area = f"{metrics['area_cells_ceil']} cells"
        label = f"Net {net_id}, {label_area}" if net_id is not None else label_area
        self.ax.text(min_x, max_y + 0.5, label, fontsize=8,
                     color=color, ha="left", va="bottom", zorder=11)

        return metrics

    def visualize_top_n_bounding_box_nets(self, rrg: RRG, route_data, n=1):
        """
        Prikaži n najvećih bounding boxova (po celoj ruti).
        """
        if not route_data.nets:
            print("⚠️ No nets found in route_data.")
            return None

        colors = ["red", "blue", "green", "orange", "purple", "brown", "magenta", "cyan", "olive", "black"]

        net_metrics = []
        for net_id, net in route_data.nets.items():
            routing_path = [node.id for node in net.nodes]
            metrics = self.calculate_bounding_box_area(routing_path)
            net_metrics.append((net_id, metrics))

        # Sort by area (descending) and take the top n
        net_metrics.sort(key=lambda x: x[1]["area_cells_ceil"], reverse=True)

        results = []
        for i, (net_id, metrics) in enumerate(net_metrics[:n]):
            color = colors[i % len(colors)]
            print(f"{i + 1}. Net {net_id} - Bounding box area: {metrics['area_cells_ceil']} cells")
            routing_path = [node.id for node in route_data.nets[net_id].nodes]
            self.visualize_signal_with_bounding_box(rrg, routing_path, net_id=net_id, color=color)
            results.append({"net_id": net_id, "metrics": metrics})

        return results
    
    def visualize_segment_terminal_bbox_overlap(self, rrg, route_data):
        # 1. Izračunaj terminal bounding box za svaki net
        terminal_bboxes = []
        for net_id, net in route_data.nets.items():
            routing_path = [node.id for node in net.nodes]
            bbox = self.calculate_terminal_bounding_box_area(routing_path, rrg)
            # ignoriši prazne bboxove
            if bbox["area_cells_ceil"] > 0:
                terminal_bboxes.append(bbox)
    
        # 2. Pripremi segmente kao u visualize_segment_wire_usage
        wires = [node for node in rrg.nodes.values() if node.type in ['CHANX', 'CHANY']]
        segment_wires = {}
        for wire in wires:
            coord = self.get_segment_coord(wire)
            if coord is None:
                continue
            if coord not in segment_wires:
                segment_wires[coord] = []
            segment_wires[coord].append(wire.id)
    
        # 3. Za svaki segment, prebroj koliko bboxova ga pokriva
        segment_overlap = {}
        for coord in segment_wires:
            x, y = coord
            overlap_count = 0
            for bbox in terminal_bboxes:
                # bbox granice
                min_x = bbox["min_x"] - 0.4
                max_x = bbox["max_x"] + 0.4
                min_y = bbox["min_y"] - 0.4
                max_y = bbox["max_y"] + 0.4
                if (min_x <= x <= max_x) and (min_y <= y <= max_y):
                    overlap_count += 1
            segment_overlap[coord] = overlap_count
    
        # 4. Heatmap vizualizacija kao u visualize_segment_wire_usage
        max_overlap = max(segment_overlap.values()) if segment_overlap else 1
        for coord, overlap in segment_overlap.items():
            x, y = coord
            wire_ids = segment_wires[coord]
            wire_type = rrg.nodes[wire_ids[0]].type if wire_ids else 'CHANX'
    
            # IO kanali detektuj po xlow/ylow (ako imaš pristup node-u)
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
                    text_x = x + 0.25
                    text_y = y + 0.25
                    ha = 'left'
                    va = 'center'
                else:
                    # CLB vertikalni kanal: desno od segmenta
                    rect_x = x - self.channel_width / 2 + 0.45
                    rect_y = y - self.clb_size / 2
                    rect_w = self.channel_width
                    rect_h = self.clb_size
                    text_x = x + 0.25
                    text_y = y
                    ha = 'left'
                    va = 'center'
            else:
                text_x = x
                text_y = y
                ha = 'center'
                va = 'center'
    
            # Boja prema broju preklapanja
            color = cm.Oranges(overlap / max_overlap if max_overlap else 0)
            rect = mpatches.Rectangle(
                (rect_x, rect_y),
                rect_w, rect_h,
                linewidth=0, edgecolor=None,
                facecolor=color, alpha=0.5, zorder=6
            )
            self.ax.add_patch(rect)
    
            # Ispiši broj preklapanja
            if overlap > 0:
                self.ax.text(
                    text_x, text_y,
                    str(overlap),
                    ha=ha, va=va,
                    fontsize=14, color='black', fontweight='bold'
                )
    
        self.ax.set_title("Vizualiacija broja preklapanja bounding box-ova na segmentima")
        
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