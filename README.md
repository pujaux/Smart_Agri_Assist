🌾 __Smart Agri Assist Platform__

An AI-Driven Decision Support and Marketplace System for Crop and Livestock Farmers
<img width="1366" height="731" alt="Screenshot (991)" src="https://github.com/user-attachments/assets/7e5dfad5-ac91-46ee-8155-f891e4924edc" />

#Crop Disease Detection — Before & After:
<img width="1366" height="731" alt="Screenshot (993)" src="https://github.com/user-attachments/assets/a6ebf4ea-b1af-4b00-aade-8fad4a5d49cb" />

<img width="1366" height="729" alt="Screenshot (994)" src="https://github.com/user-attachments/assets/18a4504d-3af3-4ab6-81c4-3606c2b281b5" />

 #Livestock Health Detection:
<img width="1366" height="695" alt="Screenshot (996)" src="https://github.com/user-attachments/assets/ee92b1ff-dbd9-4eeb-9ca7-651329609f1e" />

🛒 #Marketplace — Direct Farmer-to-Buyer:
<img width="1366" height="727" alt="Screenshot (997)" src="https://github.com/user-attachments/assets/fa61c889-4737-4b66-919f-8c3e56638c1d" />

🏛️ #Government Schemes:
<img width="1366" height="727" alt="Screenshot (998)" src="https://github.com/user-attachments/assets/fb571bc5-3a9a-49c6-9e4e-2ee40f3e2abb" />

📖 #Overview
Smart Agri Assist is an integrated AI-powered digital ecosystem built to support Indian crop and livestock farmers. 
Unlike traditional agritech tools that address only a single problem, this platform unifies disease detection, smart recommendations, 
government scheme awareness, and a direct marketplace — all in one place.
the platform empowers farmers with data-driven tools to reduce crop loss, access fair markets, and make informed decisions.

🖥️ #Platform Preview
Dashboard & Navigation
The platform features a clean, multi-language dashboard with easy navigation across all core modules
<img width="1366" height="731" alt="Screenshot (992)" src="https://github.com/user-attachments/assets/1ae07e1b-3d22-421c-a9fe-c1aea6b8b50e" />
Home page showing Dashboard, Crop Detection, Livestock Health, Marketplace, and Government Schemes navigation.

#Key Features:
Feature : Description
🌿 Crop Disease DetectionCNN-based image analysis detects diseases with up to 94% accuracy
🐄 Livestock Health MonitoringMultimodal diagnosis combining image + symptom text input
🤖 Smart Recommendation EnginePersonalized farming plans based on land, budget, soil & climate
🛒 Direct MarketplaceSell produce directly to buyers — no intermediaries
🏛️ Government SchemesSearchable database of agricultural support programs
🌦️ Climate Risk PredictionWeather-aware farming advisories
🌍 Multilingual Voice AssistantRegional language support for accessibility
📊 Yield PredictionML-based crop yield forecasting

#System Architecture:
┌─────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                      │
│              React.js  ·  Responsive UI                 │
│         (Dashboard, Upload, Marketplace, Forms)         │
└────────────────────────┬────────────────────────────────┘
                         │ RESTful API (HTTPS)
┌────────────────────────▼────────────────────────────────┐
│                  APPLICATION LAYER                       │
│              Flask / FastAPI  ·  Python                 │
│   (Auth · Routing · ML Integration · Recommendations)   │
└──────────────┬─────────────────────┬────────────────────┘
               │                     │
┌──────────────▼──────┐   ┌──────────▼──────────────────┐
│    DATA LAYER       │   │       AI / ML LAYER          │
│  PostgreSQL/MySQL   │   │  TensorFlow · PyTorch        │
│  (Users, Listings,  │   │  OpenCV · Scikit-learn       │
│   Logs, Schemes)    │   │  CNN · ResNet · MobileNet    │
└─────────────────────┘   └─────────────────────────────-┘

 #Tech Stack:

#Frontend
React.js — Component-based UI with responsive design
Axios — Async API communication

#Backend
Python + Flask — RESTful API server
JWT — Stateless authentication
bcrypt — Password hashing

#AI / Machine Learning:
TensorFlow / PyTorch — Deep learning model training
OpenCV — Image preprocessing pipeline
Scikit-learn — Auxiliary ML tasks (yield prediction, pest estimation)
CNN Architectures: MobileNet, ResNet (transfer learning)

#Database
PostgreSQL / MySQL — Relational data storage with ACID compliance

🔮 #Future Roadmap

 IoT sensor integration for real-time soil and climate monitoring
 Improve ux/ui
 Drone-based crop surveillance
 Blockchain-powered supply chain transparency
 Offline mode for low-connectivity rural areas
 Community discussion forum
 Livestock nutrition planner

 📄 License
This project was developed for academic purposes under the EPICS (Engineering Projects in Community Service) program at VIT Bhopal University. All rights reserved by the team.


<p align="center">
  Made with ❤️ for Indian Farmers 
</p>
