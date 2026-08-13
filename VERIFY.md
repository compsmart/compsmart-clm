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

The current frozen run is a qualified positive result: 103/106 checks passed,
with zero regression across 67 sequential preservation probes. See
[RESULTS.md](RESULTS.md) for the complete interpretation and disclosed refusal.

## Live behavioral verification

When `https://clm.compsmart.cloud` is active:

```powershell
python demo/verify_live.py
python demo/verify_live.py --base-url https://clm.compsmart.cloud
```

The live verifier creates an isolated anonymous session, checks an initially
unknown synthetic fact, teaches randomized facts and text skills, tests exact
and paraphrased recall, checks earlier lessons again, then deletes the session.
Inputs are generated locally and are not included in the published evidence.

Exit code `0` means all required checks passed. Exit code `1` means at least one
behavioral check failed. Exit code `2` means the endpoint could not be tested.

## Manual conversation

```powershell
python demo/chat.py
```

Use `/quit` to exit while retaining the anonymous session for the next launch.
Use `/delete` to delete the current session and its locally saved credential.
The client prints only the public service response; it does not expose internal
state or diagnostics.

## Interpreting results

Exact recall and held-out generalization are reported separately. A passing
exact-recall check does not imply that every possible paraphrase will work.
Likewise, a hosted demonstration cannot by itself make infrastructure claims
mathematically unassailable; the signed isolated-run evidence is the supporting
record for the self-contained-runtime claim.
