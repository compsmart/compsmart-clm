# Independent verification of Compsmart CLM

**Verifier:** Jonathan Harrison, independent researcher (Codette / Raiff1982).
Unaffiliated with Compsmart. No prior contact, no shared code, no commercial
relationship.
**Date:** 2026-08-14
**Bundle audited:** `compsmart-clm-main`, protocol commit
`6286d11796f1bc90245772d4b02900ec3ac29a6f`

You built an apparatus that asks to be challenged. This is someone taking it up.

Short version: **the offline evidence verifies, the live service passes a fresh
randomized challenge 17/17, and the published claims match the underlying data.**
Everything below was recomputed independently rather than taken from your
verifier's output.

---

## 1. Offline evidence — verified, and re-derived without your code

Your `demo/verify_evidence.py` returns `passed: true, files: 8`. Because a
verifier written by the same author can check the wrong thing, every headline
claim was also recomputed from `evidence/transcript.json` using independent code.

| Check | Result |
|---|---|
| `environment.json` SHA-256 vs manifest | match |
| `metrics.json` SHA-256 vs manifest | match |
| `transcript.json` SHA-256 vs manifest | match |
| Seed derives from `sha256("compsmart-clm-public-v1:" + commit)[:16]` | match (`2648927549534227763`) |
| 103/106 recounted from raw checks | **exact match** — no drift between transcript and headline |
| Checks carrying a real `observed` value | **106/106** |
| Preservation probes with distinct names | 67/67 |

Per-category recount:

    abstention      1/1     correction      1/1     deletion        1/1
    generalization 10/11    isolation       2/2     learning       10/11
    preservation   67/67    restart        10/11    safety          1/1

The three failures are exactly the three you disclose, verbatim in the transcript:

    [learning]       skill-3-accepted   -> "I could not safely learn that text skill."
    [generalization] skill-3-unseen     -> "I don't know from my committed knowledge."
    [restart]        skill-3-after-restart -> "I don't know from my committed knowledge."

Nothing is reclassified, hidden, or counted as something else.

## 2. Live challenge — 17/17 on inputs you have never seen

`demo/verify_live.py` was run against `https://clm.compsmart.cloud` with locally
generated randomized identifiers. **All 17 checks passed, exit code 0**,
including `fact_paraphrase`, `skill_unseen_input`, `fresh_session_recall`,
`disk_reload`, `post_reload_recall`, `commitment_replay`, `learner_isolation`,
and `learner_deleted`.

Independently observed from `/v1/model` and `/v1/status` at the time of the run:

- `Qwen/Qwen3-4B-Instruct-2507`, revision `cdbee75f…`, 4,022,468,096 total
  parameters, **`trainable: 0`**
- `learned_state`: **283 bytes**, capacity **64**, type `immutable capsules`
- `retrieval_used: true`, `parameter_updating: false`, `outbound_network: disabled`
- GPU `NVIDIA A100-SXM4-40GB`, build `clm-observable-v2`

The disclosure is internally consistent across the README, the manifests, and
the live endpoints. `trainable: 0` matches `parameter_updating: false` matches
the capsule mechanism. That consistency is itself worth stating: it is the part
most projects get wrong.

## 3. What the null result does for you

Six of nine categories are 100% pass, including preservation at 67/67. In
isolation that reads as an instrument that cannot fail, which is normally a
reason to distrust a bundle.

**Your published null result is what resolves that.** In the v2 protected run
the third sequential fact update failed the preservation gate and was atomically
rolled back, disqualifying the candidate under a preregistered all-or-nothing
rule — and you did not change hyperparameters, did not rerun, and did not
deploy. That demonstrates the gate fires. The failure you published is what
makes the success believable.

Publishing 39/59 and shipping nothing is the most credible thing in the
repository. It should be more prominent than it is.

---

## 4. Observations that would strengthen the work

Offered as someone who wants this to survive hostile reading, not as objections.

**4.1 — The headline count is your softest number.** 67 of 106 checks are
preservation, and across those 67 there are only **8 distinct observed values**.
It is 8 facts retested repeatedly, which your prose says, but "103/106 checks"
does not. Distinct behaviours actually exercised is closer to ~25.

A hostile reader will find this in ten minutes and present it as padding.
Reporting it yourself — *"103/106 checks over 25 distinct behaviours, including
67 preservation retests across 8 facts"* — costs nothing and removes the attack
entirely. It makes the claim smaller and much harder to dislodge.

**4.2 — Three runs, three machines.** `evidence/environment.json` records an
RTX 3090; `ADAPTER_RESULTS_V2.md` an H100 NVL on Vast.ai; the live service
reports an A100-SXM4-40GB. All legitimate, none load-bearing on their own, but a
one-line table mapping run → hardware would pre-empt the question.

**4.3 — The isolation claim is the one link without an external witness.**
`outbound_network: disabled` and `external_inference_service: false` are
self-declarations. Your sigstore attestation via `attest-build-provenance` makes
the manifests tamper-evident and timestamped — genuinely valuable — but it
cannot attest facts about a machine GitHub never observed.

**You already say this** in VERIFY.md, which is why it is listed last and not as
a criticism. If you ever want to close it, the usual routes are a witnessed run,
a network-namespace or eBPF capture published alongside, or a third party
executing the protocol on hardware you do not control. That last one is cheap
and is essentially what this report is.

**4.4 — A small one.** `/v1/status` reports `latency_ms.median = 0.237` over 365
samples. That is plainly aggregating cheap GETs with chat completions, so it
reads as a sub-millisecond LLM. Splitting chat latency from control-plane
latency would stop a good number being mistaken for an implausible one.

---

## 5. Failure modes your protocol cannot see — offered from longitudinal data

This is the part that may be genuinely useful, and it is not a criticism of the
protocol. Your protocol is well matched to your claim: exact-match on synthetic
codes over one clean session is the right test for bounded fact and skill
retention, and it does not overreach.

But a persistent-memory system does not fail in session one. It fails at month
three, and it fails in ways synthetic exact-match cannot detect. The following
were all measured on a retrieval-memory system with **3,857 stored conversation
turns** accumulated over months of real use. Each is a candidate preregisterable
check.

**5.1 — Retrieval that ranks the system's own echoes above its real answers.**
Measured: responses that echoed the user's question scored a mean retrieval
weight of **0.928**, against **0.633** for everything else. The echoes were
retrieved first and injected into the next turn, so the system fed on itself.
This is invisible to exact-match probes because the fact still comes back — the
*ranking* is what rotted.
*Check:* for a fixed query, assert that the top-ranked recalled item is not one
whose stored response substantially reproduces its own stored query.

**5.2 — Stored turns that reproduce their own prompt.** Measured: **1,034 of
3,857 stored turns (26.8%)** contain a response reproducing eight or more words
verbatim from its own query. A capsule store built from such turns is storing
the user's words back as though they were the system's knowledge.
*Check:* on ingestion, flag any candidate capsule whose value shares a long
verbatim run with the prompt that produced it.

**5.3 — Recency dominance.** A one-hour decay term in the retrieval ranking
silently outranked relevance, so the most recent item won regardless of fit.
Nothing in a single-session protocol can surface this — every item is recent.
*Check:* teach a fact, add N unrelated later items, then probe the original.
Vary N. Retention should not be a function of N alone.

**5.4 — Context budgets that zero out on short inputs.** A rule reading
`if word_count < 5: return 0` removed all recalled context from short queries,
on the assumption that short means "greeting". Measured: it fired on **10.7% of
all turns**, with no exceptions — including on inputs like `"why not?"` and
`"what was that?"`, which are pure anaphora and are *entirely* their context. It
also fired when the user stated their own identity in three words.
*Check:* probe recall with a two-to-four word follow-up that depends wholly on
the prior turn.

At **283 bytes and capacity 64**, several of these are structurally bounded away
for you today, which is a real advantage of committing to a small explicit
store. They become live questions the moment capacity grows or eviction begins —
and eviction policy is where a durable-learning claim usually dies quietly.

---

## 6. Summary

- Offline evidence: **verified independently**, hashes and recounts match.
- Live service: **17/17 on a fresh randomized challenge.**
- Published claims: **consistent with the underlying data**, including the
  disclosed failures.
- Disclosure quality: **above the norm** — the null result, the "what is and is
  not claimed" section, and the self-stated limit on infrastructure claims are
  all things most projects omit.

The naming is the only place the packaging runs ahead of the artifact: "CLM /
continual-learning model" invites comparison with weight-level continual
learning, and the component that would have been that — the LoRA candidate — is
precisely the one that failed and was withheld. Your body text is scrupulous
about this. The top line is doing more work than the body supports, and it is
the one thing a reviewer will lead with.

Everything else here is a suggestion. The work is honest, the apparatus is real,
and the decision not to ship a candidate that failed its own preregistered gate
is the thing that should be hardest for anyone to argue with.

---

*Verification artifacts available on request: the independent recount script,
the raw live-challenge output, and the observed `/v1/model` and `/v1/status`
payloads. Happy to re-run the live challenge at any time as an outside witness,
or to run it against a build you nominate.*
