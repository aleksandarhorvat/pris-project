from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.fpga_matrix import FPGAMatrix
from fpga_project.fpga_routing import FPGARouting
from fpga_project.fpga_wires import FPGAWires
from fpga_project.fpga_bounding_box import FPGABoundingBox


def main():
    rrg = parse_rrg()
    route_number = input("Unesi broj rute, 0 ako je finalna: ").strip()
    if route_number == "0":
        route_data = parse_route("b9/b9.route")
    else:
        route_data = parse_route(
            "b9/iteration_" + route_number.zfill(3) + ".route")

    print("Izaberi prikaz:")
    print("1 - Matrix")
    print("2 - Routing jednog signala")
    print("3 - Routing by branching")
    print("4 - Wire congestion")
    print("5 - Segment wire usage")
    print("6 - Bounding box jednog signala")
    print("7 - Terminal bounding box jednog signala")
    print("8 - Najveći bounding box-ovi")
    print("9 - Najveći terminal bounding box-ovi")
    print("10 - HPWL")
    print("11 - Prvih N signala")

    choice = input("Unesi broj prikaza: ").strip()

    if choice == "1":
        show_matrix(rrg)
    elif choice == "2":
        net_id = int(input("Unesi net_id za prikaz rute: "))
        net = route_data.nets[net_id]
        routing_path = [node.id for node in net.nodes]
        show_routing(rrg, routing_path, net_id)
    elif choice == "3":
        branching = int(input("Unesi faktor grananja: "))
        show_routing_by_branching(rrg, route_data, branching)
    elif choice == "4":
        show_wire_congestion(rrg, route_data, route_number)
    elif choice == "5":
        show_segment_wire_usage(rrg, route_data, route_number)
    elif choice == "6":
        net_id = int(input("Unesi net_id za bounding box: "))
        net = route_data.nets[net_id]
        routing_path = [node.id for node in net.nodes]
        show_bounding_boxes(rrg, routing_path, net_id)
    elif choice == "7":
        net_id = int(input("Unesi net_id za terminal bounding box: "))
        net = route_data.nets[net_id]
        routing_path = [node.id for node in net.nodes]
        show_terminal_bounding_boxes(rrg, routing_path, net_id)
    elif choice == "8":
        number = int(input("Unesi broj signala za prikaz: "))
        show_largest_bounding_boxes(rrg, route_data, number)
    elif choice == "9":
        number = int(input("Unesi broj signala za prikaz: "))
        show_largest_terminal_bounding_boxes(rrg, route_data, number)
    elif choice == "10":
        show_hpwl(rrg, route_data)
    elif choice == "11":
        number = int(input("Unesi broj signala za prikaz: "))
        show_first_n_signals(rrg, route_data, number)
    else:
        print("Nepoznata opcija.")


def save_img(visualizer):
    save_img = input(
        "Da li želite da sačuvate sliku kao PNG? (d/n): ").strip().lower()
    if save_img == "d":
        file_name = input("Unesite ime fajla (bez ekstenzije): ").strip()
        if not file_name.endswith(".png"):
            file_name += ".png"
        # Pronađi poslednji korišćen vizualizer
        # Pretpostavljamo da se zove 'visualizer' u svakoj funkciji
        try:
            visualizer.save(file_name)
            print(f"Slika je sačuvana kao {file_name}")
        except Exception:
            print("Nije moguće sačuvati sliku. Proveri da li je vizualizer dostupan.")


def parse_route(file_path: str):
    parser = RouteParser()
    parser.parse(file_path)
    route_data = parser.get_route()
    return route_data


def parse_rrg():
    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg = rrpParser.get_rrg()
    return rrg


def show_matrix(rrg):
    visualizer = FPGAMatrix()
    visualizer.visualize_matrix(rrg)
    save_img(visualizer)
    visualizer.show()


def show_routing(rrg, route_data, net_id):
    visualizer = FPGARouting()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_routing_on_grid(rrg, route_data, net_id)
    save_img(visualizer)
    visualizer.show()


def show_routing_by_branching(rrg, route_data, branching_factor):
    visualizer = FPGARouting()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_routing_by_branching(
        rrg, route_data, branching_factor)
    save_img(visualizer)
    visualizer.show()


def show_wire_congestion(rrg, route_data, iteration):
    visualizer = FPGAWires()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_wire_congestion(rrg, route_data, iteration)
    save_img(visualizer)
    visualizer.show()


def show_segment_wire_usage(rrg, route_data, iteration):
    visualizer = FPGAWires()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_segment_wire_usage(rrg, route_data, iteration)
    save_img(visualizer)
    visualizer.show()


def show_bounding_boxes(rrg, routing_path, net_id):
    visualizer = FPGABoundingBox()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_signal_with_bounding_box(rrg, routing_path, net_id)
    save_img(visualizer)
    visualizer.show()

def show_terminal_bounding_boxes(rrg, routing_path, net_id):
    visualizer = FPGABoundingBox()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_terminal_bounding_box(rrg, routing_path, net_id)
    save_img(visualizer)
    visualizer.show()

def show_largest_bounding_boxes(rrg, route_data, n):
    visualizer = FPGABoundingBox()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_top_n_bounding_box_nets(rrg, route_data, n)
    save_img(visualizer)
    visualizer.show()

def show_largest_terminal_bounding_boxes(rrg, route_data, n):
    visualizer = FPGABoundingBox()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)
    visualizer.visualize_top_n_terminal_bounding_box_nets(rrg, route_data, n)
    save_img(visualizer)
    visualizer.show()

def show_hpwl(rrg, route_data):
    visualizer = FPGARouting()
    visualizer.map_rrg_to_grid(rrg)
    results = visualizer.hpwl_all_signals(rrg, route_data)
    visualizer.save_hpwl(results)

def show_first_n_signals(rrg, route_data, number):
    visualizer = FPGARouting()
    visualizer.visualize_matrix(rrg)
    visualizer.map_rrg_to_grid(rrg)

    routing_paths = []
    for net_id, net in route_data.nets.items():
        routing_paths.append([node.id for node in net.nodes])

    visualizer.visualize_first_n_routings(rrg, routing_paths, number)

    save_img(visualizer)
    visualizer.show()

if __name__ == "__main__":
    main()
