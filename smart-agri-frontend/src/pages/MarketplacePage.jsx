import Navbar from "../components/Navbar";
import "./Marketplace.css";

function Marketplace() {
  const products = [
    {
      id: 1,
      name: "Wheat",
      price: "₹2200 / quintal",
      farmer: "Ramesh Kumar",
    },
    {
      id: 2,
      name: "Rice",
      price: "₹1800 / quintal",
      farmer: "Suresh Patel",
    },
    {
      id: 3,
      name: "Tomatoes",
      price: "₹25 / kg",
      farmer: "Amit Singh",
    },
    {
      id: 4,
      name: "Milk",
      price: "₹45 / litre",
      farmer: "Sunita Devi",
    },
  ];

  return (
    <div>
      <Navbar />

      <div className="market-container">
        <h2>Farmer Marketplace</h2>

        <div className="product-grid">
          {products.map((product) => (
            <div key={product.id} className="product-card">
              <h3>{product.name}</h3>
              <p><strong>Price:</strong> {product.price}</p>
              <p><strong>Farmer:</strong> {product.farmer}</p>
              <button className="buy-btn">Contact Farmer</button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Marketplace;
