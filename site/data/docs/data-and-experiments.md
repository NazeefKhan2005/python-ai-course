---
id: data-001
title: Data, metrics and experiments
owner: Data Team (data@colibri.example)
updated: 2026-10-05
status: current
audience: all employees who use data
---

# Data, metrics and experiments

## Where the data is

* **Faro** is our data platform. It has dashboards for every team and SQL access to the main tables: orders, customers, restaurants and promotions.
* Customer data in Faro is pseudonymised (see Customer data and privacy).
* Ask for access in Nido. Access to Confidential tables needs your manager's approval.

## Metric definitions

Use these definitions in every report, so that numbers from different teams agree.

| Metric | Definition |
|---|---|
| Order | An order a customer placed, whatever its status |
| Delivered order | An order with the status "delivered"; only delivered orders count towards revenue |
| Average order value (AOV) | Total of delivered orders divided by the number of delivered orders |
| Late order | A delivered order whose delivery time is longer than the promised time shown at checkout |
| Late share | Late orders divided by delivered orders |
| Repeat order | An order from a customer who had ordered before |
| 30-day repeat rate | Of the customers who made their first order in a period, the share who ordered again within 30 days of that first order |
| Active customer | A customer with at least one order in the last 28 days |

**Complete windows only.** A customer whose first order was less than 30 days before the end of the data has not had a full 30 days to order again. Leave such customers out of the 30-day repeat rate; otherwise the rate looks lower than it is for the most recent customers.

## Experiments

* **Write the plan first:** the hypothesis, the primary metric, the smallest effect worth detecting, the sample size and the run time. Share it in #experiments before the start.
* Run every experiment for **at least 14 days**, so that it covers two full weeks with their weekends.
* Randomise by customer, not by order, so that each customer always sees the same version.
* Decide at the planned end, not when the result first looks good. Checking early and stopping when a result looks significant makes false positives much more likely.
* Report the result with a confidence interval, including experiments that did not work.

## Dashboards and reports

* Every dashboard shows its owner, its data source and when the data was last updated.
* Charts start bar axes at zero and say what each axis shows, with units.

Head of Data: Yuki Tanaka (data@colibri.example).
