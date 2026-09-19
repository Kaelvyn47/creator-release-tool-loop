import json
from types import SimpleNamespace

from src.creator_service import CreatorTools, ReleaseRequest, run_release


class FakeClient:
    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        calls = [
            SimpleNamespace(function=SimpleNamespace(name="deliver_asset", arguments=json.dumps({"title": "Clip", "content": "Edited"}))),
            SimpleNamespace(function=SimpleNamespace(name="notify_subscribers", arguments=json.dumps({"asset_id": "asset-1", "signed_download": "https://downloads.example/asset-1", "subscribers": ["sam@example.com"]}))),
        ]
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Ready", tool_calls=calls))])


def test_tool_handoff_delivers_before_notification():
    result = run_release(ReleaseRequest(creator="Mina", title="Clip", source_text="Edited", subscribers=["sam@example.com"]), FakeClient(), CreatorTools())
    assert result.signed_download.startswith("https://downloads.example/")
    assert result.notified == ["sam@example.com"]

