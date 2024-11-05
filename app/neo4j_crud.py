from neo4j import GraphDatabase
from schemas import GraphSchema
import json
from dotenv import load_dotenv
import os

load_dotenv()

neo4j_uri = os.getenv("neo4j_uri")
neo4j_user = os.getenv("neo4j_user")
neo4j_password = os.getenv("neo4j_password")

def create_graph_in_neo4j(graph_data: GraphSchema):
    """
    Creates a graph in the Neo4j database with nodes and edges based on validated MongoDB data.

    Args:
        graph_data (GraphSchema): The graph data to be created, including nodes and edges.

    Purpose:
        This function adds a new graph to the Neo4j database, creating nodes, their associated data,
        and relationships (edges) between nodes, ensuring each node is linked to the main graph node.
    """
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    graph_id = str(graph_data.id)  # Convert graph ID to string for database compatibility

    with driver.session() as session:
        # Step 1: Create the main graph node
        session.run(
            """
            CREATE (g:Graph {graph_id: $graph_id})
            """,
            graph_id=graph_id
        )

        # Step 2: Create each node in the graph with data_in and data_out properties
        # Link each node to the main graph node using PART_OF relationship
        for node in graph_data.nodes:
            data_in_json = json.dumps(node.data_in)  # Serialize data_in dictionary to JSON
            data_out_json = json.dumps(node.data_out)  # Serialize data_out dictionary to JSON

            # Create the individual node with data properties
            session.run(
                """
                CREATE (n:Node {node_id: $node_id, data_in: $data_in, data_out: $data_out, graph_id: $graph_id})
                """,
                node_id=node.node_id,
                graph_id=graph_id,
                data_in=data_in_json,
                data_out=data_out_json,
            )

            # Establish PART_OF relationship between node and graph
            session.run(
                """
                MATCH (g:Graph {graph_id: $graph_id}), (n:Node {node_id: $node_id, graph_id: $graph_id})
                CREATE (n)-[:PART_OF]->(g)
                """,
                graph_id=graph_id,
                node_id=node.node_id
            )

        # Step 3: Create edges between nodes with src_to_dst_data_keys properties
        for edge in graph_data.edges:
            src_to_dst_data_keys_json = json.dumps(edge.src_to_dst_data_keys) if edge.src_to_dst_data_keys else "{}"

            # Create directed EDGE relationship between source and destination nodes with data key mapping
            session.run(
                """
                MATCH (src:Node {node_id: $src_node, graph_id: $graph_id}),
                      (dst:Node {node_id: $dst_node, graph_id: $graph_id})
                CREATE (src)-[e:EDGE {edge_id: $edge_id, src_to_dst_data_keys: $src_to_dst_data_keys}]->(dst)
                """,
                src_node=edge.src_node,
                dst_node=edge.dst_node,
                edge_id=edge.edge_id,
                graph_id=graph_id,
                src_to_dst_data_keys=src_to_dst_data_keys_json,
            )

    # Close the database driver after all operations are complete
    driver.close()

