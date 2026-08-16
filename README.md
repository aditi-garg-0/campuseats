# CampusEats

## Repository Overview

This repository is the working record of CampusEats, a campus scale food ordering system conceived as the semester long project for **CS 543: Web Services**, taught by Dr. Pramit Mazumdar, Department of CSE, IIIT Vadodara. It contains the foundation on which the code will be built: a demonstrated understanding of the HTTP protocol at the level of individual bytes on the wire, an inspection of how a real, production website actually behaves under network load, and a settled statement of what CampusEats is, expressed in terms precise enough to become an API contract.

The repository has now been extended with **Assignment 2**, which takes the initial CampusEats brief and develops it into a service-oriented design. It defines the system capabilities, service boundaries, service contracts, the central `placeOrder()` operation, service-property validation, and the database schema.

---

## Group Information

**Group No.: 7**

| Role | Name | Student ID |
|---|---|---|
| Group Leader | Aditi Garg | 20251651008 |
| Group Member | Neha Nupur | 20251651064 |
| Group Member | Shivam Kumar Soni | 20251651084 |

---

## The Problem CampusEats Addresses

At any institute with a fixed lecture schedule and a limited number of food outlets, the same failure mode repeats itself daily. A break between two lectures is typically fifteen to twenty minutes. A student who wishes to eat during that window must walk to an outlet, wait in a physical queue behind however many people arrived first, place an order verbally or by pointing, wait for it to be prepared, and walk back, all within that window. When the queue is long, one of two outcomes follows: the student misses part of their next lecture, or the student does not eat. Neither outcome is acceptable, and neither is a failure of the food outlet itself, which is usually operating at or near its physical serving capacity. The failure is structural: the queue exists because ordering and preparation are forced to happen sequentially, at the counter, in real time.

CampusEats separates these two steps. A student browses a menu and places an order from wherever they are, before walking to the outlet at all. The outlet receives that order immediately, as a discrete, queued item, and can begin preparing it well before the student physically arrives. The queue does not disappear, but it moves from the counter, where it consumes a student's limited break time, to the kitchen, where it consumes only the outlet's own preparation time. This is the entire premise of the system, and it is deliberately narrow: no delivery riders, no city wide logistics, no payment aggregation beyond what a single institute requires. It is food delivery infrastructure reduced to the smallest version of itself that still solves the actual problem.

---

## Repository Structure

The repository contains the deliverables from both assignments.

```text
campuseats/
├── README.md
├── brief.md
│
├── docs/
│   ├── http-log.md
│   ├── network-analysis.md
│   ├── screenshot-1.png
│   ├── screenshot-2.png
│   ├── screenshot-3.png
│   ├── screenshot-4.png
│   ├── screenshot-5.png
│   ├── screenshot-6.png
│   ├── screenshot-7.png
│   └── screenshot-8.png
│
└── Assignment 2/
    ├── Task 1, 3, 4, 6/
    │   └── design.pdf
    │
    ├── Task 2/
    │   ├── services.drawio
    │   └── services.png
    │
    └── Task 5/
        ├── schema.drawio
        ├── schema.png
        └── schema.sql
````

---

## Assignment 1: HTTP by Hand and Project Foundation

Assignment 1 established the technical foundation for CampusEats. It focused on understanding HTTP communication before implementing the actual application.

The repository contains the following work:

* `http-log.md` — HTTP requests and responses captured using `curl`
* `network-analysis.md` — analysis of a real website's network activity using browser DevTools
* `brief.md` — the initial CampusEats system brief
* Network screenshots supporting the analysis

---

## Assignment 2: Service Design and Database

Assignment 2 takes the CampusEats idea defined in the first assignment and turns it into a structured service-oriented design.

It defines the **16 capabilities** of the system, including identity, catalogue management, order management, payment, feedback, administration, and notifications.

The design is divided into six services:

1. **Identity & Access Service**
2. **Catalogue Service**
3. **Order Service**
4. **Payment Service**
5. **Feedback Service**
6. **Notification & Admin Reporting Service**

The two main services are the **Catalogue Service** and **Order Service**, while the remaining four provide supporting functionality. The design contains **44 operations across the six services**.

Assignment 2 also specifies the central `placeOrder()` operation, including its input, output, validation rules, error cases, internal processing, and cross-service calls. It also defines the database schema and validates the service properties of the designed services.

---

## Rationale: Why This Assignment Precedes Any Application Code

A natural instinct, on being assigned a project such as CampusEats, is to open a code editor and begin writing an Express server immediately. This assignment deliberately withholds that step, and the reasoning behind the withholding is worth stating explicitly, since it governs everything in this repository.

A web framework such as Express exists to hide the request and response cycle from the developer. It parses the request line, assembles the response headers, and serializes the body, all so that the developer need only write `res.json(obj)` and trust that the correct bytes will appear on the wire. This is a reasonable convenience once the underlying mechanism is understood, but it is a dangerous shortcut when it is not. A developer who has never read a raw HTTP response by hand does not have a working intuition for questions that CampusEats will need answered correctly and early: what status code should be returned when an order is placed against an outlet that has just closed, what header should point a client toward a newly created order resource, what the correct behaviour is when a client requests a menu item that has been deleted. These are not framework questions. They are protocol questions, and the only reliable way to develop an intuition for them is to first observe how an existing, well designed API answers them.

This is the purpose of `http-log.md`. Before CampusEats has a single route of its own, five requests were issued by hand against a public API using `curl`, with the full raw response captured and read line by line: the status line, every header, the blank line separating headers from body, and the body itself. One of the five requests was made deliberately against a resource that does not exist, specifically to observe and document how a well behaved API reports failure, namely with a correctly formatted `404` response and an appropriate `Content-Type`, rather than a broken page or an unhandled exception. Each of the five request and response pairs is annotated with a short, precise note explaining what its status code and its `Content-Type` header communicate to a client.

`network-analysis.md` extends this same discipline from a single request to an entire page load. A browser loading a modern website does not issue one request and wait for one response; it issues dozens or hundreds of requests in parallel, some of which redirect, some of which fail silently, and one of which is invariably the bottleneck that determines how long the user actually waits. Reading that waterfall correctly, identifying the single slowest resource and understanding why it was slow, distinguishing a genuine error from an intentional `204 No Content` response, is the same skill as reading a single `curl` response, applied at the scale CampusEats will eventually need to operate at once real students are placing real orders concurrently.

---

## The System, Stated Precisely

`brief.md` contains the full statement, but its structure is worth previewing here, since it is the structure that the eventual API will inherit directly. CampusEats is described in terms of its nouns, the persistent things the system must store state about: users, outlets, menu items, orders, order items, payments, reviews, and notifications. It is described equally in terms of its verbs, the actions a client is permitted to take against those nouns: browsing a menu, placing an order, updating an order's status as it moves from placed toward collected, marking a menu item as sold out, paying for an order, and leaving a review once it is complete. This is not incidental phrasing. A noun becomes a resource, addressed by a URL. A verb becomes an HTTP method applied to that resource, together with a status code that reports what happened. The entire reason this repository begins with raw HTTP rather than a framework is so that, when this mapping is finally implemented, every status code chosen for CampusEats will have been chosen with the same deliberateness observed in `http-log.md`, rather than accepted as whatever a framework happened to default to.

Assignment 2 extends this foundation by mapping these capabilities into explicit services and contracts. Each service owns its own persistent data and communicates with other services through defined operations rather than directly accessing another service's database. The central `placeOrder()` operation connects identity validation, catalogue validation, order creation, payment, and notification while keeping these responsibilities separated between services.

---

## Commit History

```bash
git log --oneline
```

The commits in this repository were made incrementally, as each deliverable was completed, rather than as a single combined submission at the end. The sequence visible in the log, scaffold, then the HTTP log, then the brief, then the network analysis, followed by the Assignment 2 design and schema work, reflects the progression of the project and is intended to stand as a readable account of that process rather than a formality.

---

## Reproducing the HTTP Log

Every command referenced in `http-log.md` can be run exactly as written, against the same live, public API used throughout this submission:

```bash
curl -i https://jsonplaceholder.typicode.com/users/1
curl -i https://jsonplaceholder.typicode.com/posts/1
curl -i https://jsonplaceholder.typicode.com/posts/9999
curl -i -X POST -H "Content-Type: application/json" -d '{"title":"hi"}' https://jsonplaceholder.typicode.com/posts
curl -I https://jsonplaceholder.typicode.com/users/1
```

---

## Current Project Status

### Completed

* Assignment 1 — HTTP and project foundation
* HTTP request/response analysis
* Browser network analysis
* CampusEats system brief
* Assignment 2 capability design
* Service architecture and boundaries
* Service contracts
* `placeOrder()` specification
* Service property validation
* Database schema and diagrams

### Next Phase

The next stage of CampusEats is the implementation of the designed services and APIs, followed by database integration, service integration, testing, and development of the complete application.

---

## Project Team

**Group 7**

* **Aditi Garg** — Group Leader — `20251651008`
* **Neha Nupur** — Group Member — `20251651064`
* **Shivam Kumar Soni** — Group Member — `20251651084`

---

## Project Direction

The repository currently contains the analysis, requirements, service design, contracts, diagrams, and database foundation of CampusEats. The work completed so far establishes the architecture that will be used for the implementation phase of the project.

CampusEats is intentionally kept focused on the campus food-ordering problem: students browse a campus outlet menu, place an order, track it, pay for it, and review it, while outlet staff manage availability and order status and administrators manage the platform.

```
