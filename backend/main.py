# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from rapidfuzz import process
# import pandas as pd
# import os

# app = FastAPI()

# # ✅ Allow your frontend origin explicitly
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],  # <-- Your frontend origin
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# class Message(BaseModel):
#     message: str

# # Load all CSVs from dataset folder
# datasets = []
# DATA_PATH = os.path.join("data", "datasets")

# if os.path.exists(DATA_PATH):
#     for filename in os.listdir(DATA_PATH):
#         if filename.endswith(".csv"):
#             filepath = os.path.join(DATA_PATH, filename)
#             df = pd.read_csv(filepath)
#             datasets.append((filename, df))
#     print(f"✅ Loaded {len(datasets)} datasets.")
# else:
#     print(f"❌ Dataset folder not found at {DATA_PATH}")

# @app.post("/chat")
# async def chat(msg: Message):
#     user_input = msg.message.lower()
#     best_score = 0
#     best_answer = None
#     matched_file = None

#     for filename, df in datasets:
#         for col in df.columns[:-1]:  # Assume last column is the answer
#             questions = df[col].dropna().astype(str).tolist()
#             match, score, _ = process.extractOne(user_input, questions)
#             if score > best_score:
#                 best_score = score
#                 matched_file = filename
#                 matched_row = df[df[col] == match]
#                 best_answer = matched_row.iloc[0][-1] if not matched_row.empty else None

#     if best_score > 70 and best_answer:
#         return {
#             "response": best_answer,
#             "score": best_score,
#             "source": matched_file
#         }
#     else:
#         return {
#             "response": "❓ I'm sorry, I couldn't find a relevant answer. Can you rephrase it?",
#             "score": best_score
#         }
# import pandas as pd
# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from difflib import get_close_matches
# from fastapi.responses import JSONResponse

# app = FastAPI()

# # CORS to allow frontend access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:5173"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load CSV
# df_centers = pd.read_csv('data/datasets/distribution_centers.csv')

# # Create list of names for fuzzy match
# names_list = df_centers['name'].tolist()

# class ChatRequest(BaseModel):
#     message: str

# @app.post("/chat")
# def chat_endpoint(req: ChatRequest):
#     user_msg = req.message.lower()

#     # Fuzzy match for center name
#     match = get_close_matches(user_msg, names_list, n=1, cutoff=0.5)

#     if match:
#         result = df_centers[df_centers['name'] == match[0]].iloc[0].to_dict()
#         return JSONResponse(content={"answer": f"Here's the info for {match[0]}", "data": result})
#     else:
#         return JSONResponse(content={"answer": "Sorry, I couldn't find a matching distribution center."})

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
