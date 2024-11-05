import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';
import ForceGraph3D from 'react-force-graph-3d';
import Loader from '../Loader';


const OutputVisualizer = () => {
    const { run_id } = useParams();
    const [graphData, setGraphData] = useState({ nodes: [], links: [], topo_order: [] });
    const [selectedNode, setSelectedNode] = useState(null);
    const [loading, setLoading] = useState(true); // Loader state
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
      if (!run_id) return;
  
      const fetchGraphDetails = async () => {
        setLoading(true); 
        try {
          const response = await axios.get(`http://127.0.0.1:8000/output/${run_id}`);
  
          const { nodes, edges, topo_order } = response.data;
          console.log(response.data)
          // Convert edges to links format for react-force-graph
          const links = edges.map((edge) => ({
            source: edge.src,
            target: edge.dst,
          }));
  
          // Assigning random colors to nodes for a better visualization
          const coloredNodes = nodes.map(node => ({
            ...node,
            color: colors[Math.floor(Math.random() * colors.length)] // Random color from the palette
          }));
  
          setGraphData({ nodes: coloredNodes, links, topo_order });
        } catch (error) {
          console.error("Error fetching graph details:", error);
        } finally {
          setLoading(false); // Setting loading to false once the data is fetched
        }
      };
  
      fetchGraphDetails();
    }, [run_id]);
  
    const handleNodeClick = (node) => {
      setSelectedNode(node);
    };
    
    // Loader rendering
    if (loading) {
      return <Loader />;
    }
  return (
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
      <p><strong>ID:</strong> {selectedNode.id}</p> {/* Assuming 'node_id' is the correct property */}
      <p><strong>Data In:</strong> 
        {selectedNode.data_in ? (
          <pre>{JSON.stringify(JSON.parse(selectedNode.data_in), null, 2)}</pre>
        ) : 'No Data'}
      </p>
      <p><strong>Data Out:</strong> 
        {selectedNode.data_out ? (
          <pre>{JSON.stringify(JSON.parse(selectedNode.data_out), null, 2)}</pre>
        ) : 'No Data'}
      </p>
      <p><strong> Level Order Traversal </strong> </p>
      <pre>{JSON.stringify(JSON.parse(graphData.topo_order), null, 2)}</pre>
      
    </div>
  ) : (
    <div>
      <p>Click on a node to see its details.</p>
      <p><strong> Level Order Traversal </strong> </p>
      <pre>{JSON.stringify(JSON.parse(graphData.topo_order), null, 2)}</pre>
    </div>
    
  )}
</div>

    </div>
  );
};

export default OutputVisualizer;
