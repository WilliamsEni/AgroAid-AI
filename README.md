# AgroAid AI

AgroAid AI is an agricultural assistance application built for the Bincom Hackathon.

The application is designed to help farmers identify possible crop and animal health problems by uploading or taking a photo of the affected crop or animal.

The current MVP provides the complete frontend workflow and infrastructure foundation. AI-powered diagnosis will be integrated in a later development stage.

## Live Application

AgroAid AI is publicly deployed at:

https://agroaid-ai.onrender.com

## Current MVP Features

- AgroAid AI farmer-focused interface
- Crop and animal selection
- Crop or animal type selection
- JPG, JPEG and PNG image upload
- Camera image capture
- Uploaded image preview
- Farmer symptom description
- Analyze Image workflow
- AI diagnosis placeholder
- Expert Help workflow placeholder
- Docker containerization
- GitHub Actions CI pipeline
- Public deployment on Render
- Application health monitoring

## Technology Stack

### Application

- Python 3.11
- Streamlit
- Pillow

### Infrastructure and DevOps

- Docker
- Git
- GitHub
- GitHub Actions
- Render

### Planned Integrations

- Vision-capable AI API
- SQLite or Supabase
- Agricultural specialist request system

## Project Structure

```text
AgroAid-AI/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── README.md
├── app.py
└── requirements.txt