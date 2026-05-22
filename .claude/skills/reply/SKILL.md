---
name: reply
description: Identify a lead's pipeline stage from their reply and draft the next message. Trigger with "/reply [paste]", "they replied", "got a response", or paste a reply directly.
disable-model-invocation: true
argument-hint: [pasted-reply]
---

## What This Skill Does

Takes a pasted reply from a lead, identifies where they are in NINE's pipeline, and drafts the ideal next message to advance the conversation.

## Pipeline stages (in order)

Found → Emailed → DM'd → Replied → Warm → Call Booked → Proposal Sent → Won → Lost

## Stage identification rules

Read the reply tone and content, then classify:

| Signal | Stage |
|---|---|
| First reply, positive/curious | Replied |
| Asking questions, engaged, wants to know more | Warm |
| Agrees to a call / picks a time | Call Booked |
| Asks for pricing, proposal, or deck | Proposal Sent |
| Signs, pays, says "let's do it" | Won |
| Hard no, unsubscribe, not interested | Lost |

## Next message rules by stage

**Replied → Warm:** Answer their question directly. Add one piece of proof (reel example, result, case study). Keep CTA: "Worth a 15-min chat this week?"

**Warm → Call Booked:** Confirm the call. Send a calendar link or propose 2–3 time slots. One sentence on what you'll cover.

**Call Booked → Proposal Sent:** Thank them for the call. Summarise what you heard (their pain, their goal). Attach or link the Content Sprint proposal.

**Proposal Sent → Won:** Follow up if no response in 3 days. One line: reiterate the biggest benefit you discussed. CTA: "Any questions before we kick off?"

**Lost:** Acknowledge gracefully. Leave the door open. No hard sell. "No problem at all — if anything changes or you want to revisit later, I'm here."

## Execution

1. Ask user to paste the reply if not already provided
2. Identify stage
3. Draft the next message
4. Print:

```
**Stage identified:** {stage}
**Next action:** {one line}

---
**Draft reply:**

{message}
---
```

5. "Run /crm to log this reply and update their stage."
