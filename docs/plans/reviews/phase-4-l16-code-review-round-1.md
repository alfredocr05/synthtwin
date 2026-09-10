# Landing L16 — review round 1, the item list

Reviewer: codex `gpt-6-astra`, high reasoning effort, read-only.
Verdict: **RATIFY-WITH-CONDITIONS.** One round, per amendment A-P4-59.
This is also round 9 of landing L14: the round-8 item that blocked that
landing is the subject of this one.

## Items 1 to 4 — repaired before the commit

| # | severity | what it was | what closed it |
|---|---|---|---|
| 1 | high | **The letter filter REMOVED a warning the tree already gave.** `_wears_a_word` tested ASCII letters, so 280 readings beside twenty `10.50 α` carried NF54 at HEAD and carried nothing after the landing: twenty marked readings left the distribution in silence. | The test is a closed set of SYMBOLS (`_SYMBOL_MARKS`) rather than of letters, so a mark nobody listed is read as a word and asks. Chosen over `str.isalpha` because five supported Pythons carry five Unicode databases and which sentences a profile carries is a published fact (plan D12). Pinned by `test_a_marker_written_in_another_alphabet_still_asks`. |
| 2 | high | **The screen claimed retention where nothing is retained.** The landing's own new joined block said values "are kept as they are written"; three hundred different pairs reach free text, which publishes none of them. | `asking.publishes_its_values` reads `taxonomy.ROLES_PUBLISHING_NOTHING`, and the notice states per column what that column publishes. Pinned by `test_the_screen_says_what_each_joined_column_publishes`. |
| 3 | medium | **The count measured wrappers, not numbers wearing a word.** Ten `10.50 H` beside ten `<0.50` said twenty (`<` is no word); seventeen `10.50 H` beside three `many H` said twenty (`many` is no number). | `_wearing_a_word` counts a cell only where its wrapper carries a word AND its core reads as a number. Pinned by `test_the_question_counts_only_numbers_wearing_a_word`. |
| 4 | medium | **The advice promised coverage the floor prevents.** NF54 and NF55 both said `--code` keeps every value exactly as written; at a raised smallest-group size a register of 280 codes publishes what clears the floor and pools 283 rows away. | Both sentences, and NF43, are qualified by the smallest-group size in force. Pinned by `test_neither_question_promises_what_the_floor_can_take_away`, and `test_the_contract_quotes_the_sentence_the_producer_writes` holds the contract's quotes to the shipped words. |

**Found by the suite rather than the reviewer, and repaired with them:**
NF43's padded-number remark named `--identifier` — the declaration that
WITHHOLDS a column — where the screen notice raised by the same signal
said `--code`. It names `--code` first now. `test_p4d16_padded_numbers`
moved with it and says why.

## Items 5 and 6 — carried by name (A-P4-59)

| # | severity | carried as |
|---|---|---|
| 5 | low | **R-P4-158**, opened. A column reaching a label role before rule 9 never carries NF55 and does not answer to `--measurement`: measured, a hundred each of `7.1`, `7.2H`, `7.3L` takes `categorical` at rule 7 and stays there declared. Repairing it means raising the sentence above the label roles or making `--measurement` reach rule 7, both design decisions rather than adjustments. |
| 6 | low | **R-P4-72**, extended rather than opened as new. The 14.8 appendix sums to 96 argument positions while `sum(taxonomy.NOTE_ARITY.values())` is 94, and the two positions are exactly NG32 and NG34 — the two rows that residual already holds open as a scope decision. Verified on the tree: 55 forms, 55 appendix rows, those two the only disagreement. |

**Also named and deliberately not repaired here:** NF35, the affixed
role's standing remark, carries the same `--identifier` flaw NF43 shed.
It is quoted inside a frozen reference vector, so moving it moves
committed bytes and the independent oracle in the same commit — the
code-wording landing's work under the one-week close. Recorded on
R-P4-72.

## What the reviewer confirmed

The requested 280/15/5 repair works, including the mean of 54,239.18
and all three declarations. Across 24 before-and-after comparisons no
role and no detail block moved. Source tracing confirmed the
`--measurement` condition is equivalent to the one before the landing
and that NF50 excludes NF55; probes confirmed NF55 on free text and on
long-tail labels and its absence under either declaration.
