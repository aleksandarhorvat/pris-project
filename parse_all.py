from fpga_project.parser_rrg import RRGParser
from fpga_project.parser_route import RouteParser
from fpga_project.fpga_matrix import FPGAMatrix
from fpga_project.fpga_routing import FPGARouting
from fpga_project.fpga_wires import FPGAWires


def main():
    rrpParser = RRGParser()
    rrpParser.parse("b9/rrg.xml")
    rrg = rrpParser.get_rrg()

    parser = RouteParser()
    parser.parse("b9/b9.route")
    #parser.parse("b9/iteration_005.route")
    route_data = parser.get_route()

    #branching_factor = 2
    

    # zbog nasledjivanja koristimo routing a ne matrix
    # visualizer = FPGARouting()
    # visualizer.visualize_matrix(rrg)
    # visualizer.debug_coordinate_mapping(rrg)
    # visualizer.debug_io_nodes(rrg)
    # visualizer.show()

    if route_data.nets:
        success, result = visualizer.get_signals_with_largest_bboxes(rrg, route_data, top_n=5)
        if not success:
            print("Greska")
            return
        visualizer.visualize_largest_bboxes(result)

        net_id = list(route_data.nets.keys())[1]
        net = route_data.nets[net_id]=    # if route_data.nets:
    #     net_id = list(route_data.nets.keys())[1]
    #     net = route_data.nets[net_id]

    #     routing_path = [node.id for node in net.nodes]

        # visualizer.visualize_routing_on_grid(rrg, routing_path, net_id)

        hpwl_results = visualizer.hpwl_all_signals(rrg, route_data)
        visualizer.save_hpwl(hpwl_results)

    #     #visualizer.visualize_routing_on_grid(rrg, routing_path, net_id)

    # visualizer.visualize_routing_by_branching(rrg,route_data, branching_factor)
    # visualizer.save("proba.pdf", format='pdf')
    # visualizer.save("proba.png", format='png')

    # visualizer.save("grananje2.png", format='png')


    #visualizer.show()

    # zagusenje segmenta
    visualizer_segments = FPGAWires()
    visualizer_segments.visualize_matrix(rrg)
    
    if route_data.nets:
        visualizer_segments.visualize_wire_congestion(route_data, rrg, 0)
    
    visualizer_segments.save("zagusenje_finalno.png",format='png')
    #visualizer_segments.save("zagusenje_iteracija_005.png",format='png')
    visualizer_segments.show()
    
if __name__ == "__main__":
    main()