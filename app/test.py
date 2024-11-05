# test_graph_operations.py
import asyncio
from database import create_indexes

from crud import (
    create_graph, get_graph, update_graph, delete_graph,
    create_node, get_node, update_node, 
    create_edge, get_edge, delete_edge
)
from schemas import GraphSchema, NodeSchema, EdgeSchema

# Sample graph schema
# Example data fix for test_create_graph function

additional_nodes = [{
            "node_id": "node_F",
            "data_in": {"inputF": 6},
            "data_out": {"outputF": 7},
            "paths_in": [
                # {
                #     "edge_id": "edge_E_F",
                #     "src_node": "node_E",
                #     "dst_node": "node_F",
                #     "src_to_dst_data_keys": {"outputE": "inputF"}
                # }
            ],
            "paths_out": [
                # {
                #     "edge_id": "edge_C_D",
                #     "src_node": "node_C",
                #     "dst_node": "node_D",
                #     "src_to_dst_data_keys": {"outputC": "inputD"}
                # }
            ]
        }
]

additional_edges = [ {
                    "edge_id": "edge_F_A",
                    "src_node": "node_F",
                    "dst_node": "node_A",
                    "src_to_dst_data_keys": {"outputF": "inputA"}
                }
]

graph_data1 = {
    "graph_id": "graph_1",
    "name": "Linear Flow Graph",
    "description": "A simple linear data flow graph",
    "nodes": [
        {
            "node_id": "node_A",
            "data_in": {},
            "data_out": {"outputA": 1},
            "paths_in": [],
            "paths_out": [
                {
                    "edge_id": "edge_A_B",
                    "src_node": "node_A",
                    "dst_node": "node_B",
                    "src_to_dst_data_keys": {"outputA": "inputB"}
                }
            ]
        },
        {
            "node_id": "node_B",
            "data_in": {"inputB": 1},
            "data_out": {"outputB": 2},
            "paths_in": [
                {
                    "edge_id": "edge_A_B",
                    "src_node": "node_A",
                    "dst_node": "node_B",
                    "src_to_dst_data_keys": {"outputA": "inputB"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_B_C",
                    "src_node": "node_B",
                    "dst_node": "node_C",
                    "src_to_dst_data_keys": {"outputB": "inputC"}
                }
            ]
        },
        {
            "node_id": "node_C",
            "data_in": {"inputC": 2},
            "data_out": {"outputC": 3},
            "paths_in": [
                {
                    "edge_id": "edge_B_C",
                    "src_node": "node_B",
                    "dst_node": "node_C",
                    "src_to_dst_data_keys": {"outputB": "inputC"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_C_D",
                    "src_node": "node_C",
                    "dst_node": "node_D",
                    "src_to_dst_data_keys": {"outputC": "inputD"}
                }
            ]
        },
        {
            "node_id": "node_D",
            "data_in": {"inputD": 3},
            "data_out": {"outputD": 4},
            "paths_in": [
                {
                    "edge_id": "edge_C_D",
                    "src_node": "node_C",
                    "dst_node": "node_D",
                    "src_to_dst_data_keys": {"outputC": "inputD"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_D_E",
                    "src_node": "node_D",
                    "dst_node": "node_E",
                    "src_to_dst_data_keys": {"outputD": "inputE"}
                }
            ]
        },
        {
            "node_id": "node_E",
            "data_in": {"inputE": 4},
            "data_out": {"outputE": 5},
            "paths_in": [
                {
                    "edge_id": "edge_D_E",
                    "src_node": "node_D",
                    "dst_node": "node_E",
                    "src_to_dst_data_keys": {"outputD": "inputE"}
                }
            ],
            "paths_out": []
        }
    ],
    "edges": [
        {
            "edge_id": "edge_A_B",
            "src_node": "node_A",
            "dst_node": "node_B",
            "src_to_dst_data_keys": {"outputA": "inputB"}
        },
        {
            "edge_id": "edge_B_C",
            "src_node": "node_B",
            "dst_node": "node_C",
            "src_to_dst_data_keys": {"outputB": "inputC"}
        },
        {
            "edge_id": "edge_C_D",
            "src_node": "node_C",
            "dst_node": "node_D",
            "src_to_dst_data_keys": {"outputC": "inputD"}
        },
        {
            "edge_id": "edge_D_E",
            "src_node": "node_D",
            "dst_node": "node_E",
            "src_to_dst_data_keys": {"outputD": "inputE"}
        }
    ]
}

graph_data2 = {
    "graph_id": "jkll",
    "nodes": [
        {
            "node_id": "node_A1",
            "data_in": {},
            "data_out": {"outputA1": 1},
            "paths_in": [],
            "paths_out": [
                {
                    "edge_id": "edge_A1_B1",
                    "src_node": "node_A1",
                    "dst_node": "node_B1",
                    "src_to_dst_data_keys": {"outputA1": "inputB1"}
                },
                {
                    "edge_id": "edge_A1_C1",
                    "src_node": "node_A1",
                    "dst_node": "node_C1",
                    "src_to_dst_data_keys": {"outputA1": "inputC1"}
                },
                {
                    "edge_id": "edge_A1_D1",
                    "src_node": "node_A1",
                    "dst_node": "node_D1",
                    "src_to_dst_data_keys": {"outputA1": "inputD1"}
                }
            ]
        },
        {
            "node_id": "node_B1",
            "data_in": {"inputB1": 1},
            "data_out": {"outputB1": 2},
            "paths_in": [
                {
                    "edge_id": "edge_A1_B1",
                    "src_node": "node_A1",
                    "dst_node": "node_B1",
                    "src_to_dst_data_keys": {"outputA1": "inputB1"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_B1_E1",
                    "src_node": "node_B1",
                    "dst_node": "node_E1",
                    "src_to_dst_data_keys": {"outputB1": "inputE1"}
                }
            ]
        },
        {
            "node_id": "node_C1",
            "data_in": {"inputC1": 1},
            "data_out": {"outputC1": 3},
            "paths_in": [
                {
                    "edge_id": "edge_A1_C1",
                    "src_node": "node_A1",
                    "dst_node": "node_C1",
                    "src_to_dst_data_keys": {"outputA1": "inputC1"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_C1_E1",
                    "src_node": "node_C1",
                    "dst_node": "node_E1",
                    "src_to_dst_data_keys": {"outputC1": "inputE1"}
                }
            ]
        },
        {
            "node_id": "node_D1",
            "data_in": {"inputD1": 1},
            "data_out": {"outputD1": 4},
            "paths_in": [
                {
                    "edge_id": "edge_A1_D1",
                    "src_node": "node_A1",
                    "dst_node": "node_D1",
                    "src_to_dst_data_keys": {"outputA1": "inputD1"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_D1_F1",
                    "src_node": "node_D1",
                    "dst_node": "node_F1",
                    "src_to_dst_data_keys": {"outputD1": "inputF1"}
                }
            ]
        },
        {
            "node_id": "node_E1",
            "data_in": {"inputE1": 3},
            "data_out": {"outputE1": 5},
            "paths_in": [
                {
                    "edge_id": "edge_B1_E1",
                    "src_node": "node_B1",
                    "dst_node": "node_E1",
                    "src_to_dst_data_keys": {"outputB1": "inputE1"}
                },
                {
                    "edge_id": "edge_C1_E1",
                    "src_node": "node_C1",
                    "dst_node": "node_E1",
                    "src_to_dst_data_keys": {"outputC1": "inputE1"}
                }
            ],
            "paths_out": [
                {
                    "edge_id": "edge_E1_G1",
                    "src_node": "node_E1",
                    "dst_node": "node_G1",
                    "src_to_dst_data_keys": {"outputE1": "inputG1"}
                }
            ]
        },
        {
            "node_id": "node_F1",
            "data_in": {"inputF1": 4},
            "data_out": {"outputF1": 6},
            "paths_in": [
                {
                    "edge_id": "edge_D1_F1",
                    "src_node": "node_D1",
                    "dst_node": "node_F1",
                    "src_to_dst_data_keys": {"outputD1": "inputF1"}
                }
            ],
            "paths_out": []
        },
        {
            "node_id": "node_G1",
            "data_in": {"inputG1": 5},
            "data_out": {"outputG1": 7},
            "paths_in": [
                {
                    "edge_id": "edge_E1_G1",
                    "src_node": "node_E1",
                    "dst_node": "node_G1",
                    "src_to_dst_data_keys": {"outputE1": "inputG1"}
                }
            ],
            "paths_out": []
        }
    ],
    "edges": [
        {
            "edge_id": "edge_A1_B1",
            "src_node": "node_A1",
            "dst_node": "node_B1",
            "src_to_dst_data_keys": {"outputA1": "inputB1"}
        },
        {
            "edge_id": "edge_A1_C1",
            "src_node": "node_A1",
            "dst_node": "node_C1",
            "src_to_dst_data_keys": {"outputA1": "inputC1"}
        },
        {
            "edge_id": "edge_A1_D1",
            "src_node": "node_A1",
            "dst_node": "node_D1",
            "src_to_dst_data_keys": {"outputA1": "inputD1"}
        },
        {
            "edge_id": "edge_B1_E1",
            "src_node": "node_B1",
            "dst_node": "node_E1",
            "src_to_dst_data_keys": {"outputB1": "inputE1"}
        },
        {
            "edge_id": "edge_C1_E1",
            "src_node": "node_C1",
            "dst_node": "node_E1",
            "src_to_dst_data_keys": {"outputC1": "inputE1"}
        },
        {
            "edge_id": "edge_D1_F1",
            "src_node": "node_D1",
            "dst_node": "node_F1",
            "src_to_dst_data_keys": {"outputD1": "inputF1"}
        },
        {
            "edge_id": "edge_E1_G1",
            "src_node": "node_E1",
            "dst_node": "node_G1",
            "src_to_dst_data_keys": {"outputE1": "inputG1"}
        }
    ]
}

# Step 1: Create a Graph
def test_create_graph():
    graph = GraphSchema(**graph_data2)
    graph_id = create_graph(graph)
    assert graph_id, "Failed to create graph"
    print(f"Graph created with ID: {graph_id}")
    return graph_id

# Step 2: Add Nodes to the Graph
def test_add_nodes(graph_id, nodes):
    """
    Adds a list of nodes to the graph, including related edges, while checking consistency.
    Rolls back all changes if any inconsistency is detected. O(N) complexity.

    Args:
        graph_id (str): The ID of the graph to which nodes should be added.
        nodes (list): A list of NodeSchema instances representing the nodes to add.

    Returns:
        list: A list of IDs for the added nodes.
    Raises:
        Exception: If any inconsistency is detected, raises an exception and performs a rollback.
    """
    node_ids = []
    edge_ids = []
    rollback_operations = []

    try:
        # Step 1: Add each node and its edges
        for node in nodes:
            # Add the node
            node_id = create_node(node, graph_id)
            assert node_id, f"Failed to add node with ID: {node.node_id}"
            node_ids.append(node_id)
            rollback_operations.append(('node', graph_id, node_id))
            print(f"Node added with ID: {node_id}")

            # Add edges from paths_in and paths_out for the current node
            for edge in node['paths_in']:
                if edge['dst_node'] == node['node_id']:
                    edge_id = create_edge(edge, graph_id)
                    assert edge_id, f"Failed to add edge with ID: {edge['edge_id']}"
                    edge_ids.append(edge_id)
                    rollback_operations.append(('edge', graph_id, edge_id))
                    print(f"Edge added with ID: {edge_id}")
            
            for edge in node['paths_out']:
                if edge['src_node'] == node['node_id']:
                    edge_id = create_edge(edge, graph_id)
                    assert edge_id, f"Failed to add edge with ID: {edge['edge_id']}"
                    edge_ids.append(edge_id)
                    rollback_operations.append(('edge', graph_id, edge_id))
                    print(f"Edge added with ID: {edge_id}")

            # Validate the graph structure after each addition
            
        if not GraphSchema.validate_graph_structure(get_graph(graph_id).dict()):
            raise Exception("Graph structure invalid after adding node and edges.")

        print("All nodes and edges added successfully with graph consistency maintained.")
        return node_ids

    except Exception as e:
        print(f"Error occurred: {e}. Rolling back changes.")
        # Rollback all changes on inconsistency or error
        for item in rollback_operations:
            item_type, graph_id, item_id = item
            print(item_type)
            if item_type == 'node':
                print(item_id +"deleted")
                delete_node(item_id, graph_id)
            elif item_type == 'edge':
                print(item_id)
                delete_edge(item_id, graph_id)
        
        print("Graph consistency check failed; all changes reverted.")



# Step 3: Add Edges to the Graph
def test_add_edges(graph_id, edges):
    edge_ids = []
    for edge in edges:
        edge_id = create_edge(edge, graph_id)
        assert edge_id, "Failed to add edge"
        print(f"Edge added with ID: {edge_id}")
        edge_ids.append(edge_id)
    return edge_ids

# Step 4: Retrieve and Verify Graph
def test_get_graph(graph_id):
    graph = get_graph(graph_id)
    assert graph, "Failed to retrieve graph"
    assert graph["name"] == "Test Graph", "Graph name mismatch"
    print(f"Graph retrieved: {graph}")

# Step 5: Update a Node's Data
def test_update_node(graph_id, node_id):
    updated_data = {"data_in": {"input1": 10}}
    update_node(graph_id, node_id, updated_data)
    node = get_node(graph_id, node_id)
    assert node["data_in"]["input1"] == 10, "Failed to update node data_in"
    print(f"Node updated: {node}")

# Step 6: Delete Edge and Verify
def test_delete_edge(graph_id, edge_id):
    delete_edge(graph_id, edge_id)
    edge = get_edge(graph_id, edge_id)
    assert edge is None, "Failed to delete edge"
    print(f"Edge deleted with ID: {edge_id}")

# Step 7: Delete Node and Verify
def test_delete_node(graph_id, node_id):
    delete_node(graph_id, node_id)
    node = get_node(graph_id, node_id)
    assert node is None, "Failed to delete node"
    print(f"Node deleted with ID: {node_id}")

# Step 8: Delete Graph and Verify
def test_delete_graph(graph_id):
    delete_graph(graph_id)
    graph = get_graph(graph_id)
    assert graph is None, "Failed to delete graph"
    print(f"Graph deleted with ID: {graph_id}")

# Run all tests sequentially
def run_tests():
    create_indexes() # Connect to MongoDB
    
    
    print("Starting CRUD operation tests...")

    # Create graph
    graph_id = test_create_graph()
    print(graph_id)
    # Add nodes
    # node_ids = test_add_nodes("6720a9b6537074851f72f4c1", additional_nodes)
    # print(node_ids)
    # Add edge between nodes
    # edge_id = test_add_edges("6720a9b6537074851f72f4c1", additional_edges)

    # # Retrieve and verify the graph structure
    # test_get_graph(graph_id)

    # # Update a node and verify
    # test_update_node(graph_id, node_ids[0])

    # # Delete the edge and verify
    # test_delete_edge(graph_id, edge_id)

    # # Delete nodes and verify
    # test_delete_node(graph_id, node_ids[0])
    # test_delete_node(graph_id, node_ids[1])

    # # Delete the graph and verify
    # test_delete_graph("6720a75b853aba5bc60fc4a0")

    print("All CRUD operation tests completed successfully.")
    

if __name__ == "__main__":
    run_tests()
