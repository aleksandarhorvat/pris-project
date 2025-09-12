import matplotlib.cm as cm
from .fpga_matrix import FPGAMatrix
from .models import RRG


class FPGAWires(FPGAMatrix):
    """
    Vizualizuje zagušenje po pojedinačnoj žici (tracku) u FPGA (CHANX/CHANY).
    """

    def __init__(self):
        super().__init__()

    def visualize_wire_congestion(self, route, rrg, iteration):
        # izdvojimo sve žice (CHANX/CHANY čvorove)
        wires = {node.id: node for node in rrg.nodes.values() if node.type in [
            'CHANX', 'CHANY']}

        # brojanje zagušenja po žicama
        wire_load = {wire_id: 0 for wire_id in wires.keys()}
        wire_signals = {wire_id: set()
                        for wire_id in wires.keys()}  # set za signale po žici

        for net_id, net in route.nets.items():
            # svaki wire u ruti signala evidentiramo samo jednom
            wire_ids = set(node.id for node in net.nodes if node.type in [
                           'CHANX', 'CHANY'])
            for wire_id in wire_ids:
                if net_id not in wire_signals[wire_id]:
                    wire_signals[wire_id].add(net_id)
                    wire_load[wire_id] += 1  # brojimo signal samo jednom

        max_load = max(wire_load.values()) if wire_load else 1

        # crtanje zagušenja na matrici
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

            # podesavanje offseta za tip žice
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

        # vraćamo i mapu signala po žici ako bude potrebno
        return wire_signals
