import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Loader from '../Loader';

const GraphsListPage = () => {
  const [graphs, setGraphs] = useState([]);
  const [expandedGraph, setExpandedGraph] = useState(null); // Track which graph is expanded
  const [runIds, setRunIds] = useState({}); // Store run_ids for each graph
  const [loading, setLoading] = useState(true); // Loader state
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch list of graphs
    const fetchGraphs = async () => {
      setLoading(true); // Set loading to true at the start
      try {
        const response = await axios.get("http://127.0.0.1:8000/api/graphs");
        setGraphs(response.data);
        
      } catch (error) {
        console.error("Error fetching graphs list:", error);
      }
      finally {
        setLoading(false); // Set loading to false once the data is fetched
      }
    };

    fetchGraphs();
  }, []);

  const handleRunIdsClick = async (graphId) => {
    // Toggle expanded graph or fetch run_ids if not already fetched
    if (expandedGraph === graphId) {
      setExpandedGraph(null); // Collapse if already expanded
    } else {
      setExpandedGraph(graphId); // Expand this graph
      if (!runIds[graphId]) {
        try {
          const response = await axios.get(`http://127.0.0.1:8000/run_ids/${graphId}`);
          setRunIds((prevRunIds) => ({
            ...prevRunIds,
            [graphId]: response.data.run_ids, // Store fetched run_ids
          }));
        } catch (error) {
          console.error("Error fetching run IDs:", error);
        }
      }
    }
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

  const handleCreateGraph = async () => {
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
          if (!jsonData.nodes || !jsonData.edges) {
            setError("Please upload correct format");
            return;
          }
          // Send POST request to run the graph
          const response = await axios.post("http://127.0.0.1:8000/create-graph", jsonData);
          setSuccessMessage("Graph run successfully initiated!");
        } catch (err) {
          console.error("Error processing file:", err);
          setError("Error processing the uploaded JSON file.");
        }
      };
      reader.readAsText(file); // Read the uploaded file as text
    } catch (error) {
      console.error("Error running graph:", error);
      setError("An error occurred while trying to run the graph.");
    }
  };
  

  if (loading) {
    return <Loader />;
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4 text-blue-700">Select a Graph</h1>
      <ul className="space-y-3">
        {graphs.map((graph) => (
          <li key={graph.graph_id} className="bg-blue-100 rounded-lg p-4">
            <div className="flex justify-between items-center cursor-pointer hover:bg-blue-200 rounded p-2">
              <span onClick={() => navigate(`/graph/${graph.graph_id}`)}>
                {graph.graph_id}
              </span>
              <button
                className="bg-blue-500 text-white px-2 py-1 rounded hover:bg-blue-600"
                onClick={() => handleRunIdsClick(graph.graph_id)}
              >
                Run IDs
              </button>
            </div>
            {/* Conditionally display run IDs if this graph is expanded */}
            {expandedGraph === graph.graph_id && runIds[graph.graph_id] && (
              <ul className="mt-2 space-y-1 pl-4">
                {runIds[graph.graph_id].map((runId) => (
                  <li
                    key={runId}
                    className="cursor-pointer text-blue-700 hover:underline"
                    onClick={() => navigate(`/output/${runId}`)}
                  >
                    {runId}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ul>
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 p-4 bg-gray-800 text-white shadow-lg rounded-lg">
        <input
          type="file"
          accept="application/json"
          onChange={handleFileChange}
          className="mb-2"
        />
        <button
          onClick={handleCreateGraph}
          className="mt-2 p-2 bg-blue-600 rounded-lg hover:bg-blue-700"
        >
          Create Graph
        </button>
        <div>
          {error && <span className="text-red-500">{error}</span>}
          {successMessage && <span className="text-green-500">{successMessage}</span>}

        </div>
      </div>
    </div>
  );
};

export default GraphsListPage;