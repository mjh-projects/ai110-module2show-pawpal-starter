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
    HIGH = 3
    MEDIUM = 2
    LOW = 1


# CHANGE: helper so every Task/Pet gets a unique id. Titles and names are not
# guaranteed unique, so lookups and links by title/name were ambiguous.
def _new_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Task:
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
        # CHANGE: takes the date so last_completed can be recorded.
        pass

    def is_due(self, on: date) -> bool:
        # CHANGE: new method. Combines frequency, days_of_week and
        # last_completed so the scheduler can ask "should this task be on the
        # plan for this date?" in one place.
        pass

    def priority_value(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    # CHANGE: pets get an id too, so Task.pet_id has something to point at.
    pet_id: str = field(default_factory=_new_id)
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        # CHANGE (behavior note): must set task.pet_id = self.pet_id.
        pass

    # CHANGE: edit/remove take task_id instead of title (titles may repeat).
    def edit_task(self, task_id: str, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    # CHANGE: str -> datetime.time. Adding durations and comparing times is
    # error-prone on strings like "8:30" vs "08:30".
    start_time: time
    end_time: time
    # CHANGE: completion for *this day* lives here, not on the shared Task,
    # so checking off today's walk doesn't mark every future walk done.
    completed: bool = False


@dataclass
class Schedule:
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
        pass

    def has_conflict(self) -> bool:
        # CHANGE (behavior note): now meaningful because Task.preferred_time
        # can pin tasks to overlapping slots. Sort by start time, then compare
        # neighbours (O(n log n)) rather than every pair (O(n^2)).
        pass

    def explain(self) -> str:
        pass


@dataclass
class Owner:
    first_name: str
    last_name: str
    pets: list[Pet] = field(default_factory=list)
    schedules: list[Schedule] = field(default_factory=list)

    def full_name(self) -> str:
        pass

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass

    def set_schedule(self, schedule: Schedule) -> None:
        # CHANGE (behavior note): replaces any existing schedule for
        # schedule.date (one per day) and sets schedule.owner = self.
        pass

    # CHANGE: date: str -> date, and the return type is now `Schedule | None`
    # because there may be no schedule for that day yet.
    def get_schedule(self, on: date) -> Schedule | None:
        pass


class Scheduler:
    # CHANGE: date/start_time use real date/time types (see Schedule).
    def generate_plan(
        self, owner: Owner, on: date, start_time: time, available_minutes: int
    ) -> Schedule:
        # CHANGE (behavior note): only include tasks where task.is_due(on).
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        # CHANGE (behavior note): ties in priority break by shorter duration
        # first, so more tasks fit in the available time.
        pass
