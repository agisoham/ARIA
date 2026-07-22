# ARIA Council Engine

Automated multi-model architecture debate. You name a decision → four persona-models
argue it over rounds → a Grok Chair issues a verdict (**BUILD / BUY / DEFER / DROP** +
one next action) → the transcript is filed in `../02 - Council Debates/`.

## The free keys you need (no credit card, ever)

| Key | Where to get it (free) | Unlocks |
|---|---|---|
| `GITHUB_TOKEN` | github.com → Settings → Developer settings → **Personal access tokens** (fine-grained, no scopes needed for Models) | GPT-4.1, DeepSeek R1, Llama 4, Mistral, **Grok 3** — the whole council in one key |
| `GOOGLE_API_KEY` | **aistudio.google.com** → *Get API key* (your working Google/UPI account) | Gemini Flash — your native rail |
| `GROQ_API_KEY` *(optional)* | **console.groq.com** → API Keys | fast Llama 3.3 70B |
| `CEREBRAS_API_KEY` *(optional)* | **cloud.cerebras.ai** → API Keys | ~1M tokens/day |

GitHub Models alone is enough to run the full council. The others are speed/volume backups.

## Run it

```bash
pip install openai --break-system-packages
export GITHUB_TOKEN=...            # and GOOGLE_API_KEY=... if you want Gemini seats

python council.py --models         # print the exact model ids your token can reach
python council.py "Should ARIA commit to the Dual Barbell split?" --rounds 2
```

The verdict `.md` appears in the Codex automatically.

## Notes
- Every seat speaks the OpenAI Chat API, so all providers use one client.
- GitHub Models has low free limits (~10–15 req/min, 8K-in/4K-out); the script paces
  calls and only feeds each agent the most recent round to stay inside the window.
- Model ids drift — if a seat errors, run `--models` and paste a current id into
  `COUNCIL` / `CHAIR` at the top of `council.py`.
- Swap any seat to Gemini/Groq/Cerebras by changing its `provider` + `model`.

## Two-layer screening
No verdict is trusted on a single pass. After Layer 1 (debate → Critic → calibrated Chair),
**Layer 2** automatically re-screens the result:
- **Bias Auditor** names the systemic bias in the panel's composition/framing most likely to have
  skewed the verdict (survivability-bias, status-quo bias, novelty-aversion…).
- **Red Team** argues the verdict is *wrong*, using the audited bias + the Critic's missed points,
  and names the alternative verdict.
- **Chair** issues a second-layer ruling: **CONFIRM** or **REVISE** (with the same calibration rule).

Every debate file gets a "Layer 2 — Re-screening" section. Add `--layer1-only` to skip it (saves
~3 calls on quota-tight days).

## Roles, reflection & calibration
- **Panel is configurable per topic.** Available seats: `quant, risk, systems, pragmatist,
  advocate, nlp, compliance`. Default = quant, risk, systems, pragmatist, advocate.
  - Set them with `--seats quant,risk,advocate,nlp` **or** a `seats: ...` line at the top of a topic file.
- **Advocate seat** steelmans the proposal so the board never rejects by default (fixes the
  built-in "everyone defaults to caution" bias).
- **Reflection pass:** a non-voting **Critic** reviews the debate for groupthink and blind spots
  before the Chair rules.
- **Chair calibration:** the Chair may not return a verdict more cautious than the most cautious
  individual seat without stating a justification (stops DEFER→DROP overshoot).
