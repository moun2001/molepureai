# Drug Interaction Prediction API - Complete Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Endpoints](#endpoints)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Client Examples](#client-examples)
- [SDKs and Libraries](#sdks-and-libraries)

## 🎯 Overview

The Drug Interaction Prediction API provides machine learning-powered predictions for drug-drug interaction severity levels. The API analyzes drug characteristics and returns severity classifications (Major, Moderate, Minor) with confidence scores and clinical recommendations.

### Base URLs
- **Development**: `http://localhost:5000`
- **Production**: `https://api.druginteractions.example.com`

### API Version
Current version: **1.0.0**

## 🔐 Authentication

Currently, the API does not require authentication. For production deployments, consider implementing:
- API key authentication
- OAuth 2.0
- JWT tokens

## ⚡ Rate Limiting

- **Rate Limit**: 100 requests per minute per IP address
- **Burst Limit**: 10 requests per second
- **Drug Limit**: Maximum 10 drugs per request
- **Timeout**: 120 seconds per request

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## 🛠 Endpoints

### Health Check Endpoints

#### `GET /`
Basic health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Drug Interaction Prediction API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "model_loaded": true
}
```

#### `GET /health`
Detailed health check with component status.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "Drug Interaction Prediction API",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "checks": {
    "model_loaded": true,
    "preprocessor_ready": true,
    "predictor_ready": true,
    "validator_ready": true
  },
  "uptime": "2024-01-01T12:00:00.000Z"
}
```

### Prediction Endpoints

#### `POST /predict-interactions`
Predict drug-drug interactions for multiple drugs.

**Request Body:**
```json
{
  "drugs": [
    {
      "drug_name": "Warfarin",
      "pharmacodynamic_class": "Anticoagulant",
      "logp": 2.7,
      "therapeutic_index": "NTI",
      "transporter_interaction": "Substrate: P-gp",
      "plasma_protein_binding": 99.0,
      "metabolic_pathways": "Substrate: CYP2C9;CYP3A4"
    },
    {
      "drug_name": "Amiodarone",
      "pharmacodynamic_class": "Antiarrhythmic",
      "logp": 7.6,
      "therapeutic_index": "NTI",
      "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp",
      "plasma_protein_binding": 96.0,
      "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "input_drugs_count": 2,
  "drug_pairs_analyzed": 1,
  "predictions": [
    {
      "drug_pair": {
        "drug_a": {
          "index": 0,
          "name": "Warfarin",
          "class": "Anticoagulant"
        },
        "drug_b": {
          "index": 1,
          "name": "Amiodarone",
          "class": "Antiarrhythmic"
        }
      },
      "prediction": {
        "severity": "Moderate",
        "confidence": 0.961,
        "risk_level": "Medium"
      },
      "probability_distribution": {
        "Major": 0.035,
        "Moderate": 0.961,
        "Minor": 0.004
      },
      "clinical_significance": "Moderate clinical significance - Monitor patient closely",
      "recommendation": "Monitor patient for adverse effects. Consider dose adjustment if needed."
    }
  ],
  "summary": {
    "high_risk_pairs": 0,
    "moderate_risk_pairs": 1,
    "low_risk_pairs": 0
  }
}
```

### Information Endpoints

#### `GET /api/info`
Get API information and usage guidelines.

**Response:**
```json
{
  "api_name": "Drug Interaction Prediction API",
  "version": "1.0.0",
  "description": "Predicts drug-drug interaction severity using machine learning",
  "endpoints": {
    "/": "Health check",
    "/predict-interactions": "Main prediction endpoint (POST)",
    "/api/info": "API information"
  },
  "supported_severity_levels": ["Major", "Moderate", "Minor"],
  "required_drug_fields": [
    "drug_name",
    "pharmacodynamic_class",
    "logp",
    "therapeutic_index",
    "transporter_interaction",
    "plasma_protein_binding",
    "metabolic_pathways"
  ]
}
```

## 📊 Data Models

### Drug Object
```json
{
  "drug_name": "string (2-100 chars)",
  "pharmacodynamic_class": "string",
  "logp": "number (-10.0 to 15.0)",
  "therapeutic_index": "string (NTI|Non-NTI)",
  "transporter_interaction": "string",
  "plasma_protein_binding": "number (0.0-100.0)",
  "metabolic_pathways": "string"
}
```

### Prediction Response
- **severity**: Major | Moderate | Minor
- **confidence**: 0.0 - 1.0 (prediction confidence)
- **risk_level**: High | Medium | Low
- **clinical_significance**: Descriptive text
- **recommendation**: Clinical guidance

## ❌ Error Handling

### HTTP Status Codes
- **200**: Success
- **400**: Bad Request (validation errors)
- **429**: Too Many Requests (rate limit exceeded)
- **500**: Internal Server Error
- **503**: Service Unavailable (health check failed)

### Error Response Format
```json
{
  "error": "Error description",
  "status": "error",
  "message": "Detailed error message",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### Validation Error Response
```json
{
  "error": "Input validation failed",
  "status": "error",
  "details": [
    "Drug 1: Missing required field 'logp'",
    "Drug 2: Field 'plasma_protein_binding' must be between 0 and 100"
  ]
}
```

## 💻 Client Examples

### Python
```python
import requests

# Basic prediction request
url = "http://localhost:5000/predict-interactions"
data = {
    "drugs": [
        {
            "drug_name": "Warfarin",
            "pharmacodynamic_class": "Anticoagulant",
            "logp": 2.7,
            "therapeutic_index": "NTI",
            "transporter_interaction": "Substrate: P-gp",
            "plasma_protein_binding": 99.0,
            "metabolic_pathways": "Substrate: CYP2C9;CYP3A4"
        },
        {
            "drug_name": "Amiodarone",
            "pharmacodynamic_class": "Antiarrhythmic",
            "logp": 7.6,
            "therapeutic_index": "NTI",
            "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp",
            "plasma_protein_binding": 96.0,
            "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
        }
    ]
}

response = requests.post(url, json=data)
result = response.json()

if response.status_code == 200:
    print(f"Analysis successful!")
    print(f"Pairs analyzed: {result['drug_pairs_analyzed']}")
    for prediction in result['predictions']:
        drug_a = prediction['drug_pair']['drug_a']['name']
        drug_b = prediction['drug_pair']['drug_b']['name']
        severity = prediction['prediction']['severity']
        confidence = prediction['prediction']['confidence']
        print(f"{drug_a} + {drug_b}: {severity} ({confidence:.1%} confidence)")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

### JavaScript (Node.js)
```javascript
const axios = require('axios');

async function predictInteractions() {
    const url = 'http://localhost:5000/predict-interactions';
    const data = {
        drugs: [
            {
                drug_name: "Warfarin",
                pharmacodynamic_class: "Anticoagulant",
                logp: 2.7,
                therapeutic_index: "NTI",
                transporter_interaction: "Substrate: P-gp",
                plasma_protein_binding: 99.0,
                metabolic_pathways: "Substrate: CYP2C9;CYP3A4"
            },
            {
                drug_name: "Amiodarone",
                pharmacodynamic_class: "Antiarrhythmic",
                logp: 7.6,
                therapeutic_index: "NTI",
                transporter_interaction: "Substrate: P-gp / Inhibitor: P-gp",
                plasma_protein_binding: 96.0,
                metabolic_pathways: "Substrate: CYP3A4 / Inhibitor: CYP2D6"
            }
        ]
    };

    try {
        const response = await axios.post(url, data);
        console.log('Analysis successful!');
        console.log(`Pairs analyzed: ${response.data.drug_pairs_analyzed}`);
        
        response.data.predictions.forEach(prediction => {
            const drugA = prediction.drug_pair.drug_a.name;
            const drugB = prediction.drug_pair.drug_b.name;
            const severity = prediction.prediction.severity;
            const confidence = (prediction.prediction.confidence * 100).toFixed(1);
            console.log(`${drugA} + ${drugB}: ${severity} (${confidence}% confidence)`);
        });
    } catch (error) {
        console.error('Error:', error.response?.data?.error || error.message);
    }
}

predictInteractions();
```

### cURL
```bash
# Basic health check
curl -X GET http://localhost:5000/

# Prediction request
curl -X POST http://localhost:5000/predict-interactions \
  -H "Content-Type: application/json" \
  -d '{
    "drugs": [
      {
        "drug_name": "Warfarin",
        "pharmacodynamic_class": "Anticoagulant",
        "logp": 2.7,
        "therapeutic_index": "NTI",
        "transporter_interaction": "Substrate: P-gp",
        "plasma_protein_binding": 99.0,
        "metabolic_pathways": "Substrate: CYP2C9;CYP3A4"
      },
      {
        "drug_name": "Amiodarone",
        "pharmacodynamic_class": "Antiarrhythmic",
        "logp": 7.6,
        "therapeutic_index": "NTI",
        "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp",
        "plasma_protein_binding": 96.0,
        "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
      }
    ]
  }'
```

## 📚 SDKs and Libraries

### Python SDK
```python
# Install: pip install drug-interaction-client
from drug_interaction_client import DrugInteractionAPI

client = DrugInteractionAPI(base_url="http://localhost:5000")

# Add drugs
client.add_drug(
    name="Warfarin",
    pharmacodynamic_class="Anticoagulant",
    logp=2.7,
    therapeutic_index="NTI",
    transporter_interaction="Substrate: P-gp",
    plasma_protein_binding=99.0,
    metabolic_pathways="Substrate: CYP2C9;CYP3A4"
)

# Predict interactions
results = client.predict_interactions()
```

### JavaScript SDK
```javascript
// Install: npm install drug-interaction-client
import { DrugInteractionAPI } from 'drug-interaction-client';

const client = new DrugInteractionAPI('http://localhost:5000');

// Add drugs and predict
const results = await client.predictInteractions([
    { /* drug 1 data */ },
    { /* drug 2 data */ }
]);
```

## 🔧 Troubleshooting

### Common Issues

1. **Validation Errors**
   - Ensure all required fields are present
   - Check numeric ranges (logp: -10 to 15, plasma_protein_binding: 0-100)
   - Verify therapeutic_index is "NTI" or "Non-NTI"

2. **Rate Limiting**
   - Implement exponential backoff
   - Cache results when possible
   - Consider upgrading to higher rate limits

3. **Timeout Errors**
   - Reduce number of drugs per request
   - Check network connectivity
   - Verify server health status

4. **Model Errors**
   - Check `/health` endpoint for component status
   - Verify model files are present and accessible
   - Review server logs for detailed error information

### Support
For additional support, please contact: support@example.com
