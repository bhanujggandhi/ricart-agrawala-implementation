"""
Runner Script
"""

import logging
from node import Node
from colorama import Fore


def main():
    """
    Main function which handles the input for client
    """
    node_id = int(input("Enter the node id: "))
    # config_path = input("Enter the config file path: ")

    logging.basicConfig(
        filename=f"log_{node_id}.log", encoding="utf-8", level=logging.DEBUG
    )

    node = Node(node_id)
    node.start_server()

    node.broadcast(f"NEW_NODE~{node_id}~{node.host}~{node.port}")

    while True:
        print(Fore.LIGHTBLUE_EX + "\n1. Send message to specific node")
        print(Fore.LIGHTBLUE_EX + "2. Broadcast message to all nodes")
        print(Fore.LIGHTBLUE_EX + "3. Print Data Structures")
        print(Fore.LIGHTBLUE_EX + "4. Enter Critical Section")
        print(Fore.LIGHTBLUE_EX + "5. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            node_id = input("Enter node id: ")
            message = input("Enter message to send: ")
            node.send_message(int(node_id), message)
        elif choice == "2":
            message = input("Enter message to broadcast: ")
            node.broadcast(message)
        elif choice == "3":
            print(f"Node ID: {node.node_id}")
            print(f"Timestamp: {node.timestamp}")
            # print(f"Heartbeat Dict: {node.heartbeat_sockets}")
            print(f"Interested CS: {node.interested_cs}")
            print(f"Executing CS: {node.executing_cs}")
            print(f"Request TS: {node.request_ts}")
            print(f"Deferred List: {node.deferred_list}")
            print(f"Waiting for Reply: {node.waiting_for_reply}")
        elif choice == "4":
            node.enter_cs()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    main()
