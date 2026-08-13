# Run the demonstrations

These standard-library Python programs interact only with the documented
black-box HTTPS API. They contain no model weights, server code, prompts,
training code, state format, architecture, or learning implementation.

From the repository root:

```powershell
python demo/chat.py
python demo/verify_live.py
python demo/verify_evidence.py
```

- `chat.py` starts an anonymous conversation in which you can teach and recall
  a personal fact.
- `verify_live.py` generates a fresh random fact, teaches it, tests exact and
  paraphrased recall, teaches a text transformation, checks that the earlier
  fact was preserved, checks session isolation, and deletes the session.
  It takes about 90 seconds because it respects the public preview rate limit.
- `verify_evidence.py` verifies the hashes and internal consistency of the
  published black-box evidence without contacting the hosted model.
- `clm_client.py` is the small reusable HTTPS client used by the other demos.

Anonymous preview sessions expire within 24 hours. Do not submit credentials,
regulated data, or information about another person.
