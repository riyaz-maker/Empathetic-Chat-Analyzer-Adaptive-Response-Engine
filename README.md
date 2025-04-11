# Empathetic-Chat-Analyzer-Adaptive-Response-Engine
A microservice that is built using sentiment analysis and emotion detection using Gemini and RoBERTa-base. This service would analyze user inputs in real time, gauge emotional states, and adapt responses to better match the user’s mood.
## Features
### Automatic Emotion Detection:
Uses a fine-tuned transformer model to classify user messages into emotions.

### Adaptive Response Generation:
Integrates Gemini 2.0 Flash API to generate responses tailored to the detected emotion.

### Real-Time Interaction:
Provides both RESTful and WebSocket endpoints for real-time communication.

### Scalable & Modular:
Developed with FastAPI for a clean, modular architecture.

## Technology Used
### Deployment:
Uvicorn for ASGI server, compatible with local and cloud environments.

### LLMs & NLP:
Hugging Face Transformers for emotion detection (using a fine-tuned classification model).
Google Gemini API 2.0 Flash for generating empathetic, context-aware responses.

### Tunneling (for remote development):
ngrok for exposing local servers (when using Google Colab).

## LLM & Gemini Integration
This project leverages two components:

### Emotion Detection via Transformers:
A fine-tuned RoBERTa-base emotion classifier (based on a transformer model) is used to detect the user's emotional state from their message.

### Response Generation with Gemini API:
The Gemini 2.0 Flash API from Google is used for generating natural, empathetic responses based on dynamic prompt templates.

# Screenshots
![447B652B-A51E-4329-9D31-3A6E0BAB8139_1_201_a](https://github.com/user-attachments/assets/76c8a6df-9fab-4291-a8a6-b951982deb52)

![41F0AE0E-DE4B-472A-86C9-FF76970BE1D3_1_201_a](https://github.com/user-attachments/assets/4fb3fbb9-000b-4a13-b460-1a4adc4c5c7a)

![70CEAC16-F789-4A90-9C7A-1740EBCC0BBA_1_201_a](https://github.com/user-attachments/assets/7f0f7766-6693-4cd3-8205-8c15abbc3e1c)

![7BC40F80-8CE7-413D-B08C-54A75DF99961_1_201_a](https://github.com/user-attachments/assets/ec53a95c-0ca9-4c9c-92a2-fd409b549b86)

![C8FB5B6E-F8AE-4097-9BA1-010E09397004_1_201_a](https://github.com/user-attachments/assets/e33c0d16-7298-416c-a40c-5e5d198e08f3)

![B2F441D2-1985-452F-91C0-BD1CBAE3EDB7_1_201_a](https://github.com/user-attachments/assets/4fc29ab8-8a45-4c1b-809e-c94c3ff1d7b8)
