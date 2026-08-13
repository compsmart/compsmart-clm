# Public evidence results

## Outcome

The frozen black-box run is a **qualified positive result**, not a perfect
protocol pass. It demonstrates that the preview acquired unrelated facts and
text skills during use, applied accepted lessons to new wording or inputs, and
preserved every accepted lesson as more lessons arrived and after a fresh
process loaded the saved session.

The evidence contains only requests, expected observable behavior, returned
answers, pass/fail decisions, aggregate metrics, and environment claims. It
does not contain weights, model samples, server code, prompts, architecture,
state, training data, or a description of the learning implementation.

## Measured results

| Capability | Result |
|---|---:|
| All black-box checks | 103/106 (97.17%) |
| Fact lessons accepted | 8/8 |
| Text-skill lessons accepted | 2/3 |
| Sequential preservation probes | 67/67 |
| Observed regressions on earlier commitments | 0 |
| Held-out probes for accepted lessons | 10/10 |
| Held-out probes across all requested lessons | 10/11 (90.91%) |
| Accepted lessons after fresh-process reload | 10/10 |
| Correction, non-mutation, isolation, deletion | all passed |

The 67 preservation probes repeatedly retested earlier facts after later fact
and skill lessons. There were zero observed regressions. The fresh-process
phase then recalled all eight accepted facts and applied both accepted skills
again, giving 10/10 retention across accepted lessons.

## Disclosed failures

The model refused the third requested text skill. Because that skill was never
accepted, its unseen-input probe and reload probe also returned no committed
knowledge. These are the run's three failures. They are retained verbatim in
the transcript and are not counted as forgetting: no previously accepted
behavior regressed.

This refusal means the run does not establish that every supported-looking
lesson will be acquired. It does establish the narrower observed capability:
multiple facts and skills can be acquired sequentially, generalized, corrected,
and retained without regression within the tested bounded setting.

## Reproduce and inspect

Verify the immutable evidence bundle offline:

```powershell
python demo/verify_evidence.py
```

Run a fresh randomized challenge against the hosted preview:

```powershell
python demo/verify_live.py
```

The complete machine-readable observations are in
[`evidence/transcript.json`](evidence/transcript.json). Aggregates are in
[`evidence/metrics.json`](evidence/metrics.json), runtime claims are in
[`evidence/environment.json`](evidence/environment.json), and SHA-256 bindings
are in [`evidence/manifest.json`](evidence/manifest.json).

## Claim boundary

This is evidence for bounded continual learning under the published challenge,
not proof of universal continual learning. It does not establish arbitrary task
learning, unlimited capacity, guaranteed generalization, or a particular
internal methodology.
