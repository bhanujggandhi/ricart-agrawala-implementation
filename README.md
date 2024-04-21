# Ricarta Agrawala Algorithm Implementation

| **Team No.**         | 42             |
| -------------------- | -------------- |
| Bhanuj Gandhi        | **2022201068** |
| Avishek Kumar Sharma | **2022202024** |

Python Implementation of Ricarata Agrawala Algorithm for mututal exclusion in a distributed system.

Reference Study: [Link](https://www.cs.ucf.edu/courses/cop6614/fall2005/Ricart-Agrawala.pdf)

## Implementation Details

1. There are N nodes in the system. Each node must have it's own config file. For simplicity I have fixed the config file name format to be `config<node id>.txt`
2. Each node is a **client** and a **server** in itself. Both of the thread listen indefinitely till the program terminates.
3. A node can request the critical section by pressing 1. Upon requesting, a request message is broadcasted to each node in the system. Upon receiving reply from all the nodes, this node will enter the critical section.
4. If a node is already executing the critical section or a node has requested the critical section before the requesting node, it will defer it's reply messages, and only after completing the critical section, it will send the reply to the deferred nodes.

### Node Addition

> When a node is added for the first time, it should have all the alive nodes information in the config file.

- Node can join the network using it's config file.
- When the node comes for the first time, it broadcast the message to every node that it has joined the message and based on the replies from each node, **it updates it's timestamp.**
- Every node adds an entry of the new node in their config file to make the system persistent.

### Node Failure

- Node failures are handled gracefully. We have **implemented the heartbeat messaged** which are sent after every fixed interval.
- In case the reply of the heartbeat is not received, the node is assumed to be dead and every node removes it's entry from all the _data structures used_ as well as the _config file_.
- All the deferred requests are assumed to be accepted in order to avoid the deadlock condition.
- Same node can enter the network, it will follow the same flow as addition of new node.

### Config file

Below is the sample config file

```
0 127.0.0.1 4000
1 127.0.0.1 4001
2 127.0.0.1 4002
3 127.0.0.1 4003

```

> Make sure to have an empty line in the end.

### Critical section

It is hard to estimate how much time a critical section will take. To add randomness, everytime a critical section is requested a random number between `CS_TIME_RANGE_START` and `CS_TIME_RANGE_END`. These parameters can be tweaked in `constants.py` file.

## Running the project

1. Install the required packages

```sh
pip install -r requirements.txt
```

2. Run the project

```sh
python main.py
```

3. You will be prompted to input the node id. The `HOST` and `PORT` will be taken from the config file.
4. Input 1 for the critical section request.
5. Input 2 to check all the data structures for a node in the system.
