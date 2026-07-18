# LLM Council 🏛️

**Automated multi-model debate for architecture decisions — on 100% free LLM APIs.**

Before committing weeks to a big technical decision, submit it to a council of AI agents with
deliberately **conflicting mandates** — a statistical purist, a survival-obsessed risk manager, a
buildability realist, a build-vs-buy pragmatist, and a steelman advocate. They argue over multiple
rounds, each seeing and rebutting the others. A non-voting **Critic** then reviews the debate for
groupthink, and a **Chair** issues a calibrated verdict: **BUILD / BUY / DEFER / DROP** plus one
concrete next action. The full transcript is saved as Markdown (Obsidian-friendly).

Born as the decision engine for ARIA, a solo-built algorithmic trading learning project, where the
rule is *debate before build, prove before risk*.

## Why conflicting incentives?
A single AI advisor tends to agree with you. Give each agent an opposing mandate and weak ideas get
attacked from several directions at once — an idea only survives if it withstands the quant's demand
for evidence, the risk manager's fear of ruin, the engineer's buildability test, and the pragmatist's
"why not just buy it?" challenge. The Advocate seat ensures the *strongest case for* is also on the
table, so the council doesn't reject everything by default.

## Features
- **Genuinely different models disagree** — seats run across model families (GPT-4.1, Llama 4,
  DeepSeek R1, Gemini, Grok…) via GitHub Models and Google AI Studio, all on free tiers.
- **Per-topic panels** — pick seats per decision (`--seats quant,risk,advocate,nlp`), or add a
  `seats: ...` line to a topic file. Domain seats included: NLP/data-signal and compliance.
- **Reflection pass** — a Critic flags groupthink and blind spots before the verdict.
- **Chair calibration** — the Chair may not be more cautious than the most cautious seat without
  stating a justification (prevents "DEFER → DROP" overshoot).
- **Self-healing model IDs** — model names drift on free catalogs; the script validates each seat
  against the live catalog and swaps stale IDs for sensible equivalents (never a vision/code model).
- **Rate-limit aware** — paced calls, 429-aware backoff, and bounded prompts that respect the 8K
  input cap on free endpoints.

## Quickstart
```bash
pip install openai            # every provider speaks the OpenAI Chat API
cp .env.example .env          # add your free keys (GitHub token needs models:read)

python council.py --models                                  # list models your token can reach
python council.py "Should we build X or buy it?"            # default 5-seat panel, 3 rounds
python council.py --topic-file topics/example-topic.md      # rich topic + custom panel
python council.py "..." --seats quant,risk,advocate --rounds 2   # lean & fast
```

Verdicts are written to `ARIA_DEBATES_DIR` (default: `../02 - Council Debates`, set it in `.env`).

## Free keys (no credit card)
| Key | Where | Unlocks |
|---|---|---|
| `GITHUB_TOKEN` | GitHub → Settings → Developer settings → fine-grained PAT, **models:read** permission | GPT-4.1, Llama 4, DeepSeek R1, Mistral, Grok 3 — one key, whole council |
| `GOOGLE_API_KEY` | aistudio.google.com | Gemini Flash |
| `GROQ_API_KEY` / `CEREBRAS_API_KEY` | consoles | optional speed/volume backups |

**Free-tier realities** (learned the hard way): reasoning models (DeepSeek R1) have the tightest
quotas — use them for single-shot roles (Critic), not per-round seats. Gemini's daily cap resets on
US Pacific time. Big panels × many rounds × many reruns will hit limits; the lean panel
(`--seats quant,risk,advocate` + `--rounds 2`) is the reliable daily driver.

## The seats
| Seat | Mandate | Core question |
|---|---|---|
| Quant Purist | Statistical-edge zealot | Evidence, or just a story? |
| Risk Manager | Survival-obsessed permabear | What's the worst case — does it end the game? |
| Systems Engineer | Buildability realist | Can one person build & maintain this in time? |
| Pragmatist | Build-vs-buy challenger | Why build what already exists? |
| Advocate | Steelman | What's the strongest honest case FOR? |
| Data-Signal Specialist | NLP/quant-data expert | Is there a real, extractable signal? |
| Compliance & Data-Rights | Regulation & ToS | Is this legal and licence-clean? |
| Critic *(non-voting)* | Reflection pass | Where's the groupthink? What was missed? |
| Chair | Calibrated synthesis | BUILD / BUY / DEFER / DROP + one next action |

## License
MIT — see [LICENSE](LICENSE).
