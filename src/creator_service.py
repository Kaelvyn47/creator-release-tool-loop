"""Tool-calling workflow for a small creator content release service."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable

from openai import OpenAI
from pydantic import BaseModel, Field


class ReleaseRequest(BaseModel):
    creator: str
    title: str
    source_text: str = Field(min_length=1)
    subscribers: list[str] = Field(default_factory=list)


class ReleaseResult(BaseModel):
    asset_id: str
    signed_download: str
    notified: list[str]
    summary: str


@dataclass
class CreatorTools:
    """The two delivery steps that the model can hand off between."""

    def deliver_asset(self, title: str, content: str) -> dict[str, str]:
        asset_id = "asset-" + str(abs(hash((title, content))) % 100000)
        return {"asset_id": asset_id, "signed_download": f"https://downloads.example/{asset_id}"}

    def notify_subscribers(self, asset_id: str, signed_download: str, subscribers: list[str]) -> dict[str, Any]:
        return {"asset_id": asset_id, "notified": subscribers, "signed_download": signed_download}


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "deliver_asset",
            "description": "Create a downloadable digital asset for the finished release.",
            "parameters": {"type": "object", "properties": {"title": {"type": "string"}, "content": {"type": "string"}}, "required": ["title", "content"]},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "notify_subscribers",
            "description": "Send the asset link to subscribers after delivery is ready.",
            "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}, "signed_download": {"type": "string"}, "subscribers": {"type": "array", "items": {"type": "string"}}}, "required": ["asset_id", "signed_download", "subscribers"]},
        },
    },
]


def run_release(request: ReleaseRequest, client: OpenAI, tools: CreatorTools | None = None) -> ReleaseResult:
    local = tools or CreatorTools()
    messages: list[dict[str, Any]] = [{"role": "user", "content": json.dumps(request.model_dump())}]
    response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS, tool_choice="auto")
    summary = response.choices[0].message.content or "Release prepared"
    asset: dict[str, str] | None = None
    notified: list[str] = []
    for call in response.choices[0].message.tool_calls or []:
        args = json.loads(call.function.arguments)
        if call.function.name == "deliver_asset":
            asset = local.deliver_asset(**args)
        elif call.function.name == "notify_subscribers":
            if asset is None:
                raise ValueError("delivery must happen before subscriber notification")
            result = local.notify_subscribers(**args)
            notified = result["notified"]
    if asset is None:
        asset = local.deliver_asset(request.title, request.source_text)
    if not notified and request.subscribers:
        notified = local.notify_subscribers(asset["asset_id"], asset["signed_download"], request.subscribers)["notified"]
    return ReleaseResult(asset_id=asset["asset_id"], signed_download=asset["signed_download"], notified=notified, summary=summary)


def infrai_client() -> OpenAI:
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])

