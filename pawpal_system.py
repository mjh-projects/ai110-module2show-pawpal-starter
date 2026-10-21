"""PawPal+ logic layer: backend classes for owners, pets, tasks and scheduling.

Revised skeleton (assignment 1b). Every line marked "CHANGE" differs from the
first skeleton and explains why.
"""

# CHANGE: postponed annotation evaluation lets classes refer to each other
# (e.g. Schedule -> Owner) and lets us write "X | None" without import tricks.
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


# CHANGE: priority was a free-form str. An Enum prevents typos like "hgih" and
# gives priority_value() one obvious ordering to rely on.
class Priority(Enum):
    """How important a task is; the value is used to sort tasks."""

    HIGH = 3
    MEDIUM = 2
    LOW = 1


# CHANGE: new enum for the state of one scheduled activity. A single
# `completed` bool could only say "done / not done"; this also covers
# "skipped by the owner today", which the scheduler's `skipped` list (tasks that
# never fit) cannot express.
class Status(Enum):
    """The state of one scheduled activity on a given day."""

    PENDING = "pending"  # on today's plan, not done yet (the starting state)
    DONE = "done"  # the owner finished it
    SKIPPED = "skipped"  # the owner chose not to do it today


# CHANGE: helper so every Task/Pet gets a unique id. Titles and names are not
# guaranteed unique, so lookups and links by title/name were ambiguous.
def _new_id() -> str:
    """Return a new unique id string for a task or pet."""
    return uuid.uuid4().hex


# CHANGE: helpers for the scheduler's time arithmetic. datetime.time objects
# can't be added to, so the scheduler works in "minutes since midnight" (plain
# integers) and converts to and from time objects at the edges.
_MINUTES_PER_DAY = 24 * 60  # 1440; a task may not run past the end of the day


def _to_minutes(t: time) -> int:
    """Convert a time of day to minutes since midnight."""
    # 08:30 -> 510
    return t.hour * 60 + t.minute


def _to_time(minutes: int) -> time:
    """Convert minutes since midnight to a time of day."""
    # 510 -> 08:30. Callers keep `minutes` below _MINUTES_PER_DAY.
    return time(minutes // 60, minutes % 60)


@dataclass
class Task:
    """A care activity for a pet, with its duration, priority and recurrence."""

    title: str
    duration_minutes: int
    priority: Priority  # CHANGE: str -> Priority enum (see above)
    category: str = ""
    frequency: str = "daily"  # "daily" or "weekly"
    # CHANGE: weekly tasks need to know which weekdays they belong on
    # (0 = Monday ... 6 = Sunday); empty means "every day". Without this the
    # scheduler cannot tell which tasks to include on a given date.
    days_of_week: list[int] = field(default_factory=list)
    # CHANGE: optional fixed time. This is what makes Schedule.has_conflict()
    # meaningful: back-to-back scheduling alone can never overlap.
    preferred_time: time | None = None
    # CHANGE: unique id so Pet.edit_task / remove_task can't hit the wrong task
    # when two tasks share a title.
    task_id: str = field(default_factory=_new_id)
    # CHANGE: pet_name (str) -> pet_id. A name can be duplicated or renamed;
    # an id keeps the link between a task and its pet stable. Set by
    # Pet.add_task().
    pet_id: str = ""
    # CHANGE: bool `completed` -> last_completed date. A bool can't reset for
    # a new day, and frequency has nothing to act on without knowing when the
    # task was last done.
    last_completed: date | None = None

    def mark_complete(self, on: date) -> None:
        """Record `on` as the day this task was last completed."""
        # CHANGE: takes the date so last_completed can be recorded.
        # Remember the day this task was finished; is_due() reads this to
        # decide when a recurring task should show up again.
        self.last_completed = on

    def is_due(self, on: date) -> bool:
        """Return True if this task belongs on the plan for date `on`."""
        # CHANGE: new method. Combines frequency, days_of_week and
        # last_completed so the scheduler can ask "should this task be on the
        # plan for this date?" in one place.

        # Step 1: weekday filter. If the task is pinned to certain weekdays
        # (0 = Monday ... 6 = Sunday) and `on` isn't one of them, it's not due.
        # An empty list means "no restriction", so we skip this check.
        if self.days_of_week and on.weekday() not in self.days_of_week:
            return False

        # Step 2: never completed before, so it is due.
        if self.last_completed is None:
            return True

        # Step 3: how many days have passed since it was last done?
        days_since = (on - self.last_completed).days

        # Step 4a: a weekly task with no fixed weekday repeats every 7 days
        # from the last time it was done.
        if self.frequency == "weekly" and not self.days_of_week:
            return days_since >= 7

        # Step 4b: everything else (daily, or weekly pinned to weekdays) is
        # due again as long as it wasn't already done on `on` itself. Using
        # `> 0` also keeps today's finished task off a regenerated plan.
        return days_since > 0

    def priority_value(self) -> int:
        """Return the priority as an integer (HIGH=3, MEDIUM=2, LOW=1)."""
        # The number behind the Priority enum (HIGH=3, MEDIUM=2, LOW=1), so
        # the scheduler can sort tasks by a plain integer.
        return self.priority.value


@dataclass
class Pet:
    """A pet and the list of care tasks it needs."""

    name: str
    species: str
    age: int = 0
    # CHANGE: pets get an id too, so Task.pet_id has something to point at.
    pet_id: str = field(default_factory=_new_id)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and link it to the pet by id."""
        # CHANGE (behavior note): must set task.pet_id = self.pet_id.
        # Stamp the task with this pet's id so the link from task to pet is
        # always set, no matter who created the Task.
        task.pet_id = self.pet_id
        # Then store it in this pet's task list.
        self.tasks.append(task)

    # CHANGE: edit/remove take task_id instead of title (titles may repeat).
    def edit_task(self, task_id: str, task: Task) -> None:
        """Replace the task with the given id, or raise ValueError if missing."""
        # Walk the list with its positions so we can replace in place.
        for i, existing in enumerate(self.tasks):
            if existing.task_id == task_id:
                # Keep the original id, so anything that refers to this task
                # (e.g. a ScheduledTask) still points at the right one.
                task.task_id = existing.task_id
                # Make sure the replacement is linked to this pet too.
                task.pet_id = self.pet_id
                # Swap the old task for the new one at the same position.
                self.tasks[i] = task
                return
        # Nothing matched: fail loudly so a wrong id is noticed, not ignored.
        raise ValueError(f"No task with id {task_id!r} for pet {self.name!r}")

    def remove_task(self, task_id: str) -> None:
        """Delete the task with the given id, or raise ValueError if missing."""
        # Find the task by id (not title, which may repeat) and delete it.
        # Past Schedules that already contain it keep their own reference,
        # so history is not rewritten.
        for i, existing in enumerate(self.tasks):
            if existing.task_id == task_id:
                del self.tasks[i]
                return
        # Nothing matched: raise the same error as edit_task.
        raise ValueError(f"No task with id {task_id!r} for pet {self.name!r}")


@dataclass
class ScheduledTask:
    """One task placed at a specific time on a day's schedule, with its status."""

    task: Task
    # CHANGE: str -> datetime.time. Adding durations and comparing times is
    # error-prone on strings like "8:30" vs "08:30".
    start_time: time
    end_time: time
    # CHANGE: `completed: bool` -> `status: Status`. The state for *this day*
    # still lives here, not on the shared Task, so checking off today's walk
    # doesn't mark every future walk done. New items begin as PENDING.
    status: Status = Status.PENDING

    # CHANGE: read-only shortcuts that forward to the wrapped Task. The Task
    # stays the single source of truth for what the activity is; these just
    # save callers from writing `item.task.title` everywhere.
    @property
    def title(self) -> str:
        """Return the wrapped task's title."""
        # The activity's name, e.g. "Morning walk".
        return self.task.title

    @property
    def duration_minutes(self) -> int:
        """Return the wrapped task's duration in minutes."""
        # How long the activity takes, taken from the task (not from the
        # start/end times, so the two can't drift apart).
        return self.task.duration_minutes

    @property
    def frequency(self) -> str:
        """Return the wrapped task's frequency ("daily" or "weekly")."""
        # "daily" or "weekly". Frequency belongs to the task, not to one
        # day's placement, so we only forward it here.
        return self.task.frequency

    @property
    def is_done(self) -> bool:
        """Return True if this scheduled task's status is DONE."""
        # Bool-style check so code that only cares "finished or not" stays
        # simple; replaces reading the old `completed` flag.
        return self.status is Status.DONE

    def mark_done(self, on: date) -> None:
        """Mark this scheduled task DONE and record `on` on its Task."""
        # CHANGE: one call finishes the activity everywhere it needs to.
        # 1) Record that this scheduled instance is done.
        self.status = Status.DONE
        # 2) Tell the underlying Task the date, so Task.is_due() knows a
        #    recurring task was just done and won't be due again until its
        #    frequency says so. `on` is a parameter because ScheduledTask
        #    doesn't know which day's Schedule it belongs to.
        self.task.mark_complete(on)

    def mark_skipped(self) -> None:
        """Mark this scheduled task SKIPPED without touching its Task."""
        # The owner chose not to do this today. Only the status changes:
        # the Task's last_completed is left alone, so it stays due later.
        self.status = Status.SKIPPED


@dataclass
class Schedule:
    """One day's plan: the tasks scheduled at set times and the ones skipped."""

    date: date  # CHANGE: str -> datetime.date
    start_time: time  # CHANGE: str -> datetime.time
    available_minutes: int
    # CHANGE: back-reference to the owner, so a Schedule passed around on its
    # own still says whose plan it is. repr/compare are off because
    # Owner -> Schedule -> Owner would otherwise recurse forever in repr().
    owner: Owner | None = field(default=None, repr=False, compare=False)
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def total_minutes(self) -> int:
        """Return the total duration of all scheduled tasks in minutes."""
        # Add up the duration of every scheduled task: the time this plan
        # actually uses, to compare against available_minutes.
        return sum(item.task.duration_minutes for item in self.scheduled)

    def has_conflict(self) -> bool:
        """Return True if any two scheduled tasks overlap in time."""
        # CHANGE (behavior note): now meaningful because Task.preferred_time
        # can pin tasks to overlapping slots. Sort by start time, then compare
        # neighbours (O(n log n)) rather than every pair (O(n^2)).

        # Put the items in time order first, so any overlap must be between
        # two items that sit next to each other.
        ordered = sorted(self.scheduled, key=lambda item: item.start_time)
        # zip(ordered, ordered[1:]) pairs each item with the one after it.
        for earlier, later in zip(ordered, ordered[1:]):
            # Overlap only if the later task starts BEFORE the earlier one
            # ends. Starting exactly when it ends (8:30 / 8:30) is fine.
            if later.start_time < earlier.end_time:
                return True
        # No neighbouring pair overlapped.
        return False

    def explain(self) -> str:
        """Return a readable text summary of the plan and any skipped tasks."""
        # Map pet_id -> pet name so each line can say which pet a task is
        # for. Empty if the schedule isn't linked to an owner.
        pet_names = {}
        if self.owner is not None:
            pet_names = {pet.pet_id: pet.name for pet in self.owner.pets}

        # Header: the day and how much of the time budget the plan uses.
        lines = [
            f"Plan for {self.date.isoformat()} "
            f"({self.total_minutes()} of {self.available_minutes} min used):"
        ]

        # One line per scheduled task, in time order.
        for item in sorted(self.scheduled, key=lambda i: i.start_time):
            task = item.task
            # Pet name if we can find it, otherwise leave it out.
            pet = pet_names.get(task.pet_id, "")
            who = f" for {pet}" if pet else ""
            # Tasks that asked for a specific time get a note saying so.
            pinned = " (at its preferred time)" if task.preferred_time else ""
            lines.append(
                f"  {item.start_time:%H:%M}-{item.end_time:%H:%M} {task.title}{who} "
                f"[{task.priority.name.lower()}, {task.duration_minutes} min]{pinned}"
            )
        # Say so explicitly instead of printing just a header.
        if not self.scheduled:
            lines.append("  Nothing scheduled.")

        # Skipped section. `skipped` holds only the tasks, not a reason per
        # task, so the reason given here is the general one.
        if self.skipped:
            remaining = self.available_minutes - self.total_minutes()
            lines.append("Skipped:")
            for task in self.skipped:
                lines.append(
                    f"  {task.title} [{task.priority.name.lower()}, "
                    f"{task.duration_minutes} min] - did not fit "
                    f"({remaining} min left, or its time slot was taken)"
                )

        # Join all the lines into one block of text.
        return "\n".join(lines)


@dataclass
class Owner:
    """A pet owner who has pets and at most one schedule per day."""

    first_name: str
    last_name: str
    pets: list[Pet] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)

    def full_name(self) -> str:
        """Return the owner's first and last name as one string."""
        # Join first and last name with a space. strip() removes the stray
        # space that would be left over if one of the names is empty.
        return f"{self.first_name} {self.last_name}".strip()

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        # Store the pet in the owner's list; an owner can have any number.
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task from every pet as one flat list."""
        # Flatten "every task of every pet" into one list. The scheduler
        # uses this so all pets' tasks are planned as a single timeline.
        return [task for pet in self.pets for task in pet.tasks]

    def set_schedule(self, schedule: Schedule) -> None:
        """Store a schedule, replacing any existing one for the same date."""
        # CHANGE (behavior note): replaces any existing schedule for
        # schedule.date (one per day) and sets schedule.owner = self.
        # Link the schedule back to this owner.
        schedule.owner = self
        # Keep only schedules for OTHER dates, dropping any old one for this
        # date, so there is never more than one schedule per day.
        self.schedules = [s for s in self.schedules if s.date != schedule.date]
        # Then add the new schedule.
        self.schedules.append(schedule)

    # CHANGE: date: str -> date, and the return type is now `Schedule | None`
    # because there may be no schedule for that day yet.
    def get_schedule(self, on: date) -> Schedule | None:
        """Return the schedule for date `on`, or None if there isn't one."""
        # Look for the schedule whose date matches and return it.
        for schedule in self.schedules:
            if schedule.date == on:
                return schedule
        # No schedule exists for that day yet.
        return None


class Scheduler:
    """Builds a daily Schedule from an owner's tasks and available time."""

    # CHANGE: date/start_time use real date/time types (see Schedule).
    def generate_plan(
        self, owner: Owner, on: date, start_time: time, available_minutes: int
    ) -> Schedule:
        """Build a one-day Schedule for the owner's due tasks within the time budget."""
        # CHANGE (behavior note): only include tasks where task.is_due(on).

        # Step 1: start with an empty schedule for this day, linked to the
        # owner so explain() can look up pet names.
        schedule = Schedule(
            date=on,
            start_time=start_time,
            available_minutes=available_minutes,
            owner=owner,
        )

        # Step 2: gather every pet's tasks, keep only the ones due today,
        # then order them from most to least important.
        due = [task for task in owner.get_all_tasks() if task.is_due(on)]
        ordered = self.sort_by_priority(due)

        # Bookkeeping: time blocks already used, as (start, end) pairs in
        # minutes since midnight, and the total task minutes placed so far.
        taken: list[tuple[int, int]] = []
        used = 0

        def overlaps(start: int, end: int) -> bool:
            """Return True if the block [start, end) overlaps any placed task."""
            # Two blocks overlap when each one starts before the other ends.
            # Touching blocks (one ends exactly when the next starts) don't.
            return any(start < t_end and t_start < end for t_start, t_end in taken)

        def place(task: Task, start: int) -> None:
            """Put the task on the schedule starting at `start` minutes."""
            # Record the task at `start`: reserve its block, add its minutes
            # to the budget used, and add it to the schedule as a
            # ScheduledTask with real time-of-day values.
            nonlocal used
            end = start + task.duration_minutes
            taken.append((start, end))
            used += task.duration_minutes
            schedule.scheduled.append(
                ScheduledTask(task, _to_time(start), _to_time(end))
            )

        # Step 3: tasks pinned to a preferred time go first so flexible tasks
        # are fitted around them. Everything else waits in `flexible`.
        flexible: list[Task] = []
        for task in ordered:
            if task.preferred_time is None:
                flexible.append(task)
                continue
            start = _to_minutes(task.preferred_time)
            end = start + task.duration_minutes
            # Keep the requested slot only if there is budget left, it ends
            # before midnight, and nothing already placed overlaps it.
            if (
                used + task.duration_minutes <= available_minutes
                and end <= _MINUTES_PER_DAY
                and not overlaps(start, end)
            ):
                place(task, start)
            else:
                # The owner asked for that exact time, so we don't move it;
                # it is reported as skipped instead.
                schedule.skipped.append(task)

        # Step 4: flexible tasks, highest priority first. Each takes the
        # earliest free gap at or after the day's start time.
        day_start = _to_minutes(start_time)
        for task in flexible:
            # Out of budget: skip without searching for a gap.
            if used + task.duration_minutes > available_minutes:
                schedule.skipped.append(task)
                continue
            # Try the day's start, and whenever the spot is blocked, jump to
            # the end of the blocking task and try again.
            start = day_start
            while True:
                end = start + task.duration_minutes
                if end > _MINUTES_PER_DAY:
                    # Ran off the end of the day without finding a gap.
                    schedule.skipped.append(task)
                    break
                # End times of any placed tasks that overlap this spot.
                blockers = [
                    t_end for t_start, t_end in taken if start < t_end and t_start < end
                ]
                if not blockers:
                    place(task, start)
                    break
                # Move past the latest blocker and check that spot next.
                start = max(blockers)

        # Step 5: tasks were placed in priority order, so put them back in
        # time order before returning. The caller decides whether to save
        # the schedule with owner.set_schedule().
        schedule.scheduled.sort(key=lambda item: item.start_time)
        return schedule

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks sorted by priority, highest first (shorter wins ties)."""
        # CHANGE (behavior note): ties in priority break by shorter duration
        # first, so more tasks fit in the available time.
        # Highest priority first (negative value sorts descending); on a tie
        # the shorter task comes first. sorted() returns a new list and
        # leaves the caller's list unchanged.
        return sorted(tasks, key=lambda t: (-t.priority_value(), t.duration_minutes))
