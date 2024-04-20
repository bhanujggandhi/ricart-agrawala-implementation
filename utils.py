"""
Utils.py
"""


def load_config(config, current_node_id):
    """
    Loads config file
    FORMAT:
    <NODEID HOST PORT>
    """
    nodes = {}
    with open(config, "r", encoding='utf-8') as file:
        for line in file:
            node_info = line.strip().split()
            if len(node_info) != 3:
                continue
            node_id, host, port = node_info
            if int(node_id) == current_node_id:
                current_host = host
                current_port = int(port)
            nodes[int(node_id)] = (host, int(port))
    return nodes, current_host, current_port
