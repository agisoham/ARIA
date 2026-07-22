# Safe agentic development for trading systems

Using an AI coding agent (Claude Code, Cursor, etc.) to build a trading system is a force
multiplier — and a liability, because the same agent that writes your backtester can also run
code that touches a live broker. This is the guardrail pattern ARIA uses so an agent can move fast
without ever being able to lose real money. It's reusable for any money-touching codebase.

> **The one rule:** the agent must never be *able* to place a live order or move money — enforced
> by tooling, not by remembering. Everything is paper/simulated until a human explicitly flips a
> switch that the agent cannot reach.

## 1. An agent "constitution" (`CLAUDE.md` / rules file)
Keep a short, always-true rules file the agent reads every session. The load-bearing lines:

```markdown
## Absolute guardrails (never violate)
- NEVER place live orders, move money, or call a live broker trading endpoint.
- All trading is simulated/paper. Live-execution code lives behind a disabled flag that
  requires an explicit, manual human step the agent cannot perform.
- Never hardcode API keys. Read them from the environment / a gitignored .env.
- No look-ahead bias: a backtest must never use data from the future of the bar being decided.
```

Short beats long — a bloated rules file dilutes attention.

## 2. Plan → Build → Verify
The habit that ships correct code and suppresses hallucinations:
1. **Plan first.** Have the agent *propose* an approach without editing. Read it. Bad designs are
   cheapest to kill before any code exists.
2. **Build one slice**, then stop.
3. **Verify every time.** Require green tests and real output — never accept "should work." For a
   trading system, "verify" also means: does the backtest still match the reference, and did this
   change introduce look-ahead bias?

Keep each session to one task; clear context between unrelated tasks.

## 3. Hooks — mechanical guardrails (the actual seatbelt)
Lifecycle hooks (`PreToolUse`, `PostToolUse`, `SessionStart`) can run a command or **block an
action**. This is where survivability is enforced in code rather than in discipline:
- **PreToolUse (on shell/exec):** block any command that looks like live execution — anything
  containing a live-order endpoint, a `--live` flag, or real-money markers. This is the seatbelt
  for "never lose money": even if the agent (or a bug, or a bad prompt) tries, it can't.
- **PostToolUse (on file write):** auto-format and run a fast test pass — catch breakage instantly.
- **SessionStart:** print the current guardrails so every session starts grounded.

Principle: *if something must happen, make it a hook* — never rely on remembering.

## 4. Testing discipline — the part that separates real from naive
The biggest risk in quant code isn't bugs, it's fooling yourself:
- **Test-driven:** write the expected behaviour first; have the agent make it pass.
- **Walk-forward by default:** no strategy is "validated" on a single in-sample backtest. Bake this
  into any scaffolding so it's unavoidable.
- **Model costs:** a backtest that ignores slippage, spread, and market impact is a red flag. Model
  them before trusting any result.
- **Anti-overfit rigor:** purged/embargoed cross-validation and a deflated Sharpe ratio (which
  penalises for how many strategies you tried) directly answer "how do you know this isn't overfit."
- Have the agent *argue against its own result* — "what would make this an overfit?" — as a cheap
  second opinion.

## 5. Secrets & isolation
- `.env` gitignored; no key ever committed (rotate immediately if one slips).
- Live-execution code disabled by default, behind a flag requiring a manual human step.
- A pre-publish secret scan gate before anything reaches a public repo.

## Checklist
- [ ] Rules file with hard guardrails, read every session.
- [ ] PreToolUse hook blocks live-order / money-moving commands.
- [ ] PostToolUse hook formats + tests on every write.
- [ ] Every strategy ships a unit test + a walk-forward test before "done".
- [ ] `.env` gitignored; secret scan before publish.
- [ ] Live execution disabled by default, behind a human-only switch.

*The through-line: let the agent be fast where mistakes are cheap (research, scaffolding, tests),
and make it structurally incapable of the one mistake that isn't (touching real money).*
