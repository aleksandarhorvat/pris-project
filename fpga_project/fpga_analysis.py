import math
from collections import defaultdict


from fpga_project.fpga_bounding_box import FPGABoundingBox
from fpga_project.models import RRG


class FPGARoutingAnalysis(FPGABoundingBox):
    def __init__(self):
        super().__init__()


    def hpwl_all_signals(self, rrg: RRG, route):

        hpwl_results = {}

        for net_id, net in route.nets.items():

            nodes = net.nodes
            x_coords, y_coords = [], []

            for node in nodes:
                if node.id in self.coord_map:
                    x, y = self.coord_map[node.id]
                    x_coords.append(x)
                    y_coords.append(y)
                else:
                    try:
                        start_clb_x = self.io_size + self.io_clb_gap
                        start_clb_y = self.io_size + self.io_clb_gap
                        x, y = self.calculate_node_position(node, start_clb_x, start_clb_y)

                        if x is not None and y is not None:
                            x_coords.append(x)
                            y_coords.append(y)
                            self.coord_map[node.id] = (x, y)
                    except:
                        print(f"Nije moguce dobiti koordinatu za cvor {node.id}")
                        continue

            if x_coords and y_coords:
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                hpwl = (x_max - x_min) + (y_max - y_min)
                hpwl_results[net_id] = hpwl
            else:
                hpwl_results[net_id] = 0
                print(f"Signal {net_id} nema validnih koordinata")

        return hpwl_results

    def save_hpwl(self, hpwl_results, filename="hpwl_metrika.txt"):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("HPWL METRIKA\n")
                f.write("*" * 25 + "\n")

                total_hpwl = 0
                for net_id, hpwl in hpwl_results.items():
                    f.write(f"Signal {net_id}: HPWL = {hpwl:.2f}\n")
                    total_hpwl += hpwl

                avg_hpwl = total_hpwl / len(hpwl_results) if hpwl_results else 0
                max_hpwl = max(hpwl_results.values()) if hpwl_results else 0
                min_hpwl = min(hpwl_results.values()) if hpwl_results else 0

                f.write("\n" + "*" * 25 + "\n")
                f.write(f"Ukupan HPWL: {total_hpwl:.2f}\n")
                f.write(f"Prosečan HPWL: {avg_hpwl:.2f}\n")
                f.write(f"Maksimalni HPWL: {max_hpwl:.2f}\n")
                f.write(f"Minimalni HPWL: {min_hpwl:.2f}\n")
                f.write("*" * 25 + "\n")

            print(f"HPWL metrike su sačuvane u fajl: {filename}")

        except Exception as e:
            print(f"Greška pri snimanju HPWL metrika u fajl: {e}")


    def calculate_real_wire_usage(self, rrg: RRG, route_data):

        wire_usage = {}

        for net_id, net in route_data.nets.items():
            # Brojimo sve CHANX i CHANY čvorove u ruti (žice)
            wire_count = sum(1 for node in net.nodes if node.type in ['CHANX', 'CHANY'])
            wire_usage[net_id] = wire_count

        return wire_usage

    def calculate_deviation_metrics(self, rrg: RRG, route_data):

        # Izračunaj HPWL za sve signale
        hpwl_results = self.hpwl_all_signals(rrg, route_data)

        # Izračunaj stvarnu dužinu rute za sve signale
        real_wire_usage = self.calculate_real_wire_usage(rrg, route_data)

        # Izračunaj odstupanje za svaki signal
        deviation_metrics = {}

        for net_id in hpwl_results.keys():
            if net_id in real_wire_usage:
                hpwl = hpwl_results[net_id]
                real = real_wire_usage[net_id]

                # Apsolutno odstupanje
                absolute_deviation = real - hpwl

                # Relativno odstupanje (procenat)
                relative_deviation = (absolute_deviation / hpwl) * 100 if hpwl > 0 else 0

                deviation_metrics[net_id] = {
                    'hpwl': hpwl,
                    'real_wires': real,
                    'absolute_deviation': absolute_deviation,
                    'relative_deviation': relative_deviation
                }

        return deviation_metrics

    def print_deviation_analysis(self, rrg: RRG, route_data, n=10):

        deviation_metrics = self.calculate_deviation_metrics(rrg, route_data)

        print("\n" + "=" * 80)
        print("ANALIZA ODSTUPANJA RUTA OD HPWL METRIKE")
        print("=" * 80)

        # Ukupne statistike
        total_signals = len(deviation_metrics)
        total_absolute_dev = sum(m['absolute_deviation'] for m in deviation_metrics.values())
        total_relative_dev = sum(m['relative_deviation'] for m in deviation_metrics.values())
        avg_absolute_dev = total_absolute_dev / total_signals if total_signals > 0 else 0
        avg_relative_dev = total_relative_dev / total_signals if total_signals > 0 else 0

        print(f"Ukupan broj signala: {total_signals}")
        print(f"Prosečno apsolutno odstupanje: {avg_absolute_dev:.2f}")
        print(f"Prosečno relativno odstupanje: {avg_relative_dev:.2f}%")
        print("-" * 80)

        # Sortiraj po apsolutnom odstupanju
        sorted_by_absolute = sorted(
            deviation_metrics.items(),
            key=lambda x: x[1]['absolute_deviation'],
            reverse=True
        )

        print(f"\nTOP {n} SIGNALA PO APSOLUTNOM ODSTUPANJU:")
        print("-" * 60)
        for i, (net_id, metrics) in enumerate(sorted_by_absolute[:n]):
            print(f"{i + 1:2d}. Net {net_id:4d}: HPWL={metrics['hpwl']:6.2f}, "
                  f"Žice={metrics['real_wires']:3d}, "
                  f"Aps.dev={metrics['absolute_deviation']:6.2f}, "
                  f"Rel.dev={metrics['relative_deviation']:6.2f}%")

        # Sortiraj po relativnom odstupanju
        sorted_by_relative = sorted(
            deviation_metrics.items(),
            key=lambda x: x[1]['relative_deviation'],
            reverse=True
        )

        print(f"\nTOP {n} SIGNALA PO RELATIVNOM ODSTUPANJU:")
        print("-" * 60)
        for i, (net_id, metrics) in enumerate(sorted_by_relative[:n]):
            print(f"{i + 1:2d}. Net {net_id:4d}: HPWL={metrics['hpwl']:6.2f}, "
                  f"Žice={metrics['real_wires']:3d}, "
                  f"Aps.dev={metrics['absolute_deviation']:6.2f}, "
                  f"Rel.dev={metrics['relative_deviation']:6.2f}%")

        print("=" * 80)

    def save_deviation_analysis(self, rrg: RRG, route_data, filename="hpwl_odstupanje_analiza.txt", n = 10):

        deviation_metrics = self.calculate_deviation_metrics(rrg, route_data)

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("ANALIZA ODSTUPANJA RUTA OD HPWL METRIKE\n")
                f.write("=" * 80 + "\n\n")

                # Ukupne statistike
                total_signals = len(deviation_metrics)
                total_absolute_dev = sum(m['absolute_deviation'] for m in deviation_metrics.values())
                total_relative_dev = sum(m['relative_deviation'] for m in deviation_metrics.values())
                avg_absolute_dev = total_absolute_dev / total_signals if total_signals > 0 else 0
                avg_relative_dev = total_relative_dev / total_signals if total_signals > 0 else 0

                f.write(f"Ukupan broj signala: {total_signals}\n")
                f.write(f"Prosečno apsolutno odstupanje: {avg_absolute_dev:.2f}\n")
                f.write(f"Prosečno relativno odstupanje: {avg_relative_dev:.2f}%\n")
                f.write("-" * 80 + "\n\n")

                # Sortiraj po apsolutnom odstupanju
                sorted_by_absolute = sorted(
                    deviation_metrics.items(),
                    key=lambda x: x[1]['absolute_deviation'],
                    reverse=True
                )

                f.write(f"\nTOP {n} SIGNALA PO APSOLUTNOM ODSTUPANJU:\n\n")
                f.write("-" * 80 + "\n\n")
                for i, (net_id, metrics) in enumerate(sorted_by_absolute[:n]):
                    f.write(f"{i + 1:2d}. Net {net_id:4d}: HPWL={metrics['hpwl']:6.2f}, "
                          f"Žice={metrics['real_wires']:3d}, "
                          f"Aps.dev={metrics['absolute_deviation']:6.2f}, "
                          f"Rel.dev={metrics['relative_deviation']:6.2f}%\n")

                f.write("\n")

                # Sortiraj po relativnom odstupanju
                sorted_by_relative = sorted(
                    deviation_metrics.items(),
                    key=lambda x: x[1]['relative_deviation'],
                    reverse=True
                )

                f.write(f"\nTOP {n} SIGNALA PO RELATIVNOM ODSTUPANJU:\n\n")
                f.write("-" * 80 + "\n\n")
                for i, (net_id, metrics) in enumerate(sorted_by_relative[:n]):
                    f.write(f"{i + 1:2d}. Net {net_id:4d}: HPWL={metrics['hpwl']:6.2f}, "
                          f"Žice={metrics['real_wires']:3d}, "
                          f"Aps.dev={metrics['absolute_deviation']:6.2f}, "
                          f"Rel.dev={metrics['relative_deviation']:6.2f}%\n")

                f.write("\n" + "=" * 80 + "\n")

                # Detaljan pregled svih signala
                f.write("\nDETALJAN PREGLED SVIH SIGNALA:\n")
                f.write("=" * 80 + "\n")

                f.write("\nSignali sortirani po apsolutnom odstupanju:\n")
                f.write("-" * 80 + "\n")
                for net_id, metrics in sorted_by_absolute:
                    f.write(f"Net {net_id}: HPWL={metrics['hpwl']:.2f}, "
                            f"Žice={metrics['real_wires']}, "
                            f"Aps.dev={metrics['absolute_deviation']:.2f}, "
                            f"Rel.dev={metrics['relative_deviation']:.2f}%\n")

                f.write("\n\nSignali sortirani po relativnom odstupanju:\n")
                f.write("-" * 80 + "\n")
                for net_id, metrics in sorted_by_relative:
                    f.write(f"Net {net_id}: HPWL={metrics['hpwl']:.2f}, "
                            f"Žice={metrics['real_wires']}, "
                            f"Aps.dev={metrics['absolute_deviation']:.2f}, "
                            f"Rel.dev={metrics['relative_deviation']:.2f}%\n")

            print(f"Analiza odstupanja je sačuvana u fajl: {filename}")

        except Exception as e:
            print(f"Greška pri snimanju analize odstupanja: {e}")