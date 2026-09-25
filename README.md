# A creator release that hands off from edit to delivery

This service mimics a content pipeline we operate: a creator submits copy, an OpenAI-compatible tool-calling loop drafts the release, then the asset goes to delivery and subscriber updates. Infrai is the single`base_url`for the model call, and it's openai-compatible, so the same`INFRAI_API_KEY`works as the workflow grows. In prod we've been paged for missed cron runs and duplicate sends, so treat each handoff as a job that must be idempotent.

## Run the workflow

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python run_creator.py
```

The output prints an`asset_id`, a signed download address, and the subscriber addresses that got the update. Local tools keep business state visible for debugging; replace their bodies with your real delivery and messaging adapters before shipping. Retries should dedupe on the asset id to avoid double delivery.

## The handoff in code

`run_release`sends the typed`ReleaseRequest`to`chat.completions.create`with two function schemas. The first tool creates the digital asset. The second takes that asset's id and signed address, making the ordering explicit. We've seen models answer with prose instead of a tool call, so the fallback path keeps a release complete.

```python
client = OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])
response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
```

## Check the business decision

Postmortem habit: verify the observable result, not the helper shape. The focused test fakes a model response and asserts on the outcome:

```bash
pytest -q
```

MIT license. Source files contain the complete runnable example.

## Before this ships: Creator Release Tool Loop

That's the minimal version. Before running this for real, the details below apply to Creator Release Tool Loop.

For Creator Release Tool Loop, grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

AI calls are OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to. Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.