from database import get_graphs_collection, get_nodes_collection, get_edges_collection
from schemas import GraphSchema
from neo4j_crud import create_graph_in_neo4j


# ---- Graph CRUD Operations ---- #
def create_graph(graph_data: GraphSchema):
    """
    Creates a new graph in MongoDB and Neo4j after validating the graph's structure.

    Args:
        graph_data (GraphSchema): The graph schema containing nodes and edges to be stored.

    Returns:
        str: The unique identifier for the created graph in MongoDB.

    Purpose:
        This function validates the graph data structure, stores the graph, nodes, and edges in MongoDB,
        and synchronizes the data by creating the graph in Neo4j. If an error occurs during the process,
        all MongoDB changes are rolled back to maintain data integrity.
    """
    # Validate the structure before saving
    if not GraphSchema.validate_graph_structure(graph_data):
        raise ValueError("Initial validation failed: The graph structure is invalid.")

    # Initialize MongoDB collections
    graphs_collection = get_graphs_collection()
    nodes_collection = get_nodes_collection()
    edges_collection = get_edges_collection()

    # Track rollback data
    node_ids = []
    edge_ids = []
    graph_id = None

    try:
        # Step 1: Insert the graph document into MongoDB and capture its ID
        graph_id = graphs_collection.insert_one(graph_data.dict(by_alias=True)).inserted_id

        # Step 2: Insert each node into the nodes collection, excluding the graph_id attribute, and store its ID
        for node in graph_data.nodes:
            node_id = nodes_collection.insert_one(node.dict(by_alias=True, exclude={"graph_id"})).inserted_id
            node_ids.append(node_id)

        # Step 3: Insert each edge into the edges collection, excluding the graph_id attribute, and store its ID
        for edge in graph_data.edges:
            edge_id = edges_collection.insert_one(edge.dict(by_alias=True, exclude={"graph_id"})).inserted_id
            edge_ids.append(edge_id)

        # Step 5: Create the graph in Neo4j if MongoDB operations are successful
        create_graph_in_neo4j(graph_data)

    except Exception as e:
        print(f"Error occurred: {e}. Rolling back MongoDB changes.")
        
        # Rollback: If an error occurs, delete the inserted graph, nodes, and edges from MongoDB
        if graph_id:
            graphs_collection.delete_one({"_id": graph_id})
        for node_id in node_ids:
            nodes_collection.delete_one({"_id": node_id})
        for edge_id in edge_ids:
            edges_collection.delete_one({"_id": edge_id})
        
        # Re-raise the exception to propagate the error
        raise

    return str(graph_id)  # Return the MongoDB graph ID as a string for further use


