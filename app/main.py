from fastapi import FastAPI, HTTPException
from schemas import GraphSchema, GraphRunConfig, NodeOutputRequest, LeafOutputRequest
from neo4j import GraphDatabase
from fastapi.responses import JSONResponse
from crud import (
    create_graph,
)
import json
from uuid import uuid4
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware




load_dotenv()


app = FastAPI()


neo4j_uri = os.getenv("neo4j_uri")
neo4j_user = os.getenv("neo4j_user")
neo4j_password = os.getenv("neo4j_password")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust according to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


#End point to get all the graphs

@app.get("/api/graphs")
async def get_all_graphs():
    """
     Time Complexity Analysis:
        Neo4j Query (Cypher): O(G), where V is the number of nodes with the label `Graph`, as it retrieves each `graph_id` node individually.
        Overall Algorithm: O(G), since the code iterates through all records to build the `graphs` list, where V is the number of `Graph` nodes.
    
      Space Complexity Analysis:
        O(V), as it stores the `graph_id` of each `Graph` node in the `graphs` list.
    """

    #Connecting to the Neo4j database
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    #Fetching all the graph_ids from the database
    with driver.session() as session:
        result = session.run("MATCH (g:Graph) RETURN g.graph_id AS graph_id")
        graphs = [{"graph_id": record["graph_id"]} for record in result]
    return graphs


# Endpoint to get a specific graph

@app.get("/api/graphs/{graph_id}")
async def get_graph(graph_id: str):
    # Time Complexity Analysis:
    # Neo4j Query (Cypher):
    #   - Nodes Query: O(V), where V is the number of nodes with the specified `graph_id` and valid `node_id`.
    #   - Edges Query: O(E), where E is the number of edges between nodes with the specified `graph_id`.
    # Overall Algorithm: O(V + E), as we need to retrieve both nodes and edges for the specified `graph_id`.
    #
    # Space Complexity Analysis:
    # O(V + E), where V is the number of nodes and E is the number of edges. Space is used to store `nodes_data` and `edges_data` lists.

    """
    Endpoint to retrieve graph data based on a specified graph ID.
    
    Args:
        graph_id (str): Unique identifier for the graph to be retrieved.
    
    Response:
        JSONResponse: A JSON object containing two main keys:
            - nodes: List of nodes in the graph, each with `id`, `data_in`, and `data_out`.
            - edges: List of edges between nodes, each with `src`, `dst`, and `src_to_dst_data_keys`.
    
    Purpose:
        This function connects to a Neo4j database to retrieve and structure graph data, 
        including nodes and edges, for use in front-end applications (e.g., ForceGraph3D).
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        # Fetch nodes with a valid node_id
        nodes_query = """
        MATCH (n {graph_id: $graph_id}) 
        WHERE n.node_id IS NOT NULL
        RETURN n.node_id AS node_id, n.data_in AS data_in, n.data_out AS data_out
        """
        nodes = session.run(nodes_query, {"graph_id": graph_id})
        
        # Convert nodes result to a list
        nodes_data = [
            {
                "id": record["node_id"],  # Use "id" for compatibility with ForceGraph3D
                "data_in": json.loads(record["data_in"]) if record["data_in"] else {},
                "data_out": json.loads(record["data_out"]) if record["data_out"] else {}
            }
            for record in nodes
        ]

        # Fetch edges
        edges_query = """
        MATCH (src {graph_id: $graph_id})-[r]->(dst {graph_id: $graph_id})
        WHERE src.node_id IS NOT NULL AND dst.node_id IS NOT NULL
        RETURN src.node_id AS src, dst.node_id AS dst, r.src_to_dst_data_keys AS src_to_dst_data_keys
        """
        edges = session.run(edges_query, {"graph_id": graph_id})
        
        # Convert edges result to a list
        edges_data = [
            {
                "src": record["src"],
                "dst": record["dst"],
                "src_to_dst_data_keys": json.loads(record["src_to_dst_data_keys"]) if record["src_to_dst_data_keys"] else {}
            }
            for record in edges
        ]
    
    # Return a structured response suitable for the frontend
    return JSONResponse(content={"nodes": nodes_data, "edges": edges_data})

@app.get("/output/{run_id}")
async def get_graph_output(run_id: str):
    # Time Complexity Analysis:
    # Neo4j Query (Cypher):
    #   - Nodes Query: O(V), where V is the number of nodes with the specified `run_id` in the `OUTPUT` relationship.
    #   - Edges Query: O(E), where E is the number of edges connecting nodes associated with the specified `run_id`.
    #   - Topo Order Query: O(1), since it only retrieves a single attribute (`topo_order`) from the `Run` node.
    # Overall Algorithm: O(V + E), as we retrieve both nodes and edges and a single value for `topo_order`.
    #
    # Space Complexity Analysis:
    # O(V + E), where V is the number of nodes and E is the number of edges. Space is used to store `nodes_data`, `edges_data`, and `topo_order`.

    """
    Endpoint to retrieve output data for all nodes and edges associated with a specified run ID.
    
    Args:
        run_id (str): Unique identifier for the run whose output data is to be retrieved.
    
    Response:
        JSON object containing:
            - run_id: The requested run ID.
            - topo_order: List of node IDs in topological order for the run.
            - nodes: List of nodes with fields `id`, `data_in`, and `data_out`.
            - edges: List of edges with fields `src`, `dst`, `edge_id`, and `src_to_dst_data_keys`.
    
    Purpose:
        This function connects to a Neo4j database to retrieve output data for nodes and edges
        based on a specific `run_id`, including topological order information for further processing.
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        # Query nodes based only on run_id
        nodes_result = session.run("""
            MATCH (n:Node)-[out:OUTPUT]->(r:Run {run_id: $run_id})
            RETURN n.node_id AS node_id, n.data_in AS data_in, n.data_out AS data_out
            """, {
                "run_id": run_id
            })

        # Collect nodes and output data
        nodes_data = [{"id": record["node_id"], "data_in": record["data_in"], "data_out": record["data_out"]} for record in nodes_result]

        if not nodes_data:
            raise HTTPException(status_code=404, detail="No output data found for the specified run_id.")

        # Query edges between nodes for this run_id
        edges_result = session.run("""
            MATCH (src:Node)-[e:EDGE]->(dst:Node),
                (src)-[:OUTPUT]->(r:Run {run_id: $run_id}),
                (dst)-[:OUTPUT]->(r)
            RETURN src.node_id AS src_id, dst.node_id AS dst_id, e.edge_id AS edge_id, e.src_to_dst_data_keys AS src_to_dst_data_keys
            """, {
                "run_id": run_id
            })

        # Collect edges data
        edges_data = [{
            "src": record["src_id"],
            "dst": record["dst_id"],
            "edge_id": record["edge_id"],
            "src_to_dst_data_keys": record["src_to_dst_data_keys"]
        } for record in edges_result]

        # Query to get topo_order from the Run node
        topo_order_result = session.run("""
            MATCH (r:Run {run_id: $run_id})
            RETURN r.topo_order AS topo_order
            """, {
                "run_id": run_id
            })

        # Extract topo_sort data
        topo_sort_data = topo_order_result.single()  # Use single() to fetch the first record
        topo_order = topo_sort_data['topo_order'] if topo_sort_data else []

        return {
            "run_id": run_id,
            "topo_order": topo_order,  # Include topo_sort in the response
            "nodes": nodes_data,
            "edges": edges_data
        }


@app.post("/create-graph")
def test_create_graph(graph_data: dict):
    # Time Complexity Analysis:
    # Neo4j Query (Cypher) in create_graph:
    #   - Assuming create_graph involves inserting nodes and edges in a single batch, 
    #     the insertion cost is O(V + E), where V is the number of nodes and E is the number of edges.
    # Overall Algorithm: O(V + E) due to the graph data processing and insertion steps.
    #
    # Space Complexity Analysis:
    # O(V + E) for storing the graph schema data and inserting it into the database.

    """
    Endpoint to create a new graph in the database based on provided graph data.
    
    Args:
        graph_data (dict): Dictionary containing the graph data required to instantiate a new graph.
    
    Response:
        str: A unique identifier (graph_id) for the newly created graph, or an error if creation fails.
    
    Purpose:
        This function validates and creates a new graph by taking in a JSON object,
        initializing it with the GraphSchema, and using a helper function to insert it into the database.
    """
    graph = GraphSchema(**graph_data)
    graph_id = create_graph(graph)
    assert graph_id, "Failed to create graph"
    return graph_id


@app.get("/run_ids/{graph_id}")
async def get_run_ids(graph_id: str):
    # Time Complexity Analysis:
    # Neo4j Query (Cypher):
    #   - The query traverses from a Graph node to its related Node and Output nodes,
    #     returning distinct run IDs. This is O(V) for node traversal, where V is the number of nodes
    #     linked to the graph, and O(R) for retrieving distinct run IDs, where R is the number of unique run IDs.
    # Overall Algorithm: O(V + R) due to the traversal and distinct filtering.
    #
    # Space Complexity Analysis:
    # O(R) for storing the list of run IDs in memory.

    """
    Endpoint to retrieve unique run IDs associated with a specified graph ID.
    
    Args:
        graph_id (str): Unique identifier for the graph whose run IDs are to be retrieved.
    
    Response:
        JSON object containing:
            - run_ids: List of unique run IDs associated with the given graph ID.
    
    Purpose:
        This function queries the Neo4j database to fetch all unique run IDs related to nodes
        within the specified graph, returning them as a list. If no run IDs are found, it raises a 404 error.
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    with driver.session() as session:
        query = """
        MATCH (g:Graph {graph_id: $graph_id})<-[:PART_OF]-(n:Node)-[:OUTPUT]->(o)
        RETURN DISTINCT o.run_id AS run_id
        """
        result = session.run(query, graph_id=graph_id)
        run_ids = [record["run_id"] for record in result]

        if not run_ids:
            raise HTTPException(status_code=404, detail="No run IDs found for the given graph ID.")

    return {"run_ids": run_ids}

from collections import deque
from fastapi import HTTPException
from neo4j import GraphDatabase
import json
from uuid import uuid4

@app.post("/run-graph")
async def run_graph(config: GraphRunConfig):
    # - Time Complexity: O(N + E)
    # - Space Complexity: O(N + E)
    """
    Endpoint to execute a graph run with specific configurations, producing a run ID and propagating data through nodes.
    
    Args:
        config (GraphRunConfig): Configuration object containing graph ID, lists to enable/disable nodes,
                                 initial root inputs, and specific data overwrites.
    
    Response:
        JSON object containing:
            - run_id: Unique identifier for this specific graph run.
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    if config.enable_list and config.disable_list:
        raise HTTPException(status_code=400, detail="Only one of enable_list or disable_list should be provided.")
    
    run_id = str(uuid4())
    
    with driver.session() as session:
        # Step 1: Fetch nodes and edges for the valid subgraph
        nodes_data, edges_data = fetch_subgraph(session, config.graph_id, config.enable_list, config.disable_list)

        # Step 2: Apply root inputs and data overwrites
        apply_inputs_and_overwrites(nodes_data, config.root_inputs, config.data_overwrites)

        # Step 3: Topological Sorting
        topo_order = topological_sort(nodes_data, edges_data)

        # Step 4: Data Propagation
        propagate_data(nodes_data, edges_data, topo_order)

        # Step 5: Save results to Neo4j
        save_run_data(session, nodes_data, edges_data, run_id, config.graph_id, topo_order)

    return {"run_id": run_id}

def fetch_subgraph(session, graph_id, enable_list, disable_list):
    # Nodes query:
    # - Retrieves nodes based on the enable_list or disable_list.
    # - Worst-case time complexity: O(N), where N is the total number of nodes in the graph.
    # Edges query:
    # - Retrieves edges where both source and destination nodes are in the valid subgraph.
    # - Worst-case time complexity: O(E), where E is the total number of edges.
    if enable_list:
        nodes_query = """
        MATCH (n {graph_id: $graph_id})
        WHERE n.node_id IN $enable_list
        RETURN n.node_id AS node_id, n.data_in AS data_in, n.data_out AS data_out
        """
        params = {"graph_id": graph_id, "enable_list": enable_list}
    elif disable_list:
        nodes_query = """
        MATCH (n {graph_id: $graph_id})
        WHERE NOT n.node_id IN $disable_list
        RETURN n.node_id AS node_id, n.data_in AS data_in, n.data_out AS data_out
        """
        params = {"graph_id": graph_id, "disable_list": disable_list}
    
    nodes = session.run(nodes_query, params)
    nodes_data = {
        record["node_id"]: {
            "data_in": json.loads(record["data_in"]) if record["data_in"] else {},
            "data_out": json.loads(record["data_out"]) if record["data_out"] else {}
        }
        for record in nodes
    }

    edges_query = """
    MATCH (src_node {graph_id: $graph_id})-[r]->(dst_node {graph_id: $graph_id})
    WHERE src_node.node_id IN $valid_nodes AND dst_node.node_id IN $valid_nodes
    RETURN src_node.node_id AS src, dst_node.node_id AS dst, r.src_to_dst_data_keys AS src_to_dst_data_keys
    """
    params["valid_nodes"] = list(nodes_data.keys())
    edges = session.run(edges_query, params)

    edges_data = [
        {
            "src": record["src"],
            "dst": record["dst"],
            "src_to_dst_data_keys": json.loads(record["src_to_dst_data_keys"]) if record["src_to_dst_data_keys"] else {}
        }
        for record in edges
    ]

    return nodes_data, edges_data

def apply_inputs_and_overwrites(nodes_data, root_inputs, data_overwrites):
    # - Applying root inputs involves iterating over each node in root_inputs.
    # - Time complexity: O(|R|), where |R| is the number of nodes with root inputs.

    # - Applying data overwrites also involves updating specific nodes.
    # - Time complexity: O(|D|), where |D| is the number of nodes with data overwrites.
    for node_id, inputs in root_inputs.items():
        if node_id in nodes_data:
            nodes_data[node_id]["data_in"].update(inputs)
    for node_id, overwrites in data_overwrites.items():
        if node_id in nodes_data:
            nodes_data[node_id]["data_in"].update(overwrites)

def topological_sort(nodes_data, edges_data):
    # 1. Building the adjacency list and in-degrees:
    # - Iterates over E edges.
    # - Time complexity: O(E).

    # 2. Topological sorting (Kahn's algorithm):
    # - The algorithm traverses all nodes and edges.
    # - Time complexity: O(N + E), where N is the number of nodes and E is the number of edges.
    in_degree = {node_id: 0 for node_id in nodes_data}
    adjacency_list = {node_id: [] for node_id in nodes_data}
    
    for edge in edges_data:
        src, dst = edge["src"], edge["dst"]
        if src in adjacency_list and dst in in_degree:
            adjacency_list[src].append(edge)
            in_degree[dst] += 1

    zero_in_degree = deque([node for node in in_degree if in_degree[node] == 0])
    topo_order = []

    while zero_in_degree:
        node = zero_in_degree.popleft()
        topo_order.append(node)
        for edge in adjacency_list[node]:
            dst = edge["dst"]
            in_degree[dst] -= 1
            if in_degree[dst] == 0:
                zero_in_degree.append(dst)

    return topo_order

def propagate_data(nodes_data, edges_data, topo_order):
    # - Iterating over each node and edge to propagate data.
    # - Time complexity: O(E).
    adjacency_list = {node_id: [] for node_id in nodes_data}
    for edge in edges_data:
        adjacency_list[edge["src"]].append(edge)

    for node in topo_order:
        for edge in adjacency_list[node]:
            src, dst = edge["src"], edge["dst"]
            for src_key, dst_key in edge["src_to_dst_data_keys"].items():
                dst_data_in = nodes_data[dst]["data_in"]
                src_data_out = nodes_data[src]["data_out"]
                dst_data_in[dst_key] = src_data_out.get(src_key)

def save_run_data(session, nodes_data, edges_data, run_id, graph_id, topo_order):
    # 1. Run node creation:
    # - Each run is associated with a unique run_id.
    # - Time complexity: O(1).

    # 2. Creating/Updating OUTPUT relationships:
    # - Iterates over each node to create/update its output relationship.
    # - Time complexity: O(N).

    session.run("""
        MERGE (r:Run {run_id: $run_id, graph_id: $graph_id})
        SET r.topo_order = $topo_order
    """, {"run_id": run_id, "graph_id": graph_id, "topo_order": json.dumps(topo_order)})

    for node_id, node_data in nodes_data.items():
        session.run("""
            MATCH (n:Node {node_id: $node_id, graph_id: $graph_id}),
                  (r:Run {run_id: $run_id, graph_id: $graph_id})
            MERGE (n)-[out:OUTPUT]->(r)
            SET out.data_out = $data_out
        """, {
            "node_id": node_id,
            "graph_id": graph_id,
            "run_id": run_id,
            "data_out": json.dumps(node_data["data_out"])
        })




@app.post("/get-node-output")
async def get_node_output(request: NodeOutputRequest):
    # Create Neo4j driver
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    with driver.session() as session:
        # Query to fetch the output data for the specified node and run
        result = session.run("""
            MATCH (n:Node)-[out:OUTPUT]->(r:Run {run_id: $run_id})
            WHERE n.node_id = $node_id AND n.graph_id = $graph_id
            RETURN out.data_out AS data_out
            """, {
                "node_id": request.node_id,
                "graph_id": request.graph_id,
                "run_id": request.run_id
            }).single()
        
        # Check if the output data exists
        if result and result["data_out"] is not None:
            output_data = json.loads(result["data_out"])
            return {
                "node_id": request.node_id,
                "run_id": request.run_id,
                "data_out": output_data
            }
        
        raise HTTPException(status_code=404, detail="Output data not found for the specified node and run_id")
    
@app.post("/get-leaf-outputs")
async def get_leaf_outputs(request: LeafOutputRequest):
    """
    Endpoint to retrieve the output data for leaf nodes (nodes with no outgoing edges) in a specified graph run.
    
    Args:
        request (LeafOutputRequest): Contains the graph ID and run ID to filter the leaf node outputs.
    
    Response:
        JSON object containing:
            - run_id: The specified run ID.
            - leaf_outputs: Dictionary with leaf node IDs as keys and their respective output data as values.
    
    Purpose:
        This function identifies all leaf nodes in the specified graph that have no outgoing edges. It then
        extracts the output data corresponding to the provided run ID and returns it. If no output data is found
        for the given run ID or graph ID, it raises a 404 error.
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    with driver.session() as session:
        # Step 1: Query all nodes and their output data for the specified run_id
        nodes_result = session.run("""
            MATCH (n:Node)-[out:OUTPUT]->(r:Run {run_id: $run_id})
            RETURN n.node_id AS node_id, n.data_in AS data_in, n.data_out AS data_out
        """, {
            "run_id": request.run_id
        })

        # Collect nodes and output data
        nodes_data = [{"id": record["node_id"], "data_in": record["data_in"], "data_out": record["data_out"]} for record in nodes_result]

        if not nodes_data:
            raise HTTPException(status_code=404, detail="No output data found for the specified run_id.")

        # Step 2: Query all edges between nodes for this run_id
        edges_result = session.run("""
            MATCH (src:Node)-[e:EDGE]->(dst:Node),
                (src)-[:OUTPUT]->(r:Run {run_id: $run_id}),
                (dst)-[:OUTPUT]->(r)
            RETURN src.node_id AS src_id, dst.node_id AS dst_id
        """, {
            "run_id": request.run_id
        })

        # Collect edges data
        edges_data = [{"src": record["src_id"], "dst": record["dst_id"]} for record in edges_result]

        # Step 3: Identify leaf nodes from nodes_data based on edges_data
        # Create a set of all nodes that are sources (have outgoing edges)
        outgoing_nodes = {edge["src"] for edge in edges_data}

        # Find leaf nodes (nodes that are in nodes_data but not in outgoing_nodes)
        leaf_outputs = {}
        for node in nodes_data:
            if node["id"] not in outgoing_nodes:  # This means it's a leaf node
                # Parse the JSON output data correctly
                if node["data_out"]:
                    leaf_outputs[node["id"]] = json.loads(node["data_out"])  # Parse the output JSON string into a dictionary
                else:
                    leaf_outputs[node["id"]] = {}  # Handle case where data_out is None

        # Step 4: Check if any leaf outputs were found
        if leaf_outputs:
            return {"run_id": request.run_id, "leaf_outputs": leaf_outputs}
        else:
            raise HTTPException(status_code=404, detail="No leaf outputs found for the specified run_id.")



