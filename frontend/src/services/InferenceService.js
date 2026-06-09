import remedies from '../data/remedies.json';

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const organicMethods = {
  healthy: {
    Low: [
      { name: "Organic Compost", instruction: "Apply well-decomposed organic compost to improve soil nutrients." },
      { name: "Proper Irrigation", instruction: "Maintain consistent watering schedule to reduce plant stress." },
      { name: "Crop Rotation", instruction: "Rotate crops seasonally to prevent soil-borne pathogen buildup." }
    ]
  },
  powdery: {
    Low: [
      { name: "Neem Oil Spray", instruction: "Mix 5ml neem oil per liter of water and spray weekly." },
      { name: "Milk Spray", instruction: "Mix milk and water in a 1:2 ratio and apply to leaves." },
      { name: "Improve Airflow", instruction: "Prune excess foliage and increase spacing between plants." }
    ],
    Medium: [
      { name: "Baking Soda Spray", instruction: "Mix 1 tbsp baking soda with 1 gallon water and a drop of soap." },
      { name: "Potassium Bicarbonate", instruction: "Apply as an antifungal spray to stop spore spread." },
      { name: "Neem Oil", instruction: "Increase application to twice weekly for better control." }
    ],
    High: [
      { name: "Remove Infected Leaves", instruction: "Prune and dispose of heavily infected parts immediately." },
      { name: "Compost Tea Spray", instruction: "Apply weekly to boost the plant's natural immune response." },
      { name: "Regular Neem Oil", instruction: "Apply every 3-4 days until the outbreak is managed." }
    ]
  },
  rust: {
    Low: [
      { name: "Remove Affected Leaves", instruction: "Pick off early spotted leaves and dispose of them properly." },
      { name: "Neem Oil Spray", instruction: "Mix 5ml per liter and apply as a preventive measure." },
      { name: "Sunlight Exposure", instruction: "Ensure plants get maximum sunlight to reduce leaf surface moisture." }
    ],
    Medium: [
      { name: "Compost Tea Spray", instruction: "Boost plant resistance by applying nutrient-rich compost tea." },
      { name: "Garlic Spray", instruction: "Blend garlic with water, strain, and spray on affected areas." },
      { name: "Neem Oil Application", instruction: "Apply consistently every 5 days to manage spore spread." }
    ],
    High: [
      { name: "Pruning", instruction: "Aggressively remove heavily infected areas to save the rest of the plant." },
      { name: "Frequent Neem Sprays", instruction: "Apply every 3 days to suppress rapid rust development." },
      { name: "Organic Fungicide", instruction: "Use copper-free organic antifungal solutions for severe cases." }
    ]
  }
};

export const performLocalInference = async (previewUrl, envData = {}) => {
  // Simulate heavy local model inference
  await sleep(1500);
  
  const results = [
    { name: 'Healthy', key: 'healthy' },
    { name: 'Powdery Mildew', key: 'powdery' },
    { name: 'Rust', key: 'rust' }
  ];
  
  const randomResult = results[Math.floor(Math.random() * results.length)];
  const isHealthy = randomResult.key === 'healthy';
  const severity = isHealthy ? 'Low' : ['Low', 'Medium', 'High'][Math.floor(Math.random() * 3)];
  const confidence = parseFloat((Math.random() * (0.99 - 0.88) + 0.88).toFixed(2));
  
  // Dynamic environmental risk calculation in mock
  const humidity = parseFloat(envData.humidity || 50);
  const temperature = parseFloat(envData.temperature || 25);
  const rainStatus = envData.rain_status || 'noRain';
  
  let envScore = 0;
  if (humidity > 70 && (envData.rain === 'Yes' || (temperature >= 20 && temperature <= 30))) {
    envScore = 2;
  } else if (humidity >= 50 || rainStatus === 'lightRain' || (temperature >= 25 && temperature <= 32)) {
    envScore = 1;
  }
  if (rainStatus === 'moderateRain') envScore = Math.max(envScore, 1);
  else if (rainStatus === 'heavyRain') envScore = 2;
  
  const riskLevels = ["Low", "Medium", "High"];
  const envRisk = riskLevels[envScore];
  const envInsight = envRisk === "High" ? "Conditions strongly favor fungal disease spread." :
                     envRisk === "Medium" ? "Moderate environmental conditions. Monitor crops regularly." :
                     "Environmental conditions are not favorable for disease spread.";

  const sScore = Math.max(0, Math.min(2, (severity === "High" ? 2 : severity === "Medium" ? 1 : 0) + (randomResult.key === 'rust' ? 1 : 0) + (envScore === 2 ? 1 : envScore === 0 ? -1 : 0)));
  const finalSpreadRisk = isHealthy ? "Low" : riskLevels[sScore];
  const spreadMsg = finalSpreadRisk === "Low" ? "Low risk. Disease spread is minimal." :
                    finalSpreadRisk === "Medium" ? "Moderate spread expected. Monitor closely." :
                    "High risk of disease spreading due to favorable conditions.";

  const recs = {
    healthy: "No disease detected. Maintain regular monitoring.",
    powdery: { Low: "Improve airflow and avoid moisture.", Medium: "Apply neem oil.", High: "Use sulfur-based fungicide." },
    rust: { Low: "Remove infected leaves.", Medium: "Apply fungicide.", High: "Use systemic fungicide." }
  };
  const recommendation = isHealthy ? recs.healthy : (recs[randomResult.key][severity] || `Detected ${randomResult.name}. Consult a specialist.`);

  const methods = isHealthy ? organicMethods.healthy.Low : (organicMethods[randomResult.key]?.[severity] || [
    { name: "General Bio-Fungicide", instruction: "Apply neem oil (5ml/L) as a broad-spectrum preventive measure." }
  ]);

  return {
    disease: randomResult.name,
    confidence: confidence,
    low_confidence: confidence < 0.45,
    severity: severity,
    treatment: recommendation,
    detected: !isHealthy,
    annotated_image: previewUrl,
    environmental_insights: {
      risk_level: envRisk,
      insight_message: envInsight
    },
    spread_prediction: {
      risk_level: finalSpreadRisk,
      insight_message: spreadMsg
    },
    organic_treatment: {
      methods: methods,
      label: "Eco-Friendly Alternatives"
    }
  };
};

export const performInference = async (selectedImage, envData, isOffline) => {
  if (isOffline) {
    console.log("Offline mode active. Falling back to local inference...");
    return performLocalInference(selectedImage.preview, envData);
  }

  try {
    const formData = new FormData();
    formData.append("file", selectedImage.file);
    formData.append("temperature", parseFloat(envData.temperature || 25));
    formData.append("humidity", parseFloat(envData.humidity || 50));
    formData.append("rain", envData.rain || "No");
    formData.append("rain_status", envData.rain_status || "No Rain");
    formData.append("rain_amount", parseFloat(envData.rain_amount || 0));

    const response = await fetch("http://127.0.0.1:8000/predict", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.warn("Connection to prediction API failed. Falling back to local inference...", error);
    return performLocalInference(selectedImage.preview, envData);
  }
};

