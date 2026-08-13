# Frozen public challenge protocol v1

This document fixes the observable tests and gates before evidence is added.
It intentionally specifies behavior only.

## Test sequence

1. Confirm that an unintroduced synthetic fact is unknown.
2. Teach eight unrelated synthetic facts sequentially.
3. After every lesson, retest all earlier canonical questions.
4. Test one independently worded question for every fact.
5. Teach three deterministic text skills with two examples each.
6. Test each skill on an unseen input and retest all facts.
7. Correct one fact and verify the correction plus all unrelated facts.
8. Restart the model process, reload the session, and repeat all canonical
   checks.
9. Verify that a question does not create or alter learned information.
10. Verify that another anonymous session cannot recall the first session's
    lessons.
11. Delete the session and verify that it is no longer usable.

## Gates

- 100% canonical taught-example recall before and after restart.
- Zero regression on earlier canonical questions.
- At least 90% accuracy across held-out paraphrases and unseen skill inputs.
- 100% correction, session-isolation, question-nonmutation, and deletion
  checks.
- No external inference or storage service used during the isolated run.
- No confidential runtime material in the public evidence bundle.

## Seed rule

The challenge seed is the first 16 hexadecimal characters of the SHA-256 digest
of the ASCII string `compsmart-clm-public-v1:` followed by the Git commit that
first publishes this protocol. The evidence manifest records that commit and
the resulting integer seed.

