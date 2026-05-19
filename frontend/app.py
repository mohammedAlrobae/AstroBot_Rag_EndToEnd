"""
Chainlit frontend for AstroBot — Mission Control Assistant.
Sends queries to the FastAPI backend and displays answers with sources.
"""

import chainlit as cl
import httpx

API_URL = "http://localhost:8000"
TIMEOUT = httpx.Timeout(120.0, connect=10.0)


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

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                f"{API_URL}/api/chat",
                json={"query": query},
            )

            if response.status_code != 200:
                msg.content = f"❌ Error {response.status_code}: {response.text}"
                await msg.update()
                return

            data = response.json()
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

    except httpx.ConnectError:
        msg.content = (
            "❌ **Cannot connect to AstroBot backend.**\n\n"
            "Make sure the FastAPI server is running on `http://localhost:8000`.\n\n"
            "Start it with: `python -m backend.app.main`"
        )
        await msg.update()
    except httpx.TimeoutException:
        msg.content = "⏱️ Request timed out. Please try again."
        await msg.update()
    except Exception as e:
        msg.content = f"❌ Error: {str(e)}"
        await msg.update()
