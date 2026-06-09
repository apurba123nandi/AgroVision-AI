# 🌿 AgroVision AI — Smart Crop Disease Detection Platform

<p align="center">
  <img src="demo/banner.png" alt="AgroVision AI Banner" width="100%"/>
</p>

<p align="center">
  <a href="#demo">📱 Demo Video</a> •
  <a href="#features">✨ Features</a> •
  <a href="#tech-stack">🛠 Tech Stack</a> •
  <a href="#installation">🚀 Installation</a> •
  <a href="#apk">📦 Download APK</a>
</p>

---

## 📱 Demo Video <a name="demo"></a>

> Watch AgroVision AI in action on an Android phone:

https://github.com/YOUR_GITHUB_USERNAME/AgroVision-AI/assets/demo/agrovision_demo.mp4

*(Replace the link above with your actual GitHub video URL after uploading)*

---

## 🌟 About

**AgroVision AI** is an AI-powered mobile application designed for farmers to detect crop diseases using their smartphone camera. Simply take a photo of a crop leaf and the app instantly diagnoses the disease, provides treatment recommendations, locates nearby pesticide stores, and gives real-time environmental risk analysis — all with multilingual support in **English, Telugu, and Hindi**.

---

## ✨ Features <a name="features"></a>

| Feature | Description |
|---|---|
| 🤖 **AI Disease Detection** | Powered by YOLOv8 model trained on crop disease datasets |
| 📸 **Camera Integration** | Native camera access via Capacitor on Android |
| 🌦 **Live Weather Sync** | Automatic GPS-based weather fetch via OpenWeatherMap API |
| 🌍 **Environmental Risk** | Dynamic disease spread risk based on humidity, rain & temperature |
| 🌿 **Organic Remedies** | Eco-friendly treatment suggestions for each disease & severity |
| 💊 **Dosage Calculator** | Calculate exact pesticide dosage per acre for your field |
| 🗺 **Nearby Stores** | Locate pesticide & agri stores near you via Google Maps API |
| 🔊 **Voice Guide** | Text-to-speech remedy reading in farmer's native language |
| 📶 **Offline Mode** | Full local inference when internet is unavailable |
| 🌐 **Multilingual** | English, Telugu (తెలుగు), Hindi (हिन्दी) |
| ☀️ **Field Mode** | High-contrast display for bright outdoor sunlight |

---

## 🦠 Detectable Diseases

- ✅ **Healthy** — No treatment needed
- 🍃 **Powdery Mildew** — Fungal disease affecting leaves
- 🟫 **Rust** — Fungal disease causing orange/brown spots

---

## 🛠 Tech Stack <a name="tech-stack"></a>

### Frontend (Android App)
| Technology | Purpose |
|---|---|
| React 19 + Vite | UI Framework |
| Capacitor 8 | Native Android bridge |
| @capacitor/camera | Camera access |
| @capacitor/network | Offline detection |
| @capacitor-community/text-to-speech | Voice guide |
| Lucide React | Icons |

### Backend (Python API)
| Technology | Purpose |
|---|---|
| FastAPI | REST API server |
| Ultralytics YOLOv8 | Crop disease detection model |
| Pillow | Image processing |
| OpenWeatherMap API | Live weather data |
| Google Maps API | Nearby store locator |
| Nominatim (OpenStreetMap) | Reverse geocoding |

---

## 🚀 Installation <a name="installation"></a>

### Prerequisites
- Python 3.10+
- Node.js 18+
- Android Studio (for building APK)

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/AgroVision-AI.git
cd AgroVision-AI
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
python main.py
```
> Backend runs at **http://127.0.0.1:8000**

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
> Frontend runs at **http://localhost:5173**

### 4. Build Android APK
```bash
cd frontend
npm run build
npx cap sync
npx cap open android
```
Then in Android Studio: **Build → Generate Signed APK**

---

## 📦 Download APK <a name="apk"></a>

> 📲 **[Download Latest APK](demo/AgroVision-AI.apk)**

Install directly on your Android device (enable "Install from unknown sources" in settings).

---

## 📁 Project Structure

```
AgroVision-AI/
├── backend/
│   ├── main.py              # FastAPI server with /predict, /nearby-stores, /reverse-geocode
│   ├── best.pt              # YOLOv8 trained model
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app with online/offline detection
│   │   ├── components/
│   │   │   ├── ImageUploader.jsx      # Drag & drop + camera
│   │   │   ├── ResultCard.jsx         # AI diagnostic report
│   │   │   ├── EnvironmentalForm.jsx  # Live weather display
│   │   │   ├── EnvironmentalInsights.jsx
│   │   │   ├── SpreadPredictor.jsx
│   │   │   ├── OrganicTreatment.jsx
│   │   │   ├── DosageCalculator.jsx
│   │   │   ├── PesticideStores.jsx    # Google Maps store finder
│   │   │   └── VoiceGuide.jsx         # TTS remedy reader
│   │   ├── services/
│   │   │   └── InferenceService.js    # Online API + offline fallback
│   │   └── utils/
│   │       └── translations.js        # EN / TE / HI translations
│   └── android/             # Capacitor Android project
└── demo/
    └── agrovision_demo.mp4  # App demo video
```

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/predict` | POST | Detect disease from uploaded image |
| `/nearby-stores` | GET | Find pesticide stores near GPS coordinates |
| `/reverse-geocode` | GET | Convert GPS coordinates to city name |
| `/detect-location` | GET | IP-based location fallback |

---

## 📷 Screenshots

> *(Add screenshots of the app here)*

---

## 🔐 Environment Notes

- Replace `GOOGLE_MAPS_KEY` in `backend/main.py` with your own Google Maps API key
- Replace `apiKey` in `EnvironmentalForm.jsx` with your OpenWeatherMap API key

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

Built with ❤️ for Indian farmers.

> *AgroVision AI — Empowering farmers with smart technology*
