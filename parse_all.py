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


    # Create visualizer
    visualizer = FPGAMatrix()

    visualizer.draw_fpga_grid(route_data)


    # for net_id, net in route_data.nets.items():
    #     print(f"Visualizing net {net_id} with {len(net.nodes)} nodes")
    #
    #     # Try different possible attribute names for the node ID
    #     try:
    #         # First try 'id' (most common)
    #         routing_path = [node.id for node in net.nodes]
    #     except AttributeError:
    #         try:
    #             # Then try 'node_id'
    #             routing_path = [node.node_id for node in net.nodes]
    #         except AttributeError:
    #             print(
    #                 f"Could not find ID attribute in Node objects. Available attributes: {dir(net.nodes[0]) if net.nodes else 'No nodes'}")
    #             continue
    #
    #     print(f"Routing path: {routing_path}")
    #
    #     # Visualize this specific net
    #     visualizer.visualize_routing_on_grid(rrg, routing_path, 6, 6)
    #
    #     # Save the visualization for this net
    #     # visualizer.save(f"net_{net_id}_visualization.png")
    #
    #     # Clear the visualizer for the next net
    #     visualizer.ax.clear()
    #
    #     # If you want to visualize just one net at a time
    # visualizer = FPGAMatrix()
    # if route_data.nets:
    #     first_net_id = list(route_data.nets.keys())[0]
    #     first_net = route_data.nets[first_net_id]
    #
    #     # Try to get the node IDs
    #     try:
    #         routing_path = [node.id for node in first_net.nodes]
    #     except AttributeError:
    #         try:
    #             routing_path = [node.node_id for node in first_net.nodes]
    #         except AttributeError:
    #             print("Cannot find node ID attribute. Printing node details:")
    #             for i, node in enumerate(first_net.nodes):
    #                 print(f"Node {i}: {dir(node)}")
    #             return
    #
    #     print(f"Visualizing net {first_net_id} with path: {routing_path}")
    #     visualizer.visualize_routing_on_grid(rrg, routing_path, 6, 6)
    #     visualizer.show()

    visualizer.show()

    # routing_visualizer.save(f"netvisualization{net_id}.png")
    # routing_visualizer.save(f"fanout{fanout}.png")


if __name__ == "__main__":
    main()