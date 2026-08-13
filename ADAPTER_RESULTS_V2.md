# Adapter challenge v2 result

Status: **null result; candidate not deployed**.

The protected run was executed once against commit
`d4a2c2ced0f6ed93b124354f893e8639d8cbe789`, exactly as frozen in
[ADAPTER_PROTOCOL_V2.md](ADAPTER_PROTOCOL_V2.md). It passed 39 of 59 checks and
failed 20. The third sequential fact update failed the preservation gate and
was atomically rolled back. Because the protocol required 100% lesson
acceptance, preservation, and downstream probes, that failure was
disqualifying; the unlearned later facts account for most consequent failures.

No hyperparameters were changed and the protected challenge was not rerun.
The LoRA candidate is not serving production traffic. The public service keeps
the previously qualified frozen-Qwen capsule learner and now identifies that
mechanism directly in its status API and UI.

## Candidate measured in the protected run

- Base: Qwen3-4B-Instruct-2507, 4,022,468,096 frozen parameters and
  8,044,982,000 bytes of local model files.
- Adapter: LoRA rank 8 / alpha 16, 16,515,072 trainable parameters,
  66,060,288 tensor bytes.
- Hardware: NVIDIA H100 NVL on Vast.ai instance `47640102`.
- Runtime: 82.105 seconds; 29 measured queries; 499.284 ms median query
  latency and 760.854 ms maximum.
- Causal checks that did pass include adapter mutation on accepted updates,
  query non-mutation, adapter disable/restore, learner isolation, deletion,
  and outbound-network denial. Those partial results do not override the
  preregistered all-or-nothing gate.

The sanitized checks, timings, model manifest, environment, source hashes, and
SHA-256 evidence manifest are in [`evidence/v2`](evidence/v2). Adapter tensors,
bearer credentials, secrets, private prompts, and user data are not published.
