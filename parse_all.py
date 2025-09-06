from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.fpga_matrix import FPGAMatrix
from fpga_project.fpga_routing import FPGARouting


def main():
    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg_data = rrpParser.get_rrg()

    parser = RouteParser()
    parser.parse("b9/b9.route")
    route_data = parser.get_route()

    matrix_visualizer = FPGAMatrix()
    matrix_visualizer.visualize_fpga_matrix(rrg_data)
    matrix_visualizer.show()

    # routing_visualizer = FPGARouting()
    # routing_visualizer.visualize_routing(rrg_data, route_data)
    # routing_visualizer.show()


    # routing_visualizer.save(f"netvisualization{net_id}.png")
    # routing_visualizer.save(f"fanout{fanout}.png")


if __name__ == "__main__":
    main()