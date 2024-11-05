import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import GraphsListPage from './pages/GraphsListPage';
import GraphVisualizer from './pages/GraphVisualizer';
import OutputVisualizer from './pages/OutputVisualizer';

function App() {
  return (
      <Router>
        <div className="min-h-screen bg-[#1b2832]">
          <Routes>
            <Route path="/" element={<GraphsListPage />} />
            <Route path="/graph/:graph_id" element={<GraphVisualizer />} /> {/* Dynamic route for graph details */}
            <Route path="/output/:run_id" element={<OutputVisualizer />} /> {/* Dynamic route for graph details */}
          </Routes>
        </div>
      </Router>
  );
}

export default App;
