---
id: eng-002
title: Engineering practices
owner: Engineering (Tomás Reyes, Chief Technology Officer)
updated: 2026-09-01
status: current
audience: engineers
---

# Engineering practices

## Code review

* Every change goes through a pull request.
* A pull request needs **at least 1 approving review** from another engineer, and **2 reviews** for code that handles payments, authentication or customer data.
* Continuous integration must pass before merging. Bug fixes come with a test that fails without the fix.
* Keep pull requests small: under 400 changed lines when you can.

## Deploying

* Deploy any working day, but **not after 15:00 on Fridays**.
* No deploys during **peak hours: 12:00 to 14:00 and 19:00 to 21:00** local time in any of our cities.
* **Change freeze from 26 November to 2 December** every year (the Black Friday week): only fixes for SEV1 and SEV2 incidents, approved by the CTO.
* Risky changes go behind a **feature flag** and roll out in steps: 5% of customers, then 25%, then 100%, with at least 1 hour between steps.
* If error rates rise after a deploy, roll back first and investigate later.

## Services and data

* Every service has an owner team, a runbook and dashboards for errors, latency and traffic.
* Logs never contain Restricted data (see Customer data and privacy).
* Database changes must work with both the old and the new version of the code, so that we can roll back.

## Machine learning models

* Every model in production has a model card: its purpose, training data, metrics, known limits and owner.
* A new model version must beat the current one on the agreed metric on a held-out test set, and the Data Team must approve it before release.
* Models are monitored for data drift; an alert opens a ticket for the owner team.
