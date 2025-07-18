# Drug Interaction Prediction API

A production-ready Flask web server that provides drug-drug interaction prediction using a trained XGBoost machine learning model. The API accepts multiple drug characteristics and returns interaction severity predictions with confidence scores.

## Features

- **Machine Learning Powered**: Uses a trained XGBoost model for accurate predictions
- **Multiple Drug Support**: Analyzes interactions between multiple drugs in a single request
- **Comprehensive Analysis**: Provides severity levels (Major, Moderate, Minor) with confidence scores
- **Production Ready**: Includes Docker support, proper logging, and error handling
- **Input Validation**: Comprehensive validation with informative error messages
- **Clinical Recommendations**: Provides actionable clinical guidance for each interaction

## API Endpoints

### `GET /`
Health check endpoint that returns server status and model information.

### `POST /predict-interactions`
Main prediction endpoint that accepts drug data and returns interaction analysis.

### `GET /api/info`
Returns API documentation and usage information.

## Input Format

Send a POST request to `/predict-interactions` with the following JSON structure:

```json
{
  "drugs": [
    {
      "drug_name": "Codeine",
      "pharmacodynamic_class": "Opioid Analgesic",
      "logp": 1.45,
      "therapeutic_index": "Non-NTI",
      "transporter_interaction": "Substrate: P-gp",
      "plasma_protein_binding": 25.0,
      "metabolic_pathways": "Substrate: CYP2D6;CYP3A4"
    },
    {
      "drug_name": "Abiraterone",
      "pharmacodynamic_class": "Androgen Synthesis Inhibitor",
      "logp": 5.12,
      "therapeutic_index": "Non-NTI",
      "transporter_interaction": "Substrate: P-gp / Inhibitor: P-gp;BCRP",
      "plasma_protein_binding": 99.0,
      "metabolic_pathways": "Substrate: CYP3A4 / Inhibitor: CYP2D6"
    }
  ]
}
```

## Response Format

The API returns detailed interaction analysis:

```json
{
  "status": "success",
  "timestamp": "2024-01-01T12:00:00",
  "input_drugs_count": 2,
  "drug_pairs_analyzed": 1,
  "predictions": [
    {
      "drug_pair": {
        "drug_a": {"index": 0, "name": "Codeine", "class": "Opioid Analgesic"},
        "drug_b": {"index": 1, "name": "Abiraterone", "class": "Androgen Synthesis Inhibitor"}
      },
      "prediction": {
        "severity": "Moderate",
        "confidence": 0.85,
        "risk_level": "Medium"
      },
      "probability_distribution": {
        "Major": 0.15,
        "Moderate": 0.85,
        "Minor": 0.00
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

## Installation and Setup

### Option 1: Docker (Recommended)

1. **Clone the repository and ensure you have the required files:**
   - `xgboost_model.pkl` (trained model)
   - `preprocessing_config.py` (preprocessing configuration)

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Or build and run with Docker:**
   ```bash
   docker build -t drug-interaction-api .
   docker run -p 5000:5000 drug-interaction-api
   ```

### Option 2: Local Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env file as needed
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

   Or with Gunicorn for production:
   ```bash
   gunicorn -c gunicorn.conf.py app:app
   ```

## Configuration

The application can be configured using environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 5000)
- `DEBUG`: Debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)

## Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:5000/

# Prediction request
curl -X POST http://localhost:5000/predict-interactions \
  -H "Content-Type: application/json" \
  -d '{
    "drugs": [
      {
        "drug_name": "Test Drug A",
        "pharmacodynamic_class": "Antibiotic",
        "logp": 2.5,
        "therapeutic_index": "Non-NTI",
        "transporter_interaction": "Substrate: P-gp",
        "plasma_protein_binding": 85.0,
        "metabolic_pathways": "Substrate: CYP3A4"
      },
      {
        "drug_name": "Test Drug B",
        "pharmacodynamic_class": "Antidepressant",
        "logp": 3.2,
        "therapeutic_index": "Non-NTI",
        "transporter_interaction": "No Transporter",
        "plasma_protein_binding": 92.0,
        "metabolic_pathways": "Substrate: CYP2D6"
      }
    ]
  }'
```

## Deployment

### Heroku
1. Create a `Procfile`:
   ```
   web: gunicorn -c gunicorn.conf.py app:app
   ```

2. Deploy:
   ```bash
   git add .
   git commit -m "Deploy drug interaction API"
   git push heroku main
   ```

### AWS/GCP/Azure
Use the provided Dockerfile for container-based deployment on cloud platforms.

## Model Information

- **Algorithm**: XGBoost Classifier
- **Features**: 78 engineered features including drug characteristics and interactions
- **Output**: Severity levels (Major, Moderate, Minor) with confidence scores
- **Training Data**: MolePure dataset with 15,000 drug interaction samples

## API Limits

- Maximum 10 drugs per request
- Request timeout: 120 seconds
- Rate limiting: 100 requests per minute (configurable)

## Error Handling

The API provides comprehensive error messages for:
- Invalid input format
- Missing required fields
- Out-of-range values
- Server errors

## Support

For issues or questions, please check the API documentation at `/api/info` endpoint or review the validation schema.
