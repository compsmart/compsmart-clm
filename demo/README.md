# Run the demonstrations

These standard-library Python programs interact only with the documented HTTPS
API. They contain no model weights, server code, system prompts, training data,
or private state.

From the repository root:

```powershell
python demo/chat.py
python demo/verify_live.py
python demo/verify_evidence.py
```

- `chat.py` starts an anonymous conversation in which you can teach and recall
  a personal fact. Every launch creates a new conversation session while a
  locally saved anonymous learner credential carries accepted learning across
  those sessions. Use `/delete` to delete only the current conversation or
  `/forget` to delete the learner, its raw prompt history, and its learned
  state. `/help` lists model, status, history, verification, reload, and new
  conversation commands.
- `verify_live.py` generates a fresh random fact, teaches it, tests exact and
  paraphrased recall, teaches a text transformation, checks that the earlier
  fact was preserved, recalls it in a fresh session, checks learner isolation,
  and deletes the learner. It takes about 50 seconds because it respects the
  public preview rate limit.
- `verify_evidence.py` verifies the hashes and internal consistency of the
  published black-box evidence without contacting the hosted model.
- `clm_client.py` is the reusable HTTPS client. In addition to chat it exposes
  `model`, `model_history`, `service_status`, `session_status`, `history`,
  `verify`, `reload`, asynchronous teaching, and privacy deletion methods.

Anonymous preview sessions expire within 24 hours. Learner state expires after
24 hours without use. Do not submit credentials, regulated data, or information
about another person.
