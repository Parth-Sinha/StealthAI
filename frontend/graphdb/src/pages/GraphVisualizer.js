import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import ForceGraph3D from 'react-force-graph-3d';
import Loader from '../Loader';



const GraphVisualizer = () => {
  const { graph_id } = useParams();
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(true); // Loader state
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [runId, setRunId] = useState("");
  const navigate = useNavigate();
  const colors = [
    "#6A9BD1", // Soft Blue
    "#A8D8B9", // Dusty Green
    "#F9B7A0", // Pale Coral
    "#B7A0D6", // Muted Lavender
    "#F2C94C", // Soft Peach
    "#7ED957", // Light Teal
    "#B0A99F", // Warm Gray
    "#E3D8C1"  // Creamy Beige
  ];
  
  useEffect(() => {
    const fetchGraphDetails = async () => {
      setLoading(true); // Set loading to true at the start
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/graphs/${graph_id}`);
        const { nodes, edges } = response.data;
        // Convert edges to links format for react-force-graph
        const links = edges.map((edge) => ({
          source: edge.src,
          target: edge.dst,
        }));

        // Assign random colors to nodes
        const coloredNodes = nodes.map(node => ({
            ...node,
            color: colors[Math.floor(Math.random() * colors.length)] // Random color from the palette
        }));

        setGraphData({ nodes: coloredNodes, links });
      } catch (error) {
        console.error("Error fetching graph details:", error);
      } finally {
        setLoading(false); // Set loading to false once the data is fetched
      }
    };

    fetchGraphDetails();
  }, [graph_id]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
  };
  const handleFileChange = (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile && uploadedFile.type === "application/json") {
      setFile(uploadedFile);
      setError(""); // Clear any previous error
      setSuccessMessage(""); // Clear previous success message
    } else {
      setError("Please upload a valid JSON file.");
      setFile(null); // Reset the file if the format is invalid
    }
  };

  const handleRunGraph = async () => {
    if (!file) {
      setError("Please upload a valid JSON file.");
      return;
    }

    try {
      const reader = new FileReader();
      reader.onload = async () => {
        try {
          const jsonData = JSON.parse(reader.result); // Parse the JSON
          // Make sure jsonData is correctly formatted before sending it
          // Assuming jsonData should have an 'enable_list' or 'disable_list' property
          if (!jsonData.root_inputs && !jsonData.data_overwrites) {
            setError("Please upload correct format");
            return;
          }
          // Send POST request to run the graph
          const response = await axios.post("http://127.0.0.1:8000/run-graph", jsonData);
          setRunId(response.data.run_id);
          setSuccessMessage("Graph run successfully initiated!");
          setSuccess(true);
        } catch (err) {
          setError("Error processing the uploaded JSON file.");
        }
      };
      reader.readAsText(file); // Read the uploaded file as text
    } catch (error) {
      setError("An error occurred while trying to run the graph.");
    }
  };
  const handleViewOutput = () => {
    navigate(`/output/${runId}`);
  };
  // Loader rendering
  if (loading) {
    return <Loader/>
  }
  return (
    <div>

      <button
        onClick={() => navigate("/")}
        className="z-20 absolute top-4 left-4 text-gray-800 hover:text-black bg-blue-500 p-2 rounded-lg"
      >
        Home
      </button>
      <div className="relative w-full h-screen">
      {/* Graph Visualization */}
      <ForceGraph3D
        graphData={graphData}
        nodeId="id"
        linkDirectionalArrowLength={3}
        linkDirectionalArrowRelPos={1}
        linkCurvature={0}
        nodeLabel={(node) => `Node ID: ${node.id}`}
        nodeColor={node => node.color}
        onNodeClick={handleNodeClick}
        backgroundColor='#13171f'
      />

      {/* Sidebar for Node Details */}
      <div className="absolute top-8 right-8 p-4 bg-transparent opacity-60 text-white shadow-lg rounded-lg">
        <h2 className="text-lg font-semibold">Node Details</h2>
        {selectedNode ? (
          <div>
            <p><strong>ID:</strong> {selectedNode.id}</p>
            <p><strong>Data In:</strong> {JSON.stringify(selectedNode.data_in, null, 2)}</p>
            <p><strong>Data Out:</strong> {JSON.stringify(selectedNode.data_out, null, 2)}</p>
          </div>
        ) : (
          <p>Click on a node to see its details.</p>
        )}
      </div>
      {/* File Upload and Run Graph Button */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 p-4 bg-gray-800 text-white shadow-lg rounded-lg">
        <input
          type="file"
          accept="application/json"
          onChange={handleFileChange}
          className="mb-2"
        />
        {success ? <button
          onClick={handleViewOutput}
          className="mt-2 p-2 bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          View Output
        </button>: <button
          onClick={handleRunGraph}
          className="mt-2 p-2 bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Run Graph
        </button>}
        <div>
          {error && <span className="text-red-500">{error}</span>}
          {successMessage && <span className="text-green-500">{successMessage}</span>}

        </div>
      </div>
    </div>
    </div>
  );
};

export default GraphVisualizer;
