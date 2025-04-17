## 🩺 SMART-on-FHIR Patient Dashboard

A simple Flask-based SMART-on-FHIR app that securely launches inside an EHR-like environment, requests authorization via SMART, and visualizes clinical data (Conditions, Medications, Observations) for a selected patient.

### 🚀 Features

- SMART on FHIR compliant (using OAuth 2.0)
- Automatically discovers `.well-known/smart-configuration` to find auth endpoints
- Displays:
  - 🧑‍⚕️ Patient name
  - 📋 Conditions
  - 💊 Medications
  - 🔬 Vital sign Observations
  - 📈 Plotly chart of vitals over time
- Works with public SMART App Launcher

### 🧪 Data Source

This app uses **synthetic patient data** provided by the [SMART Health IT App Launcher](https://launch.smarthealthit.org), which simulates a real SMART-on-FHIR environment using the HAPI FHIR server underneath.

### 📦 Requirements

- Python 3.8+
- `pip install flask requests`

### 🧰 How to Run It

```bash
python app.py
```

Then go to:  
**[https://launch.smarthealthit.org](https://launch.smarthealthit.org)**

- Select **"EHR Launch"**
- Paste in:  
  ```
  http://localhost:8000/launch
  ```
- Pick a patient
- Click **Launch App**

### ✅ Supported SMART Flow

- [x] EHR Launch (`?iss=...&launch=...`)
- [x] SMART discovery from `.well-known/smart-configuration`
- [x] Token exchange via `POST`
- [x] Patient-specific FHIR resource fetching with `access_token`

### 🛡️ Security Notes

- This app uses `client_id="my-smart-app"` for the public sandbox.
- No client secrets required.
- For real deployment, use HTTPS, secure secrets, and register a private client.
