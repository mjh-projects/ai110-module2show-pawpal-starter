# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output
```
Today's Schedule for Jordan Smith
========================================
Plan for 2026-10-21 (60 of 90 min used):
  07:00-07:15 Play time for Whiskers [low, 15 min]
  07:30-08:00 Morning walk for Rex [high, 30 min] (at its preferred time)
  08:15-08:25 Breakfast for Whiskers [high, 10 min] (at its preferred time)
  18:00-18:05 Evening medication for Rex [medium, 5 min] (at its preferred time)

```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## Implementation Summary
PawPal+ is a Python logic layer that builds a daily care schedule for a pet owner. It lives in `pawpal_system.py`, with a terminal demo in `main.py` and tests in `tests/test_pawpal.py`.

An `Owner` has one or more `Pet`s, and each `Pet` has a list of `Task`s. A task records its duration, priority, optional preferred time of day, and how often it repeats. `Task.is_due()` uses the repeat setting and the date the task was last completed to decide whether it belongs on a given day's plan.

The `Scheduler` builds the plan. It asks the owner for every pet's tasks, keeps the ones due that day, and sorts them by priority, with shorter tasks first on ties. Tasks pinned to a preferred time go on the timeline first. The rest take the earliest free gap, as long as the total stays within the owner's available minutes. Because all pets share one timeline, tasks never overlap. Tasks that don't fit go on a skipped list.

The result is a `Schedule` made of `ScheduledTask`s, each with a start time, an end time and a status (pending, done or skipped). The owner keeps one schedule per day. `Schedule.explain()` prints the plan with pet names and the skipped tasks, and `has_conflict()` checks it for overlaps. When a scheduled task is marked done, it also records the completion date on its `Task`, so recurring tasks come due again at the right time.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.


| Feature | Method(s) | Notes |
|---|---|---|
| Task sorting | `Scheduler.sort_by_priority()`, `Task.priority_value()` | Sorts by priority, highest first; ties go to the shorter task |
| Filtering | `Task.is_due()`, `Scheduler.generate_plan()` | Skips tasks not due that day or that don't fit the time budget |
| Conflict handling | `Schedule.has_conflict()`, `Scheduler.generate_plan()` | Never places overlapping tasks; checks a finished schedule for overlaps |
| Recurring tasks | `Task.is_due()`, `Task.mark_complete()`, `ScheduledTask.mark_done()` | Records the last completed date and uses frequency to decide when a task is due again |


## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
