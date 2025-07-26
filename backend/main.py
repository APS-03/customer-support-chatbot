from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rapidfuzz import process
import pandas as pd

app = FastAPI()

# Enable CORS for Vite (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    message: str

# Load your dataset
df = pd.read_csv("data/datasets/distribution_centers.csv")

# Combine columns into Q&A format
df['name_lower'] = df['name'].str.lower()
questions = df["name_lower"].tolist()
id_lookup = df.set_index("name_lower").to_dict(orient="index")

@app.post("/chat")
async def chat_endpoint(msg: Message):
    user_msg = msg.message.lower()

    match, score, _ = process.extractOne(user_msg, questions)
    if match and score > 60:  # Lowered threshold for more flexible matching
        result = id_lookup.get(match)
        return {
            "response": f"📍 *{df.loc[df['name_lower'] == match, 'name'].values[0]}*\nLatitude: {result['latitude']}, Longitude: {result['longitude']}"
        }
    else:
        return {
            "response": "❓ I'm sorry, I couldn't find a relevant location. Try asking with a city name like 'Chicago' or 'Memphis'."
        }
