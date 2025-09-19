import math
import matplotlib.patches as patches
from .fpga_routing import FPGARouting
from .models import RRG


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