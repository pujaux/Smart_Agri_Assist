import Navbar from "../components/Navbar";
import { useState } from "react";
import "./Crop.css";

function Crop() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    setImage(URL.createObjectURL(file));
  };

  const handleDetect = () => {
    // Dummy result for now
    setResult({
      disease: "Leaf Blight",
      confidence: "92%",
      suggestion: "Apply recommended fungicide and remove infected leaves.",
    });
  };

  return (
    <div>
      <Navbar />

      <div className="crop-container">
        <h2>Crop Disease Detection</h2>

        <div className="upload-box">
          <input type="file" onChange={handleImageChange} />
        </div>

        {image && (
          <div className="image-preview">
            <img src={image} alt="Uploaded crop" />
          </div>
        )}

        {image && (
          <button className="detect-btn" onClick={handleDetect}>
            Detect Disease
          </button>
        )}

        {result && (
          <div className="result-box">
            <h3>Detection Result</h3>
            <p><strong>Disease:</strong> {result.disease}</p>
            <p><strong>Confidence:</strong> {result.confidence}</p>
            <p><strong>Suggestion:</strong> {result.suggestion}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Crop;
