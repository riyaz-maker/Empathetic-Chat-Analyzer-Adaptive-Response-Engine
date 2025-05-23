!pip install datasets
!pip install nltk

import pandas as pd
from datasets import load_dataset
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import string

nltk.download('punkt')
nltk.download('stopwords')

dataset = load_dataset("empathetic_dialogues")
print(dataset)

df_train = dataset['train'].to_pandas()
df_train.head()

nltk.download('punkt_tab')

stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    #Convert text to lowercase
    text = text.lower()

    #Remove URLs
    text = re.sub(r'http\S+', '', text)

    #Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))

    #Remove numeric characters
    text = re.sub(r'\d+', '', text)

    #Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    #Tokenization
    tokens = word_tokenize(text)

    #Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]

    #Rejoin tokens
    cleaned_text = ' '.join(tokens)

    return cleaned_text

#Apply preprocessing on utterances
df_train['cleaned_utterance'] = df_train['utterance'].apply(preprocess_text)
df_train[['utterance', 'cleaned_utterance']].head()

df_train.to_csv('empathetic_dialogues_cleaned.csv', index=False)

!pip install transformers datasets evaluate -q
!pip install -q accelerate

from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
import pandas as pd
import torch

"""tokenizing and training the pretrained model"""

import pandas as pd

df = pd.read_csv("empathetic_dialogues_cleaned.csv")

#Map emotions to labels
label2id = {label: idx for idx, label in enumerate(df['context'].unique())}
id2label = {idx: label for label, idx in label2id.items()}
df['label'] = df['context'].map(label2id)

df = df[['cleaned_utterance', 'context']].dropna()
df['cleaned_utterance'] = df['cleaned_utterance'].astype(str)
df['context'] = df['context'].astype(str)

#Rebuild labels
label2id = {label: idx for idx, label in enumerate(df['context'].unique())}
id2label = {idx: label for label, idx in label2id.items()}
df['label'] = df['context'].map(label2id)

from datasets import Dataset

dataset = Dataset.from_pandas(df[['cleaned_utterance', 'label']])

from transformers import AutoTokenizer
from datasets import Dataset

tokenizer = AutoTokenizer.from_pretrained("roberta-base")

#Convert DataFrame
dataset = Dataset.from_pandas(df[['cleaned_utterance', 'label']])

#Tokenization function
def tokenize_function(example):
    return tokenizer(example["cleaned_utterance"], padding="max_length", truncation=True)

#Apply tokenization
tokenized_dataset = dataset.map(tokenize_function, batched=True)

#Split into train and test sets
tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2)

from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    "roberta-base",
    num_labels=len(label2id),
    id2label=id2label,
    label2id=label2id
)

"""training"""

from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=20,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    load_best_model_at_end=True,
    warmup_steps=500,
    gradient_accumulation_steps=2,
    fp16=True,
)

#AdamW with custom param groups
from torch.optim import AdamW

def get_optimizer(model):
    no_decay = ["bias", "LayerNorm.weight"]
    optimizer_grouped_parameters = [
        {
            "params": [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
            "weight_decay": 0.01,
        },
        {
            "params": [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
            "weight_decay": 0.0,
        },
    ]
    return AdamW(optimizer_grouped_parameters, lr=2e-5)

from sklearn.metrics import accuracy_score, f1_score

def compute_metrics(p):
    preds = p.predictions.argmax(-1)
    return {
        'accuracy': accuracy_score(p.label_ids, preds),
        'f1': f1_score(p.label_ids, preds, average='weighted')
    }

from transformers import Trainer

class CustomTrainer(Trainer):
    def create_optimizer(self):
        self.optimizer = get_optimizer(self.model)

trainer = CustomTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['test'],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

trainer.train()

trainer.save_model("empathetic-transformer")
tokenizer.save_pretrained("empathetic-transformer")

pip install fastapi uvicorn google-generativeai

import os
from getpass import getpass
import google.generativeai as genai
from transformers import pipeline

#Gemini API key from environment
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    gemini_api_key = getpass("Enter your Gemini API key: ")

#Configure Gemini API
genai.configure(api_key=gemini_api_key)
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI(title="Empathetic Adaptive Response Engine")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Empathetic Adaptive Response Engine! Visit /docs for API details."}

class ChatRequest(BaseModel):
    user_message: str
    emotion: str

#For automatic emotion detection
class AutoChatRequest(BaseModel):
    user_message: str

emotion_classifier = pipeline(
    "text-classification",
    model="empathetic-transformer",
    tokenizer="empathetic-transformer",
    return_all_scores=False
)

def build_prompt(user_message: str, emotion: str) -> str:
    prompt = f"""
You are an empathetic and supportive AI assistant.
The user is currently feeling {emotion}.
User says: "{user_message}"
Generate a compassionate, thoughtful, and contextually appropriate response.
"""
    return prompt

@app.post("/auto_generate_response", summary="Auto Generate a Response",
          description="Automatically detects the user's emotion from their message and returns an empathetic response.")
async def auto_generate_response(chat_req: AutoChatRequest):
    try:
        classifier_output = emotion_classifier(chat_req.user_message)
        predicted_emotion = classifier_output[0]["label"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in emotion classification: {e}")

    prompt = build_prompt(chat_req.user_message, predicted_emotion)
    try:
        response = gemini_model.generate_content(prompt)
        response_text = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Gemini API: {e}")

    return {"detected_emotion": predicted_emotion, "response": response_text}

@app.post("/generate_response", summary="Generate a Response (Manual)",
          description="Generates an empathetic response based on user input and provided emotion (manual input).")
async def generate_response(chat_req: ChatRequest):
    prompt = build_prompt(chat_req.user_message, chat_req.emotion)
    try:
        response = gemini_model.generate_content(prompt)
        response_text = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error with Gemini API: {e}")
    return {"response": response_text}

#WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            user_message = data.get("message")
            if not user_message:
                await websocket.send_json({"error": "Invalid input, missing 'message'"})
                continue
            try:
                classifier_output = emotion_classifier(user_message)
                predicted_emotion = classifier_output[0]["label"]
            except Exception as e:
                await websocket.send_json({"error": f"Error in emotion classification: {str(e)}"})
                continue

            #Build and send prompt to gemini
            prompt = build_prompt(user_message, predicted_emotion)
            try:
                response = gemini_model.generate_content(prompt)
                response_text = response.text
            except Exception as e:
                await websocket.send_json({"error": f"Error with Gemini API: {str(e)}"})
                continue
            await websocket.send_json({"detected_emotion": predicted_emotion, "response": response_text})
        except Exception as e:
            await websocket.close()
            break

!pip install pyngrok
from pyngrok import ngrok
import nest_asyncio
nest_asyncio.apply()

public_url = ngrok.connect(8000)
print("Public URL:", public_url)

import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
