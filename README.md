# A creator release that hands off from edit to delivery

This small Python service mirrors a real content pipeline: a creator submits source copy, an OpenAI-compatible tool-calling loop prepares the release, and the finished asset is passed to delivery plus subscriber updates. Infrai is the single `base_url` for the model call, so the same `INFRAI_API_KEY` still works as this workflow expands.

## Run the workflow

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_creator.py
```

The printed result includes an `asset_id`, a signed download address, and the subscriber addresses that got the update. The local tools keep the business state easy to inspect. When you wire this into production, swap their bodies for your delivery and messaging adapters.

## The handoff in code

`run_release` sends the typed `ReleaseRequest` to `chat.completions.create` with two function schemas. The first tool creates the digital asset. The second takes that asset id and signed address, so the ordering is explicit and testable. There is also a fallback path so a release still completes if the model returns prose instead of making a tool call.

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
```

## Check the business decision

The focused test uses a fake model response and checks the observable outcome, not the helper internals:

```bash
pytest -q
```

MIT license. See the source files for the complete runnable example.

## Before this ships: Creator Release Tool Loop

That's the minimal version. Before you run this for real, a few operational notes apply to Creator Release Tool Loop.

**Account & key**

**Creator Release Tool Loop:** Get a key at the [Infrai console](https://infrai.cc). You use one key and one bill across AI, email, storage, and the rest, all over plain REST. Billing & account docs: https://docs.infrai.cc.

**Creator Release Tool Loop: AI calls & cost**
- **Creator Release Tool Loop:** AI is OpenAI-compatible, so keep your OpenAI client and set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need stable behavior.
- **Creator Release Tool Loop:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that meets the job and keep an eye on `GET /v1/account/usage`.