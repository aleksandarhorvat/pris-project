from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.visualizer_FPGA import FPGAVisualizer


def main():
    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg = rrpParser.get_rrg()
    # print(rrpParser.get_rrg())

    parser = RouteParser()
    parser.parse("b9/b9.route")
    route = parser.get_route()
    # print(parser.get_route())


    print("Visualization: ")
    visualizer = FPGAVisualizer()

    visualizer.visualize_fpga_matrix(rrg)
    # visualizer.save("architecture_only.pdf", format="pdf")
    # print("Arhitektura pdf sacuvan")

    visualizer.visualize_routing(rrg, route)
    # visualizer.save("with_routing.pdf", format="pdf")
    # print("Ruta pdf sacuvan")

    visualizer.show()


if __name__ == "__main__":
    main()
