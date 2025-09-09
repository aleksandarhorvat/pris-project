from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.fpga_matrix import FPGAMatrix
from fpga_project.fpga_routing import FPGARouting


def main():
    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg = rrpParser.get_rrg()

    parser = RouteParser()
    parser.parse("b9/b9.route")
    route_data = parser.get_route()


    # zbog nasledjivanja koristimo routing a ne matrix
    visualizer = FPGARouting()
    visualizer.visualize_matrix(rrg)
    # visualizer.debug_coordinate_mapping(rrg)
    # visualizer.debug_io_nodes(rrg)
    # visualizer.show()

    if route_data.nets:
        net_id = list(route_data.nets.keys())[1]
        net = route_data.nets[net_id]

        routing_path = [node.id for node in net.nodes]

        visualizer.visualize_routing_on_grid(rrg, routing_path, net_id)

    # visualizer.save("proba.pdf", format='pdf')
    visualizer.save("proba.png", format='png')


    visualizer.show()

if __name__ == "__main__":
    main()