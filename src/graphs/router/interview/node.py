import asyncio
import json
import os
from typing import Annotated, TypedDict
import uuid

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from src import db


model = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
)


class State(TypedDict):
    area_id: uuid.UUID
    extract_data_tasks: asyncio.Queue[uuid.UUID]
    messages: Annotated[list[BaseMessage], add_messages]
    was_covered: bool


async def interview(state: State):
    area_id = state["area_id"]
    last_area_msg = db.LifeAreaMessages(
        id=uuid.uuid7(),
        data=state["messages"][-1].content,
        area_id=area_id,
    )
    db.LifeAreaMessages.create(last_area_msg.id, last_area_msg)

    area_msgs: list[str] = [
        msg.data
        for msg in db.LifeAreaMessages.list_by_area(area_id)
    ]
    area_criteria: list[str] = [
        c.title for c in db.Criteria.list_by_area(area_id)
    ]

    ai_answer, was_covered = await check_criteria_covered(area_msgs, area_criteria)
    if was_covered:
        await state["extract_data_tasks"].put(area_id)

    return {"messages": [AIMessage(content=ai_answer)], "was_covered": was_covered}


async def check_criteria_covered(
    interview_messages: list[str],
    area_criteria: list[str],
) -> tuple[str, bool]:
    """
    The agent:
    - Evaluates each criterion
    - Decides whether all are covered
    - Generates the NEXT assistant message (question or thank-you)
    """

    system_prompt = (
        "You are an interview agent.\n"
        "Your task:\n"
        "1. Decide for EACH criterion whether it is clearly covered by the interview\n"
        "2. If ALL criteria are covered → thank the interviewee and close politely\n"
        "3. If NOT all covered → ask about ONE uncovered criterion (the most logical next one)\n\n"
        "Rules:\n"
        "- Be strict: unclear or partial answers = NOT covered\n"
        "- Ask only ONE question\n"
        "- Be polite, natural, and conversational\n"
        "- Respond ONLY with valid JSON\n\n"
        "JSON format:\n"
        "{\n"
        '  "criteria": [\n'
        '    {"title": "<criterion>", "covered": true | false}\n'
        "  ],\n"
        '  "all_covered": true | false,\n'
        '  "final_answer": "<assistant message to send to user>"\n'
        "}\n"
    )

    user_prompt = {
        "interview_messages": interview_messages,
        "criteria": area_criteria,
    }

    response = await model.ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_prompt)},
        ]
    )

    data = json.loads(response.content)

    final_answer: str = data.get("final_answer", "")
    all_covered: bool = data.get("all_covered", False)

    return final_answer, all_covered
