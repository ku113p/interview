import asyncio
import json
import os
from pathlib import Path
from typing import Annotated, TypedDict
import uuid

from langchain_core.messages import AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages

from src import db


def get_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise ValueError("OPENROUTER_API_KEY is required")
    return api_key


model = ChatOpenAI(
    model="google/gemini-2.0-flash-001",
    api_key=get_api_key,
    base_url="https://openrouter.ai/api/v1",
)

PROMPT_LINES = [
    "You are an interview agent.",
    "Your task:",
    "1. Decide for EACH criterion whether it is clearly covered by the interview",
    "2. If ALL criteria are covered -> thank the interviewee and close politely",
    "3. If NOT all covered -> ask about ONE uncovered criterion (the most logical next one)",
    "",
    "Rules:",
    "- Be strict: unclear or partial answers = NOT covered",
    "- Ask only ONE question",
    "- Be polite, natural, and conversational",
    "- Respond ONLY with valid JSON",
    "",
    "JSON format:",
    "{",
    '  "criteria": [',
    '    {"title": "<criterion>", "covered": true | false}',
    "  ],",
    '  "all_covered": true | false,',
    '  "final_answer": "<assistant message to send to user>"',
    "}",
]


class State(TypedDict):
    area_id: uuid.UUID
    extract_data_dir: str
    messages: Annotated[list[BaseMessage], add_messages]
    was_covered: bool


async def interview(state: State):
    area_id = state["area_id"]
    last_content = get_last_content(state["messages"][-1])
    last_area_msg = db.LifeAreaMessageObject(
        id=uuid.uuid7(),
        data=last_content,
        area_id=area_id,
        created_ts=0,
    )
    db.LifeAreaMessages.create(last_area_msg.id, last_area_msg)

    area_msgs: list[str] = [
        msg.data for msg in db.LifeAreaMessages.list_by_area(area_id)
    ]
    area_criteria: list[str] = [c.title for c in db.Criteria.list_by_area(area_id)]

    ai_answer, was_covered = await check_criteria_covered(area_msgs, area_criteria)
    if was_covered:
        write_area_signal(state["extract_data_dir"], area_id)

    return {"messages": [AIMessage(content=ai_answer)], "was_covered": was_covered}


def get_last_content(message: BaseMessage) -> str:
    content = message.content
    if not isinstance(content, str):
        raise ValueError("Invalid message content")
    return content


async def check_criteria_covered(
    interview_messages: list[str],
    area_criteria: list[str],
) -> tuple[str, bool]:
    messages = build_messages(interview_messages, area_criteria)
    response = await model.ainvoke(messages)
    return extract_cover_result(response.content)


def parse_llm_json(content: object):
    if not isinstance(content, str):
        raise ValueError("Invalid LLM response")
    return json.loads(content)


def build_messages(interview_messages: list[str], area_criteria: list[str]):
    return [
        {"role": "system", "content": build_system_prompt()},
        {
            "role": "user",
            "content": build_user_prompt_json(interview_messages, area_criteria),
        },
    ]


def build_system_prompt() -> str:
    return "\n".join(PROMPT_LINES)


def build_user_prompt_json(interview_messages: list[str], area_criteria: list[str]):
    payload = {"interview_messages": interview_messages, "criteria": area_criteria}
    return json.dumps(payload)


def extract_cover_result(content: object) -> tuple[str, bool]:
    data = parse_llm_json(content)
    final_answer = data.get("final_answer", "")
    all_covered = data.get("all_covered", False)
    return final_answer, all_covered


def write_area_signal(directory: str, area_id: uuid.UUID) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)
    signal_path = Path(directory) / str(area_id)
    signal_path.write_text("ready")
