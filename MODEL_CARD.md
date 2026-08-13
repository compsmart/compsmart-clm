# Compsmart CLM preview model card

## Model summary

Compsmart CLM is a language model service designed to demonstrate bounded,
durable learning during inference. The deployed build uses a frozen
Qwen3-4B-Instruct-2507 base (4,022,468,096 parameters; about 8.04 GB of model
files) plus private immutable fact and skill capsules. Selected capsules are
provided to the model at query time; this is retrieval-backed learned state,
not parameter updating.

`GET /v1/model` publishes the architecture, base manifest, dimensions, learned
state type and size, query inputs, and excluded inputs. `GET /v1/status`
publishes runtime, GPU, disk, latency, and update telemetry. Model weights,
system prompts, and the internal capsule format remain unpublished.

## Supported preview behavior

- Learn an explicitly stated fact in conversation.
- Recall a taught fact exactly and through reasonable paraphrases.
- Learn a small deterministic text skill from an instruction and examples.
- Apply a learned skill to an unseen input.
- Correct a previously taught fact without changing unrelated learned facts.
- Preserve earlier tested behavior as additional lessons are introduced.
- Carry accepted learning into fresh sessions for the same anonymous learner.
- Unload learned state and reconstruct it from disk with an integrity and
  replay trace.
- Keep anonymous learners isolated from one another.
- Abstain when the session does not supply enough information.

## Limits

- The service trusts user-provided facts; it does not establish their truth.
- Novel phrasing and unseen-input performance are measured, not guaranteed.
- The preview is bounded by request, session, rate, retention, and capacity
  limits.
- Unsupported tasks may be refused or answered with an explicit lack of
  knowledge.
- Availability is best-effort during the research preview.

## Privacy and retention

Anonymous conversation sessions expire no later than 24 hours after creation.
Anonymous learner state expires after 24 hours without use. Both may be deleted
earlier through the API. Do not submit secrets, regulated data, credentials, or
information about another person. See [PRIVACY.md](PRIVACY.md).

## Claim boundary

Passing the public protocol is evidence for the behaviors it measures. It is
not proof of universal continual learning and does not disclose or validate a
particular implementation methodology.

The parameter-updating LoRA v2 candidate is a disclosed null result: it passed
39/59 protected checks but failed its third sequential update and was not
deployed. See [ADAPTER_RESULTS_V2.md](ADAPTER_RESULTS_V2.md).

The first published frozen run is qualified rather than perfect: all accepted
lessons were preserved, but one of three requested text skills was refused.
See [RESULTS.md](RESULTS.md) for counts and the complete disclosed failures.
