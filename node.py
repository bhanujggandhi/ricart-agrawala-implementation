"""
Node.py
"""

from colorama import Fore, Style
from constants import CS_TIME_RANGE_END, CS_TIME_RANGE_START, HEARTBEAT_TIME, logger
import random
import socket
import threading
import time
from utils import add_node_to_file, load_config, remove_node_from_file


class Node:
    """
    Class representing a node (Machine) in a distributed system
    """

    def __init__(self, node_id):
        self.server_thread = None
        self.node_id = node_id
        self.config = f"config{node_id}.txt"
        self.nodes, self.host, self.port = load_config(self.config, self.node_id)
        self._initiate_heartbeat()
        self.heartbeat_sockets = {}
        self.timestamp = 0
        self.executing_cs = False
        self.interested_cs = False
        self.request_ts = -1
        self.deferred_list = []
        self.waiting_for_reply = set()

    def start_server(self):
        """
        Method to launch a server thread
        """
        self.server_thread = threading.Thread(target=self._server)
        self.server_thread.start()

    def _server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(1)
            print(
                Style.DIM
                + f"\nServer listening on {self.host}:{self.port}"
                + Style.RESET_ALL
            )
            while True:
                client_socket, client_addr = server_socket.accept()
                # print(f"Connection from {client_addr}")
                threading.Thread(
                    target=self._handle_client, args=(client_socket,)
                ).start()

    def _handle_client(self, client_socket: socket.socket):
        retry = 5
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    message = data.decode("utf-8")
                    message = message.split("~")
                    if message[0] == "HEARTBEAT":
                        logger.info("Received HEARTBEAT from node_id %s", message[1])
                    else:
                        self.timestamp = max(self.timestamp, int(message[-1])) + 1
                        # print(
                        #     f"Received message: {message[0]} from {message[1]}")
                    response = self._process_message(message)

                    if response is not None:
                        client_socket.sendall(response.encode("utf-8"))
                except ConnectionResetError:
                    retry -= 1
                    print(
                        Style.DIM
                        + Fore.RED
                        + "\nConnection reset by peer"
                        + Style.RESET_ALL
                    )
                    if retry == 0:
                        break
            # print("Client disconnected")

    def _process_message(self, message):
        response = None
        if message[0] == "HEARTBEAT":
            response = f"HEARTBEAT_REPLY~{self.node_id}"
        elif message[0] == "NEW_NODE":
            new_node_id, new_node_host, new_node_port, _ = message[1:]
            self._handle_new_node(int(new_node_id), new_node_host, int(new_node_port))
            response = f"New node added successfully.~{self.timestamp}"
        elif message[0] == "CSENTRY":
            if self.executing_cs or (
                self.interested_cs and self.request_ts < int(message[-1])
            ):
                self.deferred_list.append(int(message[1]))
                print(
                    Style.BRIGHT
                    + Fore.LIGHTRED_EX
                    + f"\nDeferred entry request from {message[1]} at {self.timestamp}"
                )
                response = f"DEFERRED~{self.node_id}~{self.timestamp}"
            else:
                self.timestamp += 1
                print(Style.BRIGHT + Fore.GREEN + f"\nCSREPLY sent to {message[1]}")
                response = f"CSREPLY~{self.node_id}~{self.timestamp}"
        elif message[0] == "CSREPLY":
            # time.sleep(0.7)
            self.timestamp += 1
            response = f"GOTIT~{self.timestamp}"
            print(
                Style.BRIGHT
                + Fore.YELLOW
                + f"\nReceived response: CSREPLY from {message[1]} at Timestamp: {self.timestamp} "
            )
            self.waiting_for_reply.discard(int(message[1]))
            self._start_cs_thread()
        else:
            self.timestamp += 1
            response = f"Didn't get you~{self.timestamp}"
        return response

    # ==========================
    # ADDITION/FAILURE HANDLE
    # ==========================
    def _handle_new_node(self, new_node_id, new_node_host, new_node_port):
        self.nodes[new_node_id] = (new_node_host, int(new_node_port))
        add_node_to_file(self.config, new_node_id, new_node_host, new_node_port)
        print(
            Style.BRIGHT
            + Fore.CYAN
            + f"\nNew node added: Node ID {new_node_id} - {new_node_host}:{new_node_port}"
        )

    def remove_node(self, node_id):
        """
        Remove node if it has stop working
        """
        node_id = int(node_id)
        if node_id in self.deferred_list:
            self.deferred_list.remove(node_id)
        if self.interested_cs and node_id in self.waiting_for_reply:
            self.waiting_for_reply.discard(node_id)
            self._start_cs_thread()
        if node_id in self.heartbeat_sockets:
            heartbeat_socket = self.heartbeat_sockets.pop(node_id)
            heartbeat_socket.close()
        remove_node_from_file(
            self.config, node_id, self.nodes[node_id][0], self.nodes[node_id][1]
        )
        self.nodes.pop(node_id)

    # =========================
    # CRITICAL SECTION
    # =========================
    def enter_cs(self):
        """
        Method to handle the critical section requested by the client
        """
        if self.executing_cs:
            print(Style.BRIGHT + Fore.RED + "\nAlready executing CS")
            return

        if self.interested_cs:
            print(Style.BRIGHT + Fore.RED + "\nAlready requested for a CS")
            return

        self.interested_cs = True
        self.request_ts = self.timestamp
        self.waiting_for_reply = set(self.nodes.keys())
        self.waiting_for_reply.discard(self.node_id)
        self.broadcast(f"CSENTRY~{self.node_id}~{self.timestamp}")
        self._start_cs_thread()

    def _start_cs_thread(self):
        if not self.executing_cs and len(self.waiting_for_reply) == 0:
            self.executing_cs = True
            cs_thread = threading.Thread(target=self._execute_cs)
            cs_thread.start()

    def _execute_cs(self):
        time_for_cs = random.randint(CS_TIME_RANGE_START, CS_TIME_RANGE_END)
        print(Style.BRIGHT + Fore.GREEN + f"\nExecuting CS for {time_for_cs} seconds")
        time.sleep(time_for_cs)
        print(Style.BRIGHT + Fore.GREEN + "\nDone with CS")
        self._exit_cs()

    def _exit_cs(self):
        self.executing_cs = False
        self.interested_cs = False
        self.waiting_for_reply = set(self.nodes.keys())
        self._send_reply_to_deferred()
        self.deferred_list = []

    def _send_reply_to_deferred(self):
        if len(self.deferred_list) > 0:
            print(
                Style.BRIGHT
                + Fore.LIGHTGREEN_EX
                + f"\nSending replies to deferred nodes {self.deferred_list}"
            )
            time.sleep(0.7)
            for node_id in self.deferred_list:
                self.send_message(node_id, f"CSREPLY~{self.node_id}~{self.timestamp}")

    # ===============================
    # MESSAGING
    # ===============================

    def send_message(self, node_id: int, message: str):
        """
        Method to handle message sending for a client
        """
        target_host, target_port = self.nodes[node_id]
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((target_host, target_port))
                self.timestamp += 1
                client_socket.sendall(f"{message}~{self.timestamp}".encode("utf-8"))
                response = client_socket.recv(1024).decode("utf-8")
                response = response.split("~")
                if response[0] not in ["DEFERRED", "GOTIT"]:
                    print(
                        Style.BRIGHT
                        + Fore.YELLOW
                        + f"\nReceived response: {response[0]} from {response[1]}"
                        f" at Timestamp: {response[-1]}"
                    )
                if response[0] == "CSREPLY":
                    self.waiting_for_reply.discard(int(response[1]))
                    self.timestamp = max(self.timestamp, int(response[-1])) + 1
                    self._start_cs_thread()
            except Exception:
                print(
                    Style.DIM
                    + Fore.RED
                    + f"\nCould not connect to {target_host} and {target_port}"
                    + Style.RESET_ALL
                )

    def broadcast(self, message: str):
        """
        Method to handle broadcasting message to all the clients in the system
        """
        print(
            Style.BRIGHT
            + Fore.CYAN
            + f"\nSending broadcast message to {list(self.nodes.keys())}"
        )
        for node_id in self.nodes:
            if node_id == self.node_id:
                continue
            self.send_message(node_id, message)

    # =======================
    # HEARTBEAT
    # =======================
    def _initiate_heartbeat(self):
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def _send_heartbeat(self):
        while True:
            time.sleep(HEARTBEAT_TIME)
            with open(self.config, "r", encoding="utf-8") as file:
                for line in file:
                    node_info = line.strip().split()
                    if len(node_info) != 3:
                        continue
                    if int(node_info[0]) == self.node_id:
                        continue
                    try:
                        self.send_heartbeat(int(node_info[0]))
                    except Exception as e:
                        print(
                            Style.DIM
                            + Fore.RED
                            + f"\nError sending heartbeat to {node_info[0]} at"
                            f" {node_info[1]} :{node_info[2]}: {e}" + Style.RESET_ALL
                        )
                        print(
                            Style.BRIGHT
                            + Fore.RED
                            + f"Removing node {node_info[0]} from the config"
                        )
                        self.remove_node(node_info[0])

    def send_heartbeat(self, node_id):
        """
        Send heartbeat to all other nodes
        """
        if node_id in self.heartbeat_sockets:
            heartbeat_socket = self.heartbeat_sockets[node_id]
        else:
            heartbeat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            target_host, target_port = self.nodes[node_id]
            heartbeat_socket.connect((target_host, target_port))
            self.heartbeat_sockets[node_id] = heartbeat_socket
        heartbeat_socket.sendall(f"HEARTBEAT~{self.node_id}".encode("utf-8"))

    def _handle_heartbeat(self, node_id):
        # Handle heartbeat from sender node

        logger.debug(
            "Heartbeat received from %s at %s:%s",
            node_id,
            self.nodes[node_id][0],
            self.nodes[node_id][1],
        )
