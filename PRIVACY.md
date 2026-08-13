# Preview privacy notice

The public preview uses separate anonymous conversation and learner tokens.
Each conversation is retained for no longer than 24 hours. Accepted learner
state and learner-visible history are available across fresh conversations.
Learner state expires after 24 hours without use; every individual history
event is pruned no later than 24 hours after it was recorded. The history stores
user prompts, assistant replies, and learning/reload telemetry as plaintext on
the instance so users can inspect what happened. System prompts are not
included.

`/delete` deletes the current conversation credential but deliberately keeps
the learner, learned state, and learner history for fresh-conversation
persistence. `/forget` deletes that learner, all of its conversations, its raw
prompt history, and its learned state.

Do not submit passwords, API keys, financial or medical information, regulated
data, confidential business information, or personal information about anyone
else. Synthetic facts are strongly preferred for public testing.

Backend operational logs store route/status metadata, not request bodies or IP
addresses. Aggregate status, latency, rate-limit, and availability counters may
be retained. Network and TLS providers may process connection metadata as part
of delivering the service.

This is a research preview, not a production personal-data store.
