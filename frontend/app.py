"""
Chainlit frontend for AstroBot — Mission Control Assistant.
Sends queries to the FastAPI backend and displays answers with sources.
"""

import chainlit as cl
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")


def call_backend(query: str) -> dict:
    try:
        response = requests.post(
            f"{API_URL}/api/chat",
            json={"query": query},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Check if FastAPI is running."}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. The backend took too long to respond."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "🚀 **AstroBot online.** I have full access to the NASA Artemis II Reference Guide.\n\n"
            "Ask me anything about the mission, crew, spacecraft, systems, or procedures.\n\n"
            "I also handle general space questions and emergency protocols."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    query = message.content.strip() if message.content else ""
    if not query:
        return

    # Show thinking indicator
    msg = cl.Message(content="🔍 *Searching mission database...*")
    await msg.send()

    data = call_backend(query)

    if "error" in data:
        msg.content = f"❌ {data['error']}"
        await msg.update()
        return

    answer = data.get("answer", "No answer received.")
    sources = data.get("sources", [])

    # Build the response with sources
    full_response = answer

    if sources:
        full_response += "\n\n---\n"
        for src in sources:
            page = src.get("page", "?")
            score = src.get("score", 0)
            full_response += f"\n📄 Source: Artemis II Reference Guide · Page {page} · Score: {score:.0%}"

    msg.content = full_response
    await msg.update()
