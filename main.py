"""
Runner Script
"""

from colorama import Fore
import logging
from node import Node


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
        print(Fore.LIGHTBLUE_EX + "1. Enter Critical Section")
        print(Fore.LIGHTBLUE_EX + "2. Print Data Structures")
        print(Fore.LIGHTBLUE_EX + "3. Exit")
        choice = input("Enter your choice: ")

        if choice == "1":
            node.enter_cs()
        elif choice == "2":
            print(f"Node ID: {node.node_id}")
            print(f"Timestamp: {node.timestamp}")
            # print(f"Heartbeat Dict: {node.heartbeat_sockets}")
            print(f"Interested CS: {node.interested_cs}")
            print(f"Executing CS: {node.executing_cs}")
            print(f"Request TS: {node.request_ts}")
            print(f"Deferred List: {node.deferred_list}")
            print(f"Waiting for Reply: {node.waiting_for_reply}")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
