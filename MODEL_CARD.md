# Compsmart CLM preview model card

## Model summary

Compsmart CLM is a confidential language model service designed to demonstrate
bounded learning during inference. An anonymous learner may teach synthetic or
personal facts and small text transformations, ask for exact recall, and test
new wording or new inputs. Accepted learning is available in fresh conversation
sessions associated with that learner for the documented retention period.

The public service is a black-box research preview. Its weights, architecture,
prompts, runtime, training data, and internal state format are not disclosed.

## Supported preview behavior

- Learn an explicitly stated fact in conversation.
- Recall a taught fact exactly and through reasonable paraphrases.
- Learn a small deterministic text skill from an instruction and examples.
- Apply a learned skill to an unseen input.
- Correct a previously taught fact without changing unrelated learned facts.
- Preserve earlier tested behavior as additional lessons are introduced.
- Carry accepted learning into fresh sessions for the same anonymous learner.
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

The first published frozen run is qualified rather than perfect: all accepted
lessons were preserved, but one of three requested text skills was refused.
See [RESULTS.md](RESULTS.md) for counts and the complete disclosed failures.
