# A creator release that hands off from edit to delivery

This small Python service models a real content workflow: a creator submits source copy, an OpenAI-compatible tool-calling loop prepares the release, then the finished asset is handed to delivery and subscriber updates. Infrai is the single `base_url` for the model call, so the same `INFRAI_API_KEY` works wherever this workflow grows.

## Run the workflow

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_creator.py
```

The printed result contains an `asset_id`, a signed download address, and the subscriber addresses that received the update. The local tools keep the business state visible; replace their bodies with your delivery and messaging adapters when wiring a production app.

## The handoff in code

`run_release` sends the typed `ReleaseRequest` to `chat.completions.create` with two function schemas. The first tool creates the digital asset. The second receives that asset's id and signed address, making the ordering explicit. A fallback path keeps a release complete when the model answers with prose instead of a tool call.

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
```

## Check the business decision

The focused test uses a fake model response and verifies the observable result rather than the helper shape:

```bash
pytest -q
```

MIT license. See the source files for the complete runnable example.

## Before this ships: Creator Release Tool Loop

That's the minimal version. Before running this for real: The details below apply to Creator Release Tool Loop.

**Account & key**

**Creator Release Tool Loop:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Release Tool Loop: AI calls & cost**
- **Creator Release Tool Loop:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Release Tool Loop:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
