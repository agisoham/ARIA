#!/usr/bin/env python3
"""
ARIA Council — automated multi-model architecture debate.

You name a decision; a configurable panel of persona-models argues it over N rounds,
each seeing and rebutting the prior arguments. A CRITIC then reviews the debate for
groupthink and blind spots (a reflection pass), and a CHAIR synthesises a calibrated
verdict (BUILD / BUY / DEFER / DROP + one concrete next action). The full transcript,
reflection, and verdict are written to the Codex under "02 - Council Debates".

All models run on FREE, no-credit-card tiers (GitHub Models, Google Gemini, Groq, Cerebras).
Everything speaks the OpenAI Chat API, so one client class covers all.

Usage:
    python council.py --models                        # list reachable GitHub models
    python council.py "Should ARIA do X?"             # default panel, 3 rounds
    python council.py --topic-file topics/x.md        # read decision (and optional seats) from a file
    python council.py "..." --seats quant,risk,advocate,nlp --rounds 2

Per-topic roles: pass --seats, or put a line like `seats: quant, risk, nlp, compliance`
at the top of a topic file. Available seats: quant, risk, systems, pragmatist, advocate,
nlp, compliance.
"""

import argparse
import datetime as dt
import os
import re
import sys
import time

try:
    from openai import OpenAI
except ImportError:
    sys.exit("Install the client first:  pip install openai")


def _load_dotenv() -> None:
    """Load key=value pairs from a local .env next to this script, if present."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.exists(path):
        return
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip().strip('"').strip("'")
        if v:
            os.environ.setdefault(k.strip(), v)


_load_dotenv()

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

_HERE = os.path.dirname(os.path.abspath(__file__))
DEBATES_DIR = os.environ.get("ARIA_DEBATES_DIR", os.path.join(_HERE, "..", "02 - Council Debates"))

PROVIDERS = {
    "github":   ("https://models.github.ai/inference",                       "GITHUB_TOKEN"),
    "google":   ("https://generativelanguage.googleapis.com/v1beta/openai/", "GOOGLE_API_KEY"),
    "groq":     ("https://api.groq.com/openai/v1",                           "GROQ_API_KEY"),
    "cerebras": ("https://api.cerebras.ai/v1",                               "CEREBRAS_API_KEY"),
}

# A library of seats. Pick which ones debate per topic (see --seats / topic-file "seats:").
SEAT_LIBRARY = {
    "quant": dict(
        name="Quant Purist", provider="github", model="openai/gpt-4.1",
        mandate="You are the QUANT PURIST: a statistical-edge zealot. You trust only measured, "
                "out-of-sample evidence and are hostile to narratives, curve-fitting, and overfit "
                "backtests. Core question: 'Is there measured, out-of-sample evidence — or just a story?'"),
    "risk": dict(
        name="Risk Manager", provider="github", model="meta/llama-4-scout-17b-16e-instruct",
        mandate="You are the RISK MANAGER: a survival-obsessed permabear. Your job is to ensure the game "
                "never ends. You reason from worst cases, tail risk, and ruin, under the hard rule 'never "
                "lose money'. Core question: 'What is the worst case, and does it end the game?'"),
    "systems": dict(
        name="Systems Engineer", provider="github", model="meta/llama-4-scout-17b-16e-instruct",
        mandate="You are the SYSTEMS ENGINEER: a buildability realist. One solo developer, finite time, "
                "free tooling only. Core question: 'Can one person actually build and maintain this in time?'"),
    "pragmatist": dict(
        name="Pragmatist", provider="github", model="openai/gpt-4.1",
        mandate="You are the PRAGMATIST: a build-vs-buy challenger. You ask why we'd build what an existing "
                "platform (Streak, AlgoTest, AlgoBulls) already does. Core question: 'Why build this when an "
                "existing platform already does it?'"),
    "advocate": dict(
        name="Advocate", provider="github", model="meta/llama-4-scout-17b-16e-instruct",
        mandate="You are the ADVOCATE (steelman). Your mandate is to build the STRONGEST honest, evidence-aware "
                "case FOR the proposal — the version its smartest proponent would give. You are NOT a cheerleader: "
                "use real mechanisms and evidence. Your job is to ensure the best case is on the table so the "
                "council never rejects by default. Core question: 'What's the strongest reason this SHOULD be done, "
                "and what would have to be true for it to win?'"),
    "nlp": dict(
        name="Data-Signal Specialist", provider="github", model="openai/gpt-4.1",
        mandate="You are the DATA-SIGNAL SPECIALIST: an NLP/quant-data expert. You judge whether a proposed signal "
                "carries real, extractable, non-overfit information — data availability, labelling, look-ahead "
                "leakage, signal-to-noise, and how you'd validate it. Core question: 'Is there a real, measurable "
                "signal here, and can it be extracted without overfitting or leakage?'"),
    "compliance": dict(
        name="Compliance & Data-Rights", provider="github", model="openai/gpt-4.1",
        mandate="You are the COMPLIANCE & DATA-RIGHTS seat: you know SEBI's retail-algo framework, exchange/broker "
                "terms, and data-source ToS/licensing. You flag legal, regulatory, and terms-of-service risk. Core "
                "question: 'Is this legal and within every relevant rule and licence — and what's the compliant way?'"),
}

DEFAULT_SEATS = ["quant", "risk", "systems", "pragmatist", "advocate"]

# The Critic runs a reflection pass; it does not vote.
CRITIC = dict(
    name="Critic", provider="github", model="openai/gpt-4.1",
    mandate="You are the CRITIC. You do NOT vote. Review the debate for quality: (1) name the single strongest "
            "argument on each side, (2) flag any GROUPTHINK or shared bias where the seats converged too easily "
            "(e.g. everyone defaulting to caution), (3) name the most important consideration the council MISSED. "
            "Be brief and specific.")

# ---- Layer 2: re-screening (bias audit + red team + second ruling) ----
# Every Layer-1 verdict is stress-tested a second time: audit the panel's systemic bias,
# red-team the verdict using the Critic's missed considerations, then CONFIRM or REVISE.
LAYER2_AUDITOR = dict(
    name="Bias Auditor", provider="github", model="openai/gpt-4.1",
    mandate="You are the BIAS AUDITOR. You do NOT re-argue the decision — you audit the PROCESS. "
            "Name the single systemic bias in this panel's composition or framing most likely to have "
            "skewed the verdict (e.g. survivability-bias toward DEFER/DROP, status-quo bias, "
            "novelty-aversion, solo-builder timidity), and the one consideration the whole panel "
            "structurally under-weighted. Be concrete and brief.")
LAYER2_REDTEAM = dict(
    name="Red Team", provider="google", model="gemini-3.5-flash",
    mandate="You are the RED TEAM. Your sole job is to argue that the Layer-1 verdict is WRONG. Use the "
            "audited bias and the Critic's missed considerations to build the strongest possible case for a "
            "DIFFERENT verdict, and state which one (BUILD / BUY / DEFER / DROP) it points to.")

# The Chair synthesises — with an explicit calibration rule against over-cautious verdicts.
CHAIR = dict(
    name="Chair", provider="github", model="openai/gpt-4.1",
    mandate="You are the CHAIR. You synthesise; you do not take a side during the debate. "
            "CALIBRATION RULE — verdict severity order, most to least cautious: DROP > DEFER > BUY > BUILD. "
            "Your verdict must NOT be more cautious than the most cautious *individual seat vote* unless you state, "
            "in one sentence, a specific justification for overriding it. Reflect the genuine balance of the debate "
            "and weigh the Advocate's best case fairly.")

ARIA_CONTEXT = """\
PROJECT: ARIA — a solo-built algorithmic trading system targeting BOTH Indian markets (NSE/BSE) and US
markets. PRIMARY GOAL is learning ML, quant finance, and systems engineering. HARD RULE: never lose money
(survivability first). Earning real money is a genuine goal too, but strictly within all applicable
regulations: SEBI rules and broker terms for India; for US access as an Indian resident — RBI's LRS
(USD 250k/yr remittance cap, ~20% TCS on large remittances), W-8BEN (0% US capital-gains tax for Indian
residents, 25% treaty rate on dividends), SEC/FINRA rules (PDT rule eliminated 2026), and US broker terms
(e.g. Alpaca offers free unlimited paper trading via API; IBKR for full market access). Architecture is the
Dual Barbell: a conservative Core (80-90%) walled off from a small, capped Aggressive Alpha sleeve (10-20%).
Builder is a solo 18-year-old in India with no budget and only free-tier tooling. Currently Phase 0:
architecture, no trading code yet. Method: debate before build; prove before risk; protect the Core always."""

REQUEST_PAUSE = 6.0
MAX_RETRIES = 5

# --------------------------------------------------------------------------- #
# Client helpers
# --------------------------------------------------------------------------- #

_clients: dict[str, OpenAI] = {}


def client_for(provider: str) -> OpenAI:
    if provider not in _clients:
        base_url, key_env = PROVIDERS[provider]
        key = os.environ.get(key_env)
        if not key:
            raise RuntimeError(f"Missing API key: set {key_env} for provider '{provider}'.")
        _clients[provider] = OpenAI(base_url=base_url, api_key=key)
    return _clients[provider]


def ask(seat: dict, system: str, user: str, max_tokens: int = 1500) -> str:
    client = client_for(seat["provider"])
    for attempt in range(MAX_RETRIES):
        try:
            resp = client.chat.completions.create(
                model=seat["model"],
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                max_tokens=max_tokens, temperature=0.7,
            )
            time.sleep(REQUEST_PAUSE)
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:  # noqa: BLE001
            name = e.__class__.__name__
            is_rl = "RateLimit" in name or "429" in str(e)
            wait = 30.0 if is_rl else REQUEST_PAUSE * (2 ** attempt)  # rate windows reset per-minute
            msg = str(e).replace("\n", " ")[:120]
            print(f"   ! {seat['name']} error ({name}: {msg}); retry in {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
    return f"[{seat['name']} did not respond after {MAX_RETRIES} attempts.]"


def _strip_think(text: str) -> str:
    """Remove chain-of-thought <think>...</think> blocks (reasoning models leak them)."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<think>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
    return text.strip()


# --------------------------------------------------------------------------- #
# Model catalogs + self-healing
# --------------------------------------------------------------------------- #

_BAD_KINDS = ("vision", "embed", "codestral", "-code", "ocr", "guard",
              "tts", "whisper", "rerank", "audio", "image", "moderation")
_GOOD_MARKERS = ("large", "medium", "small", "instruct", "chat", "flash",
                 "pro", "4.1", "4o", "mini", "70b", "r1", "grok")


def github_catalog_ids() -> list[str]:
    import httpx
    _, key_env = PROVIDERS["github"]
    token = os.environ.get(key_env, "")
    for url in ("https://models.github.ai/catalog/models", "https://models.github.ai/inference/models"):
        try:
            r = httpx.get(url, headers={"Authorization": f"Bearer {token}",
                                        "Accept": "application/vnd.github+json"}, timeout=30)
            r.raise_for_status()
            data = r.json()
            items = data.get("data", data) if isinstance(data, dict) else data
            ids = [m.get("id") or m.get("name") for m in items if isinstance(m, dict)]
            ids = [i for i in ids if i]
            if ids:
                return ids
        except Exception:  # noqa: BLE001
            continue
    return []


def google_model_ids() -> list[str]:
    import httpx
    base, key_env = PROVIDERS["google"]
    key = os.environ.get(key_env, "")
    if not key:
        return []
    try:
        r = httpx.get(base.rstrip("/") + "/models", headers={"Authorization": f"Bearer {key}"}, timeout=30)
        r.raise_for_status()
        data = r.json()
        items = data.get("data", data) if isinstance(data, dict) else data
        return [m["id"].split("/")[-1] for m in items if isinstance(m, dict) and m.get("id")]
    except Exception:  # noqa: BLE001
        return []


def heal_models(seats: list[dict]) -> None:
    """Validate each seat's model against the provider's live catalog (case-insensitively).
    Keep anything that exists; only replace genuinely-missing ids, never downgrading to a
    vision/code/embedding/image model."""
    gh = github_catalog_ids()
    gg = google_model_ids()
    gh_lower = {i.lower(): i for i in gh}
    gg_lower = {i.lower(): i for i in gg}
    gh_default = gh_lower.get("openai/gpt-4.1", gh[0] if gh else None)
    if not gh and not gg:
        print("   (catalogs unavailable; using configured ids as-is)")
        return
    for seat in seats:
        prov, want = seat["provider"], seat["model"].lower()
        if prov == "github" and gh:
            if want in gh_lower:
                seat["model"] = gh_lower[want]
                continue
            vendor = seat["model"].split("/")[0].split("-")[0].lower()
            cands = [i for i in gh if vendor in i.lower()]
            clean = [i for i in cands if not any(b in i.lower() for b in _BAD_KINDS)]
            pool = clean or cands
            pref = [i for i in pool if any(g in i.lower() for g in _GOOD_MARKERS)]
            choice = (pref or pool or ([gh_default] if gh_default else gh))[0]
        elif prov == "google" and gg:
            if want in gg_lower:
                seat["model"] = gg_lower[want]
                continue
            bad = ("image", "tts", "lite", "vision", "live", "native", "-exp", "embedding")
            cand = [g for g in gg if "flash" in g.lower() and not any(b in g.lower() for b in bad)]
            choice = (sorted(cand, reverse=True) or gg)[0]
        else:
            continue
        print(f"   · healed {seat['name']}: {seat['model']} -> {choice}")
        seat["model"] = choice


def list_github_models() -> None:
    ids = github_catalog_ids()
    print("\n".join(ids) if ids else "Could not read the GitHub Models catalog.")


# --------------------------------------------------------------------------- #
# Council assembly + debate
# --------------------------------------------------------------------------- #

def build_council(seat_ids: list[str]) -> list[dict]:
    council = []
    for sid in seat_ids:
        seat = SEAT_LIBRARY.get(sid.strip().lower())
        if seat:
            council.append(dict(seat))  # copy so healing doesn't mutate the library
        else:
            print(f"   (unknown seat '{sid}' — skipping; valid: {', '.join(SEAT_LIBRARY)})")
    return council or [dict(SEAT_LIBRARY[s]) for s in DEFAULT_SEATS]


def parse_seats(text: str):
    """Pull an optional 'seats: a, b, c' line from a topic; return (seat_ids|None, cleaned_text)."""
    m = re.search(r"^\s*(?:<!--\s*)?seats:\s*([a-z0-9_,\s]+?)\s*(?:-->)?\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return None, text
    ids = [s.strip().lower() for s in m.group(1).split(",") if s.strip()]
    cleaned = (text[:m.start()] + text[m.end():]).strip()
    return (ids or None), cleaned


def parse_models(text: str):
    """Pull an optional per-topic casting line and return (overrides, cleaned_text).

    Syntax (one line):  models: quant=github:deepseek/deepseek-r1, advocate=google:gemini-3.5-flash
    Maps seat id -> (provider, model). Lets each debate cast its strongest model
    into its pivotal seat without editing this file."""
    m = re.search(r"^\s*(?:<!--\s*)?models:\s*(.+?)\s*(?:-->)?\s*$", text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return {}, text
    overrides = {}
    for part in m.group(1).split(","):
        part = part.strip()
        if "=" not in part or ":" not in part:
            continue
        seat_id, spec = part.split("=", 1)
        provider, model = spec.split(":", 1)
        if provider.strip().lower() in PROVIDERS:
            overrides[seat_id.strip().lower()] = (provider.strip().lower(), model.strip())
    cleaned = (text[:m.start()] + text[m.end():]).strip()
    return overrides, cleaned


def layer2_screen(topic_brief: str, verdict: str, critique: str):
    """Layer 2: re-screen a Layer-1 verdict for systemic bias and missed considerations.
    Returns (audit, redteam, ruling)."""
    print("  · Layer 2: bias audit")
    audit = _strip_think(ask(
        LAYER2_AUDITOR, f"{LAYER2_AUDITOR['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}",
        f"DECISION:\n{topic_brief}\n\nLAYER-1 VERDICT:\n{verdict}\n\nCRITIC'S REVIEW:\n{critique[:1500]}\n\n"
        "Name the systemic bias and the structurally under-weighted consideration now. <150 words.",
        max_tokens=600))
    print("  · Layer 2: red team")
    redteam = _strip_think(ask(
        LAYER2_REDTEAM, f"{LAYER2_REDTEAM['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}",
        f"DECISION:\n{topic_brief}\n\nLAYER-1 VERDICT:\n{verdict}\n\nBIAS AUDIT:\n{audit[:1200]}\n\n"
        "Make the strongest case the Layer-1 verdict is WRONG, and name the alternative verdict. <180 words.",
        max_tokens=700))
    print("  · Layer 2: second-layer ruling")
    ruling = _strip_think(ask(
        CHAIR, f"{CHAIR['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}",
        f"DECISION:\n{topic_brief}\n\nLAYER-1 VERDICT:\n{verdict}\n\nBIAS AUDIT:\n{audit[:1000]}\n\n"
        f"RED TEAM:\n{redteam[:1200]}\n\nSecond-layer ruling: either **CONFIRM** (Layer-1 verdict survives "
        "re-screening) or **REVISE** to a stated verdict. One sentence of justification. Obey the calibration rule.",
        max_tokens=500))
    return audit, redteam, ruling


def load_rescreen(path: str):
    """Read a filed verdict and pull out (original_topic, prior_verdict, missed_considerations, bias)."""
    text = open(path, encoding="utf-8").read()
    cut = re.search(r"\n##\s*(Layer 1|Verdict)", text)
    topic = (text[:cut.start()] if cut else text).strip()
    def section(pat):
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else ""
    verdict = section(r"##\s*(?:Layer 1 . )?Verdict[^\n]*\n(.+?)(?:\n##|\Z)")[:700]
    missed = section(r"##\s*Reflection \(Critic\)\s*\n(.+?)(?:\n##|\Z)")[:1200]
    bias = section(r"Bias Auditor:\*{0,2}\s*(.+?)(?:\*\*Red Team|</details>|\Z)")[:800]
    return topic, verdict, missed, bias


def build_rescreen_topic(topic, verdict, missed, bias) -> str:
    parts = [topic, "\n\n## RE-SCREENING MANDATE",
             "This is a SECOND-PASS re-screening of a prior council verdict — question it afresh.",
             f"\nPRIOR VERDICT:\n{verdict}",
             f"\nMISSED CONSIDERATIONS flagged last time (address each directly):\n{missed or '(none recorded)'}"]
    if bias:
        parts.append(f"\nSYSTEMIC BIAS to consciously counteract this time:\n{bias}")
    parts.append("\nRe-debate on the merits: engage the missed considerations, correct for the bias, "
                 "and CONFIRM or OVERTURN the prior verdict — do not simply defer to it.")
    return "\n".join(parts)


def run_debate(topic: str, rounds: int, council: list[dict], screen2: bool = True, title: str = None) -> str:
    heal_models(council + [CRITIC, CHAIR] + ([LAYER2_AUDITOR, LAYER2_REDTEAM] if screen2 else []))
    print(f"\n=== DEBATE: {topic[:80]}{'...' if len(topic) > 80 else ''} ===")
    print("Panel: " + ", ".join(f"{s['name']}" for s in council) + f"  |  {rounds} rounds\n")

    transcript: list[tuple[str, str]] = []

    def digest(cap: int = 1200) -> str:
        recent = transcript[-len(council):]
        return "\n\n".join(f"### {who}\n{txt[:cap]}" for who, txt in recent) or "(no arguments yet)"

    for rnd in range(1, rounds + 1):
        print(f"--- Round {rnd}/{rounds} ---")
        for seat in council:
            system = f"{seat['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}"
            if rnd == 1:
                user = (f"DECISION UNDER DEBATE:\n{topic}\n\nGive your opening argument from your mandate. "
                        "Be specific and concise (<200 words). State your provisional vote: BUILD / BUY / DEFER / DROP.")
            else:
                user = (f"DECISION UNDER DEBATE:\n{topic}\n\nARGUMENTS SO FAR:\n{digest()}\n\n"
                        "Rebut the points you most disagree with and sharpen your own. Be concise (<200 words). "
                        "End with your current vote: BUILD / BUY / DEFER / DROP.")
            print(f"  · {seat['name']} ({seat['model']})")
            transcript.append((seat["name"], _strip_think(ask(seat, system, user))))

    # Build a bounded summary for synthesis — GitHub models cap input at ~8K tokens,
    # so feed only each seat's FINAL-round position (their sharpened argument + vote), trimmed.
    topic_brief = topic[:600]
    final_positions = "\n\n".join(
        f"### {who}\n{txt[:1200]}" for who, txt in transcript[-len(council):])

    # Reflection pass — the Critic reviews the final positions.
    print("  · Critic reviewing debate (reflection pass)")
    critique = _strip_think(ask(
        CRITIC, f"{CRITIC['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}",
        f"DECISION:\n{topic_brief}\n\nFINAL POSITIONS (last round):\n{final_positions}\n\nWrite your review now.",
        max_tokens=800))

    # Chair synthesis — sees the final positions AND the critique, with the calibration rule.
    print("  · Chair synthesising calibrated verdict")
    chair_user = (
        f"DECISION:\n{topic_brief}\n\nFINAL POSITIONS (last round):\n{final_positions}\n\n"
        f"CRITIC'S REVIEW:\n{critique[:2000]}\n\n"
        "Synthesise. Give: (1) a 3-4 sentence summary of the real disagreement, (2) the VERDICT in caps — "
        "BUILD, BUY, DEFER, or DROP — obeying the calibration rule, (3) ONE concrete next action. Keep it tight.")
    verdict = _strip_think(ask(CHAIR, f"{CHAIR['mandate']}\n\nARIA CONTEXT:\n{ARIA_CONTEXT}", chair_user, max_tokens=1000))

    layer2 = layer2_screen(topic_brief, verdict, critique) if screen2 else None

    return render_markdown(title or topic, rounds, council, transcript, critique, verdict, layer2)


def render_markdown(topic, rounds, council, transcript, critique, verdict, layer2=None) -> str:
    today = dt.date.today().isoformat()
    panel = ", ".join(f"{s['name']} (`{s['model']}`)" for s in council)
    lines = [f"# {topic}", "",
             f"*Automated council debate · {today} · {rounds} rounds · two-layer screening*", "",
             f"**Panel:** {panel}", "",
             "## Layer 1 — Verdict (Chair)", "", verdict, "",
             "## Reflection (Critic)", "", critique, ""]
    if layer2:
        audit, redteam, ruling = layer2
        lines += ["## Layer 2 — Re-screening", "",
                  "**Second-layer ruling:**", "", ruling, "",
                  "<details><summary>Bias audit &amp; red team</summary>", "",
                  "**Bias Auditor:** " + audit, "", "**Red Team:** " + redteam, "", "</details>", ""]
    lines += ["---", "", "## Full transcript", ""]
    per_round = len(council)
    model_by_name = {s["name"]: s["model"] for s in council}
    for i, (who, txt) in enumerate(transcript):
        if i % per_round == 0:
            lines.append(f"### Round {i // per_round + 1}\n")
        lines.append(f"**{who}** _(`{model_by_name.get(who, '')}`)_\n\n{txt}\n")
    return "\n".join(lines)


def save(topic: str, markdown: str) -> str:
    os.makedirs(DEBATES_DIR, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")[:60]
    path = os.path.join(DEBATES_DIR, f"{dt.date.today().isoformat()} - {slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return path


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> None:
    p = argparse.ArgumentParser(description="ARIA automated council debate")
    p.add_argument("topic", nargs="?", help="the decision to debate")
    p.add_argument("--topic-file", help="read the decision (and optional 'seats:' line) from a file")
    p.add_argument("--seats", help="comma-separated seats: " + ", ".join(SEAT_LIBRARY))
    p.add_argument("--rounds", type=int, default=3)
    p.add_argument("--layer1-only", action="store_true", help="skip the Layer-2 re-screening pass")
    p.add_argument("--rescreen", metavar="VERDICT.md",
                   help="re-run a past debate, feeding in its own flagged missed considerations + bias")
    p.add_argument("--models", action="store_true", help="list reachable GitHub models and exit")
    args = p.parse_args()

    if args.models:
        list_github_models()
        return

    if args.rescreen:
        otopic, verdict, missed, bias = load_rescreen(args.rescreen)
        first = next((ln.lstrip("# ").strip() for ln in otopic.splitlines() if ln.strip()), "decision")
        display = f"RE-SCREEN — {first[:70]}"
        aug = build_rescreen_topic(otopic, verdict, missed, bias)
        cli_seats = [s.strip().lower() for s in args.seats.split(",")] if args.seats else None
        council = build_council(cli_seats or DEFAULT_SEATS)
        md = run_debate(aug, args.rounds, council, screen2=not args.layer1_only, title=display)
        print(f"\n✓ Re-screen filed: {save(display, md)}")
        return

    topic = args.topic
    if args.topic_file:
        with open(args.topic_file, encoding="utf-8") as f:
            topic = f.read().strip()
    if not topic:
        p.error("provide a topic, --topic-file, or --models")

    cli_seats = [s.strip().lower() for s in args.seats.split(",")] if args.seats else None
    file_seats, topic = parse_seats(topic)
    overrides, topic = parse_models(topic)
    council = build_council(cli_seats or file_seats or DEFAULT_SEATS)
    for seat_id, (provider, model) in overrides.items():
        for seat in council:
            if seat is not None and SEAT_LIBRARY.get(seat_id, {}).get("name") == seat["name"]:
                seat["provider"], seat["model"] = provider, model
                print(f"   · cast {seat['name']} -> {provider}:{model}")

    markdown = run_debate(topic, args.rounds, council, screen2=not args.layer1_only)
    path = save(topic, markdown)
    print(f"\n✓ Verdict filed: {path}")


if __name__ == "__main__":
    main()
