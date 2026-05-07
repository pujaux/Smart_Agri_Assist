import Navbar from "../components/Navbar";
import { useState } from "react";
import "./Livestock.css";

function Livestock() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(URL.createObjectURL(file));
  };

  const handleDetect = () => {
    // Dummy result
    setResult({
      issue: "Minor skin infection",
      confidence: "88%",
      suggestion: "Clean the affected area and apply antiseptic ointment.",
    });
  };

  return (
    <div>
      <Navbar />

      <div className="livestock-container">
        <h2>Livestock Health Detection</h2>

        <div className="upload-box">
          <input type="file" onChange={handleImageChange} />
        </div>

        {image && (
          <div className="image-preview">
            <img src={image} alt="Uploaded livestock" />
          </div>
        )}

        {image && (
          <button className="detect-btn" onClick={handleDetect}>
            Detect Issue
          </button>
        )}

        {result && (
          <div className="result-box">
            <h3>Detection Result</h3>
            <p><strong>Issue:</strong> {result.issue}</p>
            <p><strong>Confidence:</strong> {result.confidence}</p>
            <p><strong>Suggestion:</strong> {result.suggestion}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Livestock;
