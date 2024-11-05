from pydantic import BaseModel, Field, root_validator, ConfigDict
from typing import List, Dict, Optional, Union, Any
from bson import ObjectId
import networkx as nx

# ---- Utility to handle ObjectId ---- #

class PyObjectId(ObjectId):
    """Custom ObjectId class to integrate with Pydantic."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validates if the provided value is a valid ObjectId."""
        if v is None:
            return None
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        """Overrides the JSON schema generation to define ObjectId as a string."""
        schema.update(type="string")
        return schema


# ---- Edge Schema ---- #

class EdgeSchema(BaseModel):
    """Schema for representing an edge in the graph."""
    
    src_node: str  # Source node identifier
    dst_node: str  # Destination node identifier
    src_to_dst_data_keys: Dict[str, str] = {}  # Mapping of data keys from source to destination
    edge_id: str  # Unique identifier for the edge
    
    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types in validation


# ---- Node Schema ---- #

class NodeSchema(BaseModel):
    """Schema for representing a node in the graph."""
    
    node_id: str  # Unique identifier for the node
    data_in: Dict[str, Optional[Union[int, float, str, bool, list, dict]]] = {}  # Input data for the node
    data_out: Dict[str, Optional[Union[int, float, str, bool, list, dict]]] = {}  # Output data from the node
    paths_in: List[EdgeSchema] = []  # Incoming edges
    paths_out: List[EdgeSchema] = []  # Outgoing edges

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types in validation


# ---- Graph Schema ---- #

class GraphSchema(BaseModel):
    """Schema for representing a graph containing nodes and edges."""
    
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)  # Unique identifier for the graph
    nodes: List[NodeSchema]  # List of nodes in the graph
    edges: List[EdgeSchema]  # List of edges in the graph

    @classmethod
    def validate_graph_structure(cls, graph_data):
        """Validates the graph structure and raises ValueError if invalid.
        Works with both dicts and GraphSchema instances."""
        
        # Determine if graph_data is an instance of GraphSchema or a dictionary
        if isinstance(graph_data, GraphSchema):
            # Use dot notation if graph_data is a GraphSchema instance
            nodes = graph_data.nodes
            edges = graph_data.edges
        else:
            # Use dictionary access for dict-based data
            nodes = graph_data.get("nodes", [])
            edges = graph_data.get("edges", [])
        
        # Check for unique node IDs within the graph
        node_ids = [node.node_id for node in nodes]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError("Each node_id within a graph must be unique.")
        
        # Initialize the directed graph
        G = nx.DiGraph()
        G.add_nodes_from(node_ids)

        # Mapping node data for type checks
        node_data_out_map = {node.node_id: node.data_out for node in nodes}
        node_data_in_map = {node.node_id: node.data_in for node in nodes}
        
        edge_pairs = set()  # Track edge pairs to detect duplicates
        for edge in edges:
            # Check if edge references existing nodes
            if edge.src_node not in node_ids or edge.dst_node not in node_ids:
                raise ValueError("Edges must reference existing nodes in the graph.")
            
            # Add edge to directed graph
            G.add_edge(edge.src_node, edge.dst_node)

            # Ensure there are no duplicate edges from the same source node to the same destination node
            edge_pair = (edge.src_node, edge.dst_node)
            if edge_pair in edge_pairs:
                raise ValueError(f"Duplicate edge detected from {edge.src_node} to {edge.dst_node}.")
            edge_pairs.add(edge_pair)

            # Validate compatible data types for src_to_dst_data_keys
            for src_key, dst_key in edge.src_to_dst_data_keys.items():
                src_data_type = type(node_data_out_map[edge.src_node].get(src_key, None))
                dst_data_type = type(node_data_in_map[edge.dst_node].get(dst_key, None))
                if src_data_type != dst_data_type:
                    raise ValueError(f"Incompatible data types for key '{src_key}' in {edge.src_node} "
                                     f"to key '{dst_key}' in {edge.dst_node}: {src_data_type} vs {dst_data_type}.")
            
            # Ensure bidirectional parity in nodes' path records
            src_node = next(node for node in nodes if node.node_id == edge.src_node)
            dst_node = next(node for node in nodes if node.node_id == edge.dst_node)
            if edge not in src_node.paths_out or edge not in dst_node.paths_in:
                raise ValueError(f"Edge parity error: {edge.src_node} -> {edge.dst_node} must be present in both nodes.")

        # Check for cycles
        if not nx.is_directed_acyclic_graph(G):
            raise ValueError("The graph must be a Directed Acyclic Graph (DAG).")

        # Check for islands (ensuring all nodes are in a single connected component)
        if len(list(nx.weakly_connected_components(G))) > 1:
            raise ValueError("All nodes must be connected; isolated subgraphs found.")

        return True  # Validation successful


    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types in validation
        json_encoders = {ObjectId: str}  # Encode ObjectId as string


# ---- Run Schema ---- #

class RunSchema(BaseModel):
    """Schema for representing a run of the graph."""
    
    id: Optional[PyObjectId] = Field(alias="_id", default_factory=PyObjectId)  # Unique identifier for the run
    graph_id: str  # Identifier for the graph this run is associated with
    run_id: str  # Unique identifier for the run
    root_inputs: Dict[str, Dict[str, Union[int, float, str, bool, list, dict]]]  # Input data for root nodes
    data_overwrites: Dict[str, Dict[str, Union[int, float, str, bool, list, dict]]] = {}  # Data overwrites for specific nodes
    enable_list: List[str] = []  # List of nodes to enable for this run
    disable_list: List[str] = []  # List of nodes to disable for this run
    outputs: Dict[str, Dict[str, Union[int, float, str, bool, list, dict]]] = {}  # Outputs from this run

    @root_validator(pre=True)
    def validate_run_config(cls, values):
        """Validates the run configuration to ensure only one of enable_list or disable_list is provided."""
        enable_list = values.get("enable_list", [])
        disable_list = values.get("disable_list", [])
        if enable_list and disable_list:
            raise ValueError("Only one of enable_list or disable_list can be provided, not both.")
        return values

    class Config:
        arbitrary_types_allowed = True  # Allow arbitrary types in validation
        json_encoders = {ObjectId: str}  # Encode ObjectId as string


class GraphRunConfig(BaseModel):
    """Configuration for running a graph."""
    
    graph_id: str  # Identifier for the graph to run
    root_inputs: Dict[str, Dict[str, Union[int, str, float, Any]]]  # Input data for root nodes
    data_overwrites: Dict[str, Dict[str, Union[int, str, float, Any]]]  # Data overwrites for specific nodes
    enable_list: List[str] = []  # List of nodes to enable for this run
    disable_list: List[str] = []  # List of nodes to disable for this run

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow arbitrary types in validation


class NodeOutputRequest(BaseModel):
    """Request schema for obtaining node outputs."""
    
    run_id: str  # Identifier for the run
    node_id: str  # Identifier for the node
    graph_id: str  # Identifier for the graph


class LeafOutputRequest(BaseModel):
    """Request schema for obtaining leaf node outputs."""
    
    run_id: str  # Identifier for the run
    graph_id: str  # Identifier for the graph