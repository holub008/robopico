# robopico

This project is a fork of [RobotReviewer](https://github.com/ijmarshall/robotreviewer). Its main objective is to 
provide a simple API around the core functionality RobotReviewer offers. 

## Features

* PI(C)O extraction: [Named-entity Recognition models](https://en.wikipedia.org/wiki/Named-entity_recognition) extract 
Patient/Problem, Intervention, and Outcome entities from article abstracts.
* Study Type prediction: Gradient boosted trees classify studies as RCTs, case reports, systematic reviews, and other 
using article abstracts.

Note that, while PICO extraction is based on peer reviewed work, study type prediction is unvetted. See 
`train/publication_type` for methods.

## Example
```sh
curl --header "Content-Type: application/json" --data '{"title": ["The AtRial Cardiopathy and Antithrombotic Drugs In prevention After cryptogenic stroke randomized trial: Rationale and methods."], "abstract": ["Recent data suggest that a thrombogenic atrial substrate can cause stroke in the absence of atrial fibrillation. Such an atrial cardiopathy may explain some proportion of cryptogenic strokes. The aim of the ARCADIA trial is to test the hypothesis that apixaban is superior to aspirin for the prevention of recurrent stroke in subjects with cryptogenic ischemic stroke and atrial cardiopathy. 1100 participants. Biomarker-driven, randomized, double-blind, active-control, phase 3 clinical trial conducted at 120 U.S. centers participating in NIH StrokeNet. Patients ≥ 45 years of age with embolic stroke of undetermined source and evidence of atrial cardiopathy, defined as ≥ 1 of the following markers: P-wave terminal force >5000 µV × ms in ECG lead V1, serum NT-proBNP > 250 pg/mL, and left atrial diameter index ≥ 3 cm/m2 on echocardiogram. Exclusion criteria include any atrial fibrillation, a definite indication or contraindication to antiplatelet or anticoagulant therapy, or a clinically significant bleeding diathesis. Intervention: Apixaban 5 mg twice daily versus aspirin 81 mg once daily. Analysis: Survival analysis and the log-rank test will be used to compare treatment groups according to the intention-to-treat principle, including participants who require open-label anticoagulation for newly detected atrial fibrillation. The primary efficacy outcome is recurrent stroke of any type. The primary safety outcomes are symptomatic intracranial hemorrhage and major hemorrhage other than intracranial hemorrhage. ARCADIA is the first trial to test whether anticoagulant therapy reduces stroke recurrence in patients with atrial cardiopathy but no known atrial fibrillation."]}' localhost:5050/pico
```

Results in:

```json
[
  {
    "interventions": [
      "Apixaban 5\u2009mg twice daily versus aspirin", 
      "apixaban", 
      "anticoagulant therapy", 
      "aspirin", 
      "Intervention"
    ], 
    "interventions_mesh": [
      {
        "cui": "C1831808", 
        "mesh_term": "apixaban", 
        "mesh_ui": "C522181"
      }, 
      {
        "cui": "C0004057", 
        "mesh_term": "Aspirin", 
        "mesh_ui": "D001241"
      }, 
      {
        "cui": "C0003280", 
        "mesh_term": "Anticoagulants", 
        "mesh_ui": "D000925"
      }, 
      {
        "cui": "C0087111", 
        "mesh_term": "Therapeutics", 
        "mesh_ui": "D013812"
      }
    ], 
    "outcomes": [
      "stroke recurrence", 
      "recurrent stroke of any type", 
      "symptomatic intracranial hemorrhage and major hemorrhage other than intracranial hemorrhage"
    ], 
    "outcomes_mesh": [
      {
        "cui": "C0038454", 
        "mesh_term": "Stroke", 
        "mesh_ui": "D020521"
      }, 
      {
        "cui": "C2825055", 
        "mesh_term": "Recurrence", 
        "mesh_ui": "D012008"
      }, 
      {
        "cui": "C0151699", 
        "mesh_term": "Intracranial Hemorrhages", 
        "mesh_ui": "D020300"
      }, 
      {
        "cui": "C0019080", 
        "mesh_term": "Hemorrhage", 
        "mesh_ui": "D006470"
      }
    ], 
    "population": [
      "120 U.S. centers participating in NIH StrokeNet", 
      "participants who require open-label anticoagulation for newly detected atrial fibrillation", 
      "1100 participants", 
      "patients with atrial cardiopathy but no known atrial fibrillation", 
      "subjects with cryptogenic ischemic stroke and atrial cardiopathy", 
      "Patients\u2009\u2265\u200945 years of age with embolic stroke of undetermined source and evidence of atrial cardiopathy, defined as\u2009\u2265\u20091 of the following markers: P-wave terminal force >5000\u2009\u00b5V\u2009\u00d7\u2009ms in ECG lead V1, serum NT-proBNP\u2009>\u2009250\u2009pg/mL, and left atrial diameter index\u2009\u2265\u20093\u2009cm/m2 on echocardiogram"
    ], 
    "population_mesh": [
      {
        "cui": "C0004238", 
        "mesh_term": "Atrial Fibrillation", 
        "mesh_ui": "D001281"
      }, 
      {
        "cui": "C0030705", 
        "mesh_term": "Patient", 
        "mesh_ui": "D010361"
      }, 
      {
        "cui": "C0018799", 
        "mesh_term": "Heart Diseases", 
        "mesh_ui": "D006331"
      }, 
      {
        "cui": "C0038454", 
        "mesh_term": "Stroke", 
        "mesh_ui": "D020521"
      }, 
      {
        "cui": "C0001811", 
        "mesh_term": "Aging", 
        "mesh_ui": "D000375"
      }, 
      {
        "cui": "C1623258", 
        "mesh_term": "Electrocardiography", 
        "mesh_ui": "D004562"
      }, 
      {
        "cui": "C0023175", 
        "mesh_term": "Lead", 
        "mesh_ui": "D007854"
      }, 
      {
        "cui": "C0229671", 
        "mesh_term": "Serum", 
        "mesh_ui": "D044967"
      }, 
      {
        "cui": "C0754710", 
        "mesh_term": "Amino-terminal pro-brain natriuretic peptide", 
        "mesh_ui": "C109794"
      }, 
      {
        "cui": "C0600653", 
        "mesh_term": "Index", 
        "mesh_ui": "D020481"
      }, 
      {
        "cui": "C0013516", 
        "mesh_term": "Echocardiography", 
        "mesh_ui": "D004452"
      }
    ], 
    "study_type": {
      "Case Report": 0.00025277058011852205, 
      "Other": 0.013372665271162987, 
      "RCT": 0.9858561754226685, 
      "Systematic Review": 0.0005183960893191397
    }
  }
]
```

## Deploying

### Development

After cloning the repository, install the project with:
```sh
pipenv install 
```

Start the server:
```sh
pipenv run python server.py
```
The server will be available at  `http://localhost:5050`- note startup time is 5-10 seconds, due to loading large models.

### Production

Run the flask app behind a production grade server using WSGI. Gunicorn is the default option of this project

```sh
venv/bin/gunicorn --bind localhost:8000 wsgi:app —-timeout 5000
```