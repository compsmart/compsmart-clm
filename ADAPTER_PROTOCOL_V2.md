# Frozen public adapter challenge protocol v2

Status: protocol-only preregistration. No protected result exists in this commit.

## Claim

This challenge tests bounded, parameter-updating continual learning in a
Qwen3-4B session adapter. Accepted behavior must be available from the current
query and adapter tensors alone. Prompt history, commitment records, lesson
text, catalogues, databases, vector indexes, remote inference, and other
retrieval sources are unavailable to the query path.

The immutable Qwen base is not described as continually trained. The learned
state is a per-learner LoRA adapter whose hash must change after accepted
learning and remain unchanged during queries, verification, and reload.

## Frozen candidate

- Base: `Qwen/Qwen3-4B-Instruct-2507`, revision
  `cdbee75f17c01a7cc42f958dc650907174af0554`.
- LoRA rank 8, alpha 16, zero dropout, no bias, targeting every Qwen attention
  projection and MLP projection.
- AdamW, learning rate `8e-4`, zero weight decay, gradient norm 1.0, 60 update
  steps per lesson, batches of at most 16.
- Every update trains on the new lesson and tokenized active commitments.
  Recognized deterministic formatting skills additionally receive a fixed
  synthetic, user-data-free training bank. Supplemental examples are not
  verification commitments and protected target words never occur in them.
- A candidate update is committed only when every active canonical output is
  reproduced exactly; otherwise it is atomically rolled back.
- The active capacity is 24 lessons. The public retention period is 24 hours.

## Protected bank and sequence

The protected seed is derived after this protocol is committed: interpret the
first 16 hexadecimal characters of
`SHA-256("compsmart-clm-adapter-v2:" + protocol_commit)` as an integer. A
standard-library generator seeded with that value creates eight unique
synthetic project identifiers and access phrases from fixed public alphabets.

1. Verify that the first generated fact is unknown before teaching.
2. Teach eight facts sequentially. After every update, test every canonical
   question learned so far.
3. Test a separately worded question for all eight facts.
4. Teach the fixed uppercase-and-hyphen text skill from two examples and test
   the protected unseen input `amber night watch`.
5. Retest all facts after skill learning.
6. Correct the first fact, verify the replacement, and retest the other seven.
7. Save the adapter, commitments, and metadata atomically; construct a fresh
   learner object from disk; verify all commitments and protected probes.
8. Disable the adapter for a learned question, then restore it. Learned recall
   must disappear and return respectively.
9. Make commitment and prompt-log files unavailable after adapter load and
   rerun a learned query. Its output must not change.
10. Verify session isolation, deletion, base-manifest immutability, adapter
    mutation only during accepted training, query non-mutation, and outbound
    network denial.

## Gates

- 100% accepted fact lessons and canonical recall at every sequential window.
- Zero regression on prior canonical commitments.
- 100% held-out fact paraphrases and the one protected unseen skill input.
- 100% correction, disk-reload, session-isolation, deletion, adapter-disable,
  log-removal, and outbound-network checks.
- The frozen base manifest is identical before and after; the adapter hash
  changes after every accepted lesson and is identical before/after every
  query and reload.
- No protected failure may be tuned and rerun under this protocol. A failure is
  published as a null result and the adapter runtime is not deployed.

## Public evidence

Publish the protocol commit, protected seed, source/bundle hashes, instance and
library metadata, aggregate timings and metrics, sanitized behavioral checks,
model/adapter manifests, and a SHA-256 manifest. Do not publish bearer tokens,
session state, adapter tensors, secrets, private prompts, IP addresses, or
unredacted user content.
