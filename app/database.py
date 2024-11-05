from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Constants
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

def get_db():
    """Establish a new MongoDB client connection and return the database object."""
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_graphs_collection():
    """Retrieve the graphs collection from MongoDB."""
    db = get_db()
    return db["graphs_collection"]

def get_nodes_collection():
    """Retrieve the nodes collection from MongoDB."""
    db = get_db()
    return db["nodes_collection"]

def get_edges_collection():
    """Retrieve the edges collection from MongoDB."""
    db = get_db()
    return db["edges_collection"]

def create_indexes():
    """Create indexes for collections to optimize common queries."""

    nodes_collection = get_nodes_collection()
    nodes_collection.create_index([("graph_id", 1), ("node_id", 1)], unique=True)

    edges_collection = get_edges_collection()
    edges_collection.create_index([("graph_id", 1), ("src_node", 1), ("dst_node", 1), ("edge_id", 1)], unique=True)
