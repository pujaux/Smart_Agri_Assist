import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Crop from "./pages/Crop";
import Livestock from "./pages/Livestock";
import Marketplace from "./pages/MarketplacePage";
import Schemes from "./pages/Schemes";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/crop" element={<Crop />} />
        <Route path="/livestock" element={<Livestock />} />
        <Route path="/marketplace" element={<Marketplace />} />
        <Route path="/schemes" element={<Schemes />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
