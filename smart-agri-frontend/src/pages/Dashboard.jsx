import Navbar from "../components/Navbar";
import { useNavigate } from "react-router-dom";
import "./Dashboard.css";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div>
      <Navbar />

      <div className="dashboard-container">

        {/* Hero Section */}
        <div className="hero-section">
          <div className="hero-text">
            <h1>Smart Agriculture Made Easy</h1>
            <p>
              AI-powered insights for crops, livestock, and direct
              marketplace access.
            </p>
            <button
              className="primary-btn"
              onClick={() => navigate("/crop")}
            >
              Explore Features
            </button>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="card-grid">

          <div
            className="feature-card"
            onClick={() => navigate("/crop")}
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/2909/2909767.png"
              alt="crop"
            />
            <h3>Crop Detection</h3>
            <p>Identify crop diseases using AI.</p>
          </div>

          <div
            className="feature-card"
            onClick={() => navigate("/livestock")}
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/1998/1998610.png"
              alt="livestock"
            />
            <h3>Livestock Health</h3>
            <p>Detect wounds and infections.</p>
          </div>

          <div
            className="feature-card"
            onClick={() => navigate("/marketplace")}
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/263/263142.png"
              alt="marketplace"
            />
            <h3>Marketplace</h3>
            <p>Sell products directly to buyers.</p>
          </div>

          <div
            className="feature-card"
            onClick={() => navigate("/schemes")}
          >
            <img
              src="https://cdn-icons-png.flaticon.com/512/3135/3135706.png"
              alt="schemes"
            />
            <h3>Government Schemes</h3>
            <p>Explore farming benefits.</p>
          </div>

        </div>
      </div>
    </div>
  );
}

export default Dashboard;
