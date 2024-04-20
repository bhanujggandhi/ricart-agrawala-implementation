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


def add_node_to_file(config, new_node_id, new_node_host, new_node_port):
    """
    Method to add new node to the config file
    """
    with open(config, "r+", encoding='utf-8') as file:
        lines = file.readlines()
        if not any(f"{new_node_id} {new_node_host} {new_node_port}\n" in line for line in lines):
            file.write(f"{new_node_id} {new_node_host} {new_node_port}\n")


def remove_node_from_file(config, node_id, ip, port):
    """
    Remove the node entry from the file
    """
    node_entry = f"{node_id} {ip} {port}"
    with open(config, "r+", encoding='utf-8') as file:
        lines = file.readlines()
        file.seek(0)
        for line in lines:
            if node_entry not in line.strip():
                file.write(line)
        file.truncate()
