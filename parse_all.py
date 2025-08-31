from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.visualizer_FPGA import FPGAVisualizer


def main():
    # rrpParser = RRGParser()
    # rrpParser.parse("b9/rrg.xml")
    # print(rrpParser.get_rrg())

    # parser = RouteParser()
    # parser.parse("b9/b9.route")
    # print(parser.get_route())

    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg_data = rrpParser.get_rrg()
    # print(rrpParser.get_rrg())

    parser = RouteParser()
    parser.parse("b9/b9.route")
    route_data = parser.get_route()
    # print(parser.get_route())

    visualizer = FPGAVisualizer()
    visualizer.visualize_fpga_matrix(rrg_data)

    net_id = 10
    fanout = 5
    visualizer.visualize_signal(route_data, net_id)
    # visualizer.visualize_signals_by_branching(route_data, fanout)

    # visualizer.save(f"netvisualization{netid}.png")
    # visualizer.save(f"fanout{fanout}.png")

    visualizer.show()


if __name__ == "__main__":
    main()
