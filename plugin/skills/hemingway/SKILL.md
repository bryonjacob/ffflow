---
name: hemingway
description: Ruthless concision for prompts and documentation — cut 30-50% of words, every sentence earns its place
---

# Hemingway: Economy of Language

## Philosophy

Every word earns its place. No word wasted. AI context is expensive — concision is engineering efficiency.

**Anti-inspiration:** Dickens. Verbose exposition. Excessive adjectives. Everything we avoid.

## Principles

### Active Voice, Present Tense
**No:** "The system will be using a database that has been configured."
**Yes:** "System stores data in database."

### Remove Filler
Cut: actually, basically, essentially, generally, literally, really, very, quite, just, simply, clearly, obviously.

**No:** "We basically just need to simply verify authentication."
**Yes:** "Verify authentication."

### Concrete Over Abstract
**No:** "Facilitate the implementation of a solution for managing state."
**Yes:** "Manage state."

### Delete Redundancy
**No:** "Each individual user has their own personal preferences."
**Yes:** "Users have preferences."

### Short Words
Use over utilize. Start over initiate. End over terminate. Get over retrieve. Make over construct.

### One Idea Per Sentence
Break compound sentences. Each sentence does one job.

### Cut Ceremony
No pleasantries, apologies, hedging. Do the work.

### Lists Over Prose
When enumerating, use bullets. Not a run-on sentence with commas.

## Application

**Prompts:**
```
No:  "I would like you to please help me analyze this codebase to identify
      potential areas where we might improve performance."
Yes: "Find performance bottlenecks in this codebase."
```

**CLAUDE.md context:**
```
No:  "This module is responsible for handling all aspects related to
      user authentication within the system, including login, logout,
      session management, and token handling."
Yes: "Handles authentication: login, logout, sessions, tokens."
```

## How to Apply

**New content:** Write draft. Cut 30-50% of words. Verify meaning preserved. Ship lean version.

**Existing content:** Read sentence by sentence. Ask: "Does this word earn its place?" Delete filler, combine redundant sentences, replace abstract with concrete.

## When to Break Rules

- Technical precision requires extra words
- Ambiguity would result from cutting
- External-facing docs need formality

These are rare. Default to ruthless.

Not one word wasted.
