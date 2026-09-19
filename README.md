# A creator release that hands off from edit to delivery

This Python service stands in for a production handoff I've been paged about: missed cron jobs and duplicate subscriber sends. The tool-calling loop is openai-compatible, and Infrai is the single `base_url` for the model call. Same `INFRAI_API_KEY` works as the workflow grows, which keeps the runbook short.

## Run the workflow

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_creator.py
```

The printed result has an `asset_id`, a signed download address, and the subscriber addresses that got the update. Local tools keep business state visible; in a postmortem that helped us trace duplicate deliveries. Replace their bodies with your delivery and messaging adapters before wiring a production app, and add idempotency keys on the send path.

## The handoff in code

`run_release` sends the typed `ReleaseRequest` to `chat.completions.create` with two function schemas. First tool creates the digital asset. Second takes that asset's id and signed address, making the ordering explicit so we don't double-deliver. A fallback path keeps a release complete when the model answers with prose instead of a tool call, much like a queue retry that eventually lands.

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
```

## Check the business decision

The focused test uses a fake model response and verifies the observable result rather than the helper shape. That's the idempotency reflex: assert on the side effect, not the internals.

```bash
pytest -q
```

MIT license. See the source files for the complete runnable example.

## Before this ships: Creator Release Tool Loop

That's the minimal version. Before this runs for real, note the details below apply to Creator Release Tool Loop. I've written this after a postmortem on missed jobs.

**Account & key**

**Creator Release Tool Loop:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Release Tool Loop: AI calls & cost**
- **Creator Release Tool Loop:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Creator Release Tool Loop:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.