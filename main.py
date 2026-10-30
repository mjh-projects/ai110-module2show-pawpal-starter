"""Temporary testing ground: run the PawPal+ logic in the terminal.

Usage:  python main.py
"""

from datetime import date, time

# Bring in the backend classes from the logic layer.
from pawpal_system import Owner, Pet, Priority, Scheduler, Task

# Create an owner and give them two pets.
owner = Owner("Jordan", "Smith")
rex = Pet("Rex", "dog", age=4)
whiskers = Pet("Whiskers", "cat", age=2)
owner.add_pet(rex)
owner.add_pet(whiskers)

# Add tasks to the pets. preferred_time pins a task to a specific time of day.
# ADDED: added out of chronological/priority order on purpose (evening task
# first, morning task last) so the output actually proves sort_by_time() and
# sort_by_priority() are sorting, not just echoing insertion order.
rex.add_task(
    Task("Evening medication", 5, Priority.MEDIUM, category="meds", preferred_time=time(18, 0))
)
# A task with no preferred time: the scheduler picks the earliest free gap.
whiskers.add_task(Task("Play time", 15, Priority.LOW, category="enrichment"))
# ADDED: same preferred_time as "Morning walk" below, on purpose, so two
# pinned tasks for different pets collide. The scheduler places one (ties
# break by shorter duration, so Breakfast wins) and skips the other instead
# of double-booking it - demonstrates the overlap handling in generate_plan()
# and explain()'s "Skipped" section.
whiskers.add_task(
    Task("Breakfast", 10, Priority.HIGH, category="feeding", preferred_time=time(7, 30))
)
rex.add_task(
    Task("Morning walk", 30, Priority.HIGH, category="exercise", preferred_time=time(7, 30))
)

# Build today's schedule: start at 7:00 with 90 minutes of task time available.
today = date.today()
schedule = Scheduler().generate_plan(
    owner, on=today, start_time=time(7, 0), available_minutes=90
)

# Save it on the owner (one schedule per day), then print it.
owner.set_schedule(schedule)

print(f"Today's Schedule for {owner.full_name()}")
print("=" * 40)
print(schedule.explain())
