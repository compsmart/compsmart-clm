# Compsmart CLM

Compsmart CLM is a confidential, self-contained continual-learning model
preview. It can learn selected facts and small text skills during ordinary
inference, retain them across later interactions, and recall them through new
wording without retraining by the tester.

This repository intentionally contains **verification material only**. It does
not contain model weights, executable model samples, server code, prompts,
architecture, training material, state files, or implementation details. This
boundary protects ongoing confidential research and prevents published samples
from disclosing how the capability is implemented.

## Try the hosted model

The public preview will be available at `https://clm.compsmart.cloud` after the
origin DNS and TLS activation described in the release status is complete.

```powershell
python chat.py
```

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
python verify_live.py
```

Verify the published evidence and its hashes without contacting the service:

```powershell
python verify_evidence.py
```

## What is and is not claimed

The preview demonstrates bounded continual learning for the documented fact
and text-skill tasks, persistence, paraphrase generalization, correction,
isolation, and preservation checks. It does not claim universal continual
learning, arbitrary skill acquisition, truth verification, unlimited memory,
or guaranteed answers to every paraphrase.

See [MODEL_CARD.md](MODEL_CARD.md), [VERIFY.md](VERIFY.md), and
[CHALLENGE_PROTOCOL.md](CHALLENGE_PROTOCOL.md) for the precise public contract.

The code in this repository is licensed under Apache-2.0. That license does not
grant access to, or rights in, the confidential hosted model or runtime.

