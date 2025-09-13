import math
import matplotlib.patches as patches
from .fpga_routing import FPGARouting
from .models import RRG


class FPGABoundingBox(FPGARouting):
    def __init__(self):
        super().__init__()

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

    def visualize_signal_with_bounding_box(self, rrg: RRG, routing_path, net_id=None):
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
            edgecolor="red",
            facecolor="none",
            alpha=0.9,
            zorder=10
        )
        self.ax.add_patch(rect)

        label_area = f"{metrics['area_cells_ceil']} cells"

        label = f"Net {net_id}, {label_area}" if net_id is not None else label_area
        self.ax.text(min_x, max_y + 0.5, label, fontsize=8,
                     color="red", ha="left", va="bottom", zorder=11)

        return metrics


    def visualize_largest_bounding_box_net(self, rrg: RRG, route_data):
        """
        Go through all nets, find the one with the largest bounding box area,
        draw its routing + bounding box, and return its info.
        """
        if not route_data.nets:
            print("⚠️ No nets found in route_data.")
            return None

        max_net_id = None
        max_area = -1
        max_metrics = None

        for net_id, net in route_data.nets.items():
            routing_path = [node.id for node in net.nodes]
            metrics = self.calculate_bounding_box_area(routing_path)

            if metrics["area_cells_ceil"] > max_area:
                max_area = metrics["area_cells_ceil"]
                max_net_id = net_id
                max_metrics = metrics

        if max_net_id is None:
            print("⚠️ No valid bounding boxes found.")
            return None

        print(f"Net with largest bounding box area: {max_net_id}")
        print(f"Bounding box area: {max_area} cells")

        # visualize the winning net
        routing_path = [node.id for node in route_data.nets[max_net_id].nodes]
        self.visualize_signal_with_bounding_box(rrg, routing_path, net_id=max_net_id)

        return {
            "net_id": max_net_id,
            "metrics": max_metrics
        }