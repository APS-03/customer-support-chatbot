import React, { useState } from "react";
import axios from "axios";
import "./ChatBot.css"; // Optional: move styles here

function ChatBot() {
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);

  const handleSend = async () => {
    if (!input) return;

  const userMessage = { sender: "user", message: input };
  setChat((prev) => [...prev, userMessage]);

  try {
    const response = await axios.post("http://localhost:8000/chat", {
      message: input,
    });

    const botMessage = { sender: "bot", message: response.data.response };
    setChat((prev) => [...prev, botMessage]);
  } catch (error) {
    console.error("Error:", error);
    const errorMessage = {
      sender: "bot",
      message: "⚠️ Sorry, I couldn’t connect to the server.",
    };
    setChat((prev) => [...prev, errorMessage]);
  }

  setInput("");
  };

  return (
    <div className="chat-container">
      <h2>🛍️ E-Commerce Support Bot</h2>
      <div className="chat-box">
        {chat.map((msg, idx) => (
          <div key={idx} className={`chat-msg ${msg.sender}`}>
            <span><b>{msg.sender === "user" ? "You" : "Bot"}:</b> {msg.message}</span>
          </div>
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask a question..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default ChatBot;
