from __future__ import annotations

import logging
from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import openai


load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("my-worker")
logger.setLevel(logging.INFO)


async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()

    run_multimodal_agent(ctx, participant)

    logger.info("agent started")


def run_multimodal_agent(ctx: JobContext, participant: rtc.RemoteParticipant):
    logger.info("starting multimodal agent")

    model = openai.realtime.RealtimeModel(
        instructions=(
            "You are an AI broker assistant designed to help clients with stock market investments, real estate, and financial planning"
            "Your role is to provide personalized advice, real-time market insights, and help clients make informed decisions"
            "You can analyze stock trends, offer suggestions for portfolio diversification, and answer questions about specific investment opportunities"
            "You should be clear, concise, and always prioritize the client's best financial interests while ensuring that you explain any risks involved"
            "Your responses should be based on real-time data and user preferences."
            "You love Bulgaria."),
        modalities=["audio", "text"],
    )

    assistant = MultimodalAgent(model=model)
    assistant.start(ctx.room, participant)
    session= model.sessions[0]
    session.conversation.item.create(
        llm.ChatMessage(
            role="user",
            content="Please begin the interaction with the user in a manner consistent with your instructions"
            
        )
    )
    session.response.create()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        )
    )
    
    #lk sip inbound create inbound-trunk.json
    #lk sip dispatch create dispatch-rule.json
    #lk sip outbound create outbound-trunk.json
