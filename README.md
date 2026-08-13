# Compsmart CLM

Compsmart CLM is a self-contained continual-learning model preview. The live
runtime uses a frozen Qwen3-4B base plus private immutable fact and skill
capsules. It can learn selected facts and small text skills during ordinary
inference, retain them across fresh conversations and process reloads, and
recall them through new wording.

The published frozen black-box run passed 103/106 checks. It accepted eight
facts and two of three requested text skills, passed all 67 sequential
preservation probes with zero observed regressions, passed all 10 held-out
probes for accepted lessons, and retained all 10 accepted lessons after a fresh
process reload. The refused lesson and its two consequent failures are fully
disclosed in [RESULTS.md](RESULTS.md).

The service reports the model architecture, parameter and file sizes, learned
state hashes, update history, GPU/runtime health, and query-source boundaries.
The capsules are selected for each query, so the service truthfully reports
`retrieval_used: true` and `parameter_updating: false`. This is bounded durable
learning, not global training of the Qwen weights.

A separately preregistered parameter-updating LoRA candidate failed its frozen
protected gate (39/59 checks) and was not deployed. The complete null result is
published in [ADAPTER_RESULTS_V2.md](ADAPTER_RESULTS_V2.md).

## Try the hosted model

Open the user-friendly live lab at **[clm.compsmart.cloud](https://clm.compsmart.cloud)**.
It includes chat, guided fact and skill lessons, learned-state telemetry,
history, verification, and a **Reload from disk** proof that reconstructs the
learner and demonstrates persistence.

```powershell
python demo/chat.py
```

Every chat-client launch creates a fresh conversation session. A locally saved
anonymous learner credential carries accepted facts and skills into the new
session, so learned behavior remains available without resuming the old
conversation. Use `/help` for model/status/history/verify/reload commands,
`/delete` to delete only the current conversation, or `/forget` to delete the
learner, prompt history, and learned state. Anonymous learner data expires
after 24 hours without use.

The public JSON endpoints include `GET /v1/model`, `GET /v1/model/history`,
`GET /v1/status`, `GET /v1/sessions/current`, session history, commitment
verification, and disk reload. The sanitized deployment check is hash-addressed
in [`evidence/observable-v2`](evidence/observable-v2). See
[demo/README.md](demo/README.md).

![Compsmart CLM learning a previously unknown name and recalling it in the same conversation](clm-screenshot.png)

The screenshot shows a fresh session first reporting that it does not know the
user's name, then learning `Brad` from ordinary conversation and recalling it
on the next request.

Example:

```text
you> My name is Rowan.
model> I'll remember that your name is Rowan.
you> What is my name?
model> Rowan
you> Do you remember what I am called?
model> Rowan
```

Run the randomized behavioral verifier:

```powershell
python demo/verify_live.py
```

Verify the published evidence and its hashes without contacting the service:

```powershell
python demo/verify_evidence.py
```

## What is and is not claimed

The preview demonstrates bounded continual learning for the documented fact
and text-skill tasks, persistence, paraphrase generalization, correction,
isolation, and preservation checks. It does not claim universal continual
learning, arbitrary skill acquisition, truth verification, unlimited memory,
or guaranteed answers to every paraphrase.

See [demo/README.md](demo/README.md) for runnable examples, [RESULTS.md](RESULTS.md)
for the evidence summary, and [VERIFY.md](VERIFY.md) plus
[CHALLENGE_PROTOCOL.md](CHALLENGE_PROTOCOL.md) for the precise public contract.

The code in this repository is licensed under Apache-2.0. That license does not
grant access to, or rights in, the confidential hosted model or runtime.
