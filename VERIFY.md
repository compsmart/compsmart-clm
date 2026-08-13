# Verification guide

## Offline evidence verification

Requires Python 3.11 or newer and no third-party packages:

```powershell
python demo/verify_evidence.py
python -m unittest discover -s tests -v
```

The verifier checks every published evidence file against
`evidence/manifest.json`, validates the transcript schema, recomputes aggregate
results, and confirms that the challenge seed was derived from the frozen
protocol commit recorded in the manifest.

The deployed capsule runtime's frozen run is a qualified positive result:
103/106 checks passed, with zero regression across 67 sequential preservation
probes. The separate LoRA v2 protected run is a null result (39/59) and is
verified from `evidence/v2/manifest.json`. See [RESULTS.md](RESULTS.md) and
[ADAPTER_RESULTS_V2.md](ADAPTER_RESULTS_V2.md).

## Live behavioral verification

When `https://clm.compsmart.cloud` is active:

```powershell
python demo/verify_live.py
python demo/verify_live.py --base-url https://clm.compsmart.cloud
```

The live verifier creates an isolated anonymous session, checks an initially
unknown synthetic fact, teaches randomized facts and text skills, tests exact
and paraphrased recall, checks earlier lessons again, recalls the fact from a
fresh session, unloads and reloads learned state from disk, replays
commitments, inspects learner-visible history, verifies isolation, then deletes
the learner. Inputs are generated locally and are not published.

The captured live run in `evidence/observable-v2/verification.json` passed all
18 deployment checks. Its manifest covers both that result and the public
model/runtime disclosure captured from the live endpoint.

Exit code `0` means all required checks passed. Exit code `1` means at least one
behavioral check failed. Exit code `2` means the endpoint could not be tested.

## Manual conversation

```powershell
python demo/chat.py
```

Every launch creates a new conversation session associated with the locally
saved anonymous learner identity. Type `/help`; useful commands include
`/model`, `/status`, `/history`, `/verify`, `/reload`, and `/new`. Use `/delete`
to delete only the current conversation or `/forget` to delete the learner,
history, and learned state.

## Interpreting results

Exact recall and held-out generalization are reported separately. A passing
exact-recall check does not imply that every possible paraphrase will work.
Likewise, a hosted demonstration cannot by itself make infrastructure claims
mathematically unassailable; the signed isolated-run evidence is the supporting
record for the self-contained-runtime claim.
