---
id: eng-001
title: On-call and incident response
owner: Engineering (Tomás Reyes, Chief Technology Officer)
updated: 2026-07-14
status: current
audience: engineers and the operations team
---

# On-call and incident response

## Severity levels

| Level | Meaning | Examples | Acknowledge within |
|---|---|---|---|
| SEV1 | Customers cannot order or pay | The app is down in a city; more than 5% of payments fail for 10 minutes | **15 minutes** |
| SEV2 | An important feature is broken or slow | Order tracking stops updating; restaurant tablets miss orders | **30 minutes** |
| SEV3 | A minor problem with a workaround | A report is late; one menu shows wrong photos | Next working day |

When in doubt, choose the higher severity. It is easy to lower it later.

## The rota

* On-call shifts last one week, **from Tuesday 10:00 to the next Tuesday 10:00**.
* Each shift has a primary and a secondary engineer. If the primary does not acknowledge a page in time, the secondary is paged.
* Swap shifts with a colleague in the paging tool and tell your manager.
* Before your shift, read the last handover note and check that paging works on your phone.

## During an incident

1. Acknowledge the page.
2. For a SEV1, name an **incident commander**, who coordinates and does not debug.
3. Open a channel named after the incident and post updates in #incidents **every 30 minutes** until it is resolved.
4. Fix the customer impact first (roll back, switch off a feature flag), and find the root cause later.

## After an incident

* Write a **blameless postmortem within 5 working days** for every SEV1 and SEV2: what happened, the timeline, the impact, why it happened and the actions that prevent it from happening again.
* Each action has an owner and a due date.

## Pay and rest

* **On-call allowance: 250 per week on call**, plus **40 per hour** of work when you are paged outside working hours.
* If a page keeps you working for more than 2 hours at night (22:00 to 06:00), take the next morning off.
