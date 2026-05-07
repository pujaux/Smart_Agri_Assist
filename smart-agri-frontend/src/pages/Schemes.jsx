import Navbar from "../components/Navbar";
import "./Schemes.css";

function Schemes() {
  const schemes = [
    {
      id: 1,
      name: "PM-KISAN",
      benefit: "₹6000 per year income support",
      eligibility: "Small and marginal farmers",
    },
    {
      id: 2,
      name: "Soil Health Card Scheme",
      benefit: "Free soil testing and recommendations",
      eligibility: "All farmers",
    },
    {
      id: 3,
      name: "Pradhan Mantri Fasal Bima Yojana",
      benefit: "Crop insurance against natural disasters",
      eligibility: "Farmers with insured crops",
    },
    {
      id: 4,
      name: "Kisan Credit Card",
      benefit: "Low-interest agricultural loans",
      eligibility: "All eligible farmers",
    },
  ];

  return (
    <div>
      <Navbar />

      <div className="schemes-container">
        <h2>Government Schemes</h2>

        <div className="schemes-grid">
          {schemes.map((scheme) => (
            <div key={scheme.id} className="scheme-card">
              <h3>{scheme.name}</h3>
              <p><strong>Benefit:</strong> {scheme.benefit}</p>
              <p><strong>Eligibility:</strong> {scheme.eligibility}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Schemes;
