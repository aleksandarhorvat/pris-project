import matplotlib.cm as cm
from .fpga_matrix import FPGAMatrix
from .models import RRG

class FPGASegments(FPGAMatrix):
    def __init__(self):
        super().__init__()

    def visualize_congestion(self, route, rrg, iteration):
        # izdvojimo sve segmente
        segments = {node.id: node for node in rrg.nodes.values() if node.type in ['CHANX', 'CHANY']}
        
        # brojanje zagusenja po zicama (PTC) u svakom segmentu
        segment_ptc_signals = {seg_id: {} for seg_id in segments.keys()}  # {seg_id: {ptc: set_of_signals}}

        for net_id, net in route.nets.items():
            for node in net.nodes:
                if node.type in ['CHANX', 'CHANY'] and node.id in segments:
                    seg_id = node.id
                    ptc = node.ptc
                    
                    # inicijalizujemo set za ovaj PTC ako ne postoji
                    if ptc not in segment_ptc_signals[seg_id]:
                        segment_ptc_signals[seg_id][ptc] = set()
                    
                    # dodaj signal u ovaj PTC
                    segment_ptc_signals[seg_id][ptc].add(net_id)

        # pronalazimo maksimalno zagusenje po segmentu
        segment_max_congestion = {}
        for seg_id in segments.keys():
            if seg_id in segment_ptc_signals and segment_ptc_signals[seg_id]:
                max_signals = max(len(signals) for signals in segment_ptc_signals[seg_id].values())
                segment_max_congestion[seg_id] = max_signals
            else:
                segment_max_congestion[seg_id] = 0

        max_load = max(segment_max_congestion.values()) if segment_max_congestion else 1

        # crtanje zagusenja na matrici
        for seg_id, max_congestion in segment_max_congestion.items():
            x, y = self.coord_map.get(seg_id, (None, None))
            if x is None or y is None:
                continue
            color = cm.Blues(max_congestion / max_load)
            self.ax.scatter(
                x, y,
                color=[color],
                edgecolors='gray',
                linewidths=1,
                s=20,
                zorder=10
            )
            
            node_type = rrg.nodes[seg_id].type
            
            # podesavanje offseta za tip kanala
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

            self.ax.text(text_x, text_y, str(max_congestion), ha=ha, va=va, fontsize=6, color='black')
        
        # naslov figure
        if iteration == 0:
            self.ax.set_title("Zagušenje po segmentima - Finalna iteracija")
        else:
            self.ax.set_title("Zagušenje po segmentima - Iteracija broj " + str(iteration))
