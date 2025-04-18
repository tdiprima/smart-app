"""
SMART Launcher: App's Launch URL = http://localhost:8000/launch
"""
import requests
from flask import Flask, request, redirect, render_template
from flask import session
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")  # Use environment variable for production

AUTH_BASE = "https://launch.smarthealthit.org/v/r4/sim/eyJhIjoiMSJ9"
FHIR_BASE = f"{AUTH_BASE}/fhir"
CLIENT_ID = "my-smart-app"
REDIRECT_URI = "http://localhost:8000/callback"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/launch")
def launch():
    iss = request.args.get("iss")
    launch_token = request.args.get("launch")

    if not iss or not launch_token:
        return "<h2>🚫 Error: Missing SMART launch parameters.</h2>"

    # Discover .well-known config
    try:
        discovery = requests.get(f"{iss}/.well-known/smart-configuration").json()
        auth_endpoint = discovery["authorization_endpoint"]
        token_endpoint = discovery["token_endpoint"]
    except Exception as e:
        return f"<h2>🚫 Failed to discover SMART config: {e}</h2>"

    # Store for callback
    session["token_endpoint"] = token_endpoint
    session["iss"] = iss

    # Redirect to SMART auth
    auth_url = (
        f"{auth_endpoint}?"
        f"response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope=launch patient/*.read openid profile"
        f"&aud={iss}"
        # f"&aud={FHIR_BASE}"
        f"&launch={launch_token}"
        f"&state=123"  # TODO: State should be random per request, not fixed
    )
    return redirect(auth_url)


@app.route("/callback")
def callback():
    # print("FULL CALLBACK URL:", request.url)
    code = request.args.get("code")

    if not code:
        return "<h2>🚫 No code returned from authorization step.</h2>"

    # Grab stored token endpoint and FHIR base
    token_url = session.get("token_endpoint")
    iss = session.get("iss")

    if not token_url or not iss:
        return "<h2>🚫 Session expired or invalid SMART launch.</h2>"

    token_response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})

    # print("Token Status:", token_response.status_code)
    # print("Token Response:", token_response.text)

    token_data = token_response.json()
    access_token = token_data.get("access_token")
    patient_id = token_data.get("patient")

    if not access_token or not patient_id:
        return "<h2>🚫 Token exchange failed.</h2>"

    headers = {"Authorization": f"Bearer {access_token}"}

    # Patient call using discovered iss
    patient = requests.get(f"{iss}/Patient/{patient_id}", headers=headers).json()
    name = patient.get("name", [{}])[0]
    full_name = f"{name.get('given', ['?'])[0]} {name.get('family', '?')}"

    # return f"<h1>✅ Success!</h1><p>Patient: {full_name} (ID: {patient_id})</p>"

    # Get conditions
    conditions = requests.get(f"{FHIR_BASE}/Condition?patient={patient_id}", headers=headers).json().get("entry", [])
    cond_list = [c["resource"]["code"]["text"] for c in conditions if "code" in c["resource"]]
    cond_list.sort()

    # Get medications
    meds = requests.get(f"{FHIR_BASE}/MedicationRequest?patient={patient_id}", headers=headers).json().get("entry", [])
    med_list = [m["resource"]["medicationCodeableConcept"]["text"] for m in meds if
                "medicationCodeableConcept" in m["resource"]]
    med_list.sort()

    # Get observations
    obs = requests.get(f"{FHIR_BASE}/Observation?patient={patient_id}", headers=headers).json().get("entry", [])
    chart_obs = []
    obs_list = []

    # Filter only specific vital types
    allowed_obs = ["Body Weight", "Systolic Blood Pressure", "Diastolic Blood Pressure", "Heart rate"]

    for o in obs:
        res = o["resource"]
        code = res.get("code", {}).get("text", "Unknown")
        if code not in allowed_obs:
            continue  # skip anything we don't want charted

        val = res.get("valueQuantity", {}).get("value")
        unit = res.get("valueQuantity", {}).get("unit", "")
        time = res.get("effectiveDateTime", "")

        if val is not None:
            obs_list.append({"label": code, "value": f"{val} {unit}"})
            chart_obs.append({
                "label": code,
                "num": val,
                "time": time
            })

    return render_template("dashboard.html",
        patient={"name": full_name},
        conditions=cond_list,
        medications=med_list,
        observations=obs_list,
        chart_obs=chart_obs
    )


if __name__ == "__main__":
    app.run(port=8000, debug=True)
