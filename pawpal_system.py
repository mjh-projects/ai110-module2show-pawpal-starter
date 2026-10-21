"""PawPal+ logic layer: backend classes for owners, pets, tasks and scheduling."""

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str = ""
    frequency: str = "daily"
    pet_name: str = ""
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def priority_value(self) -> int:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def edit_task(self, title: str, task: Task) -> None:
        pass

    def remove_task(self, title: str) -> None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str


@dataclass
class Schedule:
    date: str
    start_time: str
    available_minutes: int
    scheduled: list[ScheduledTask] = field(default_factory=list)
    skipped: list[Task] = field(default_factory=list)

    def total_minutes(self) -> int:
        pass

    def has_conflict(self) -> bool:
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
        pass

    def get_schedule(self, date: str) -> Schedule:
        pass


class Scheduler:
    def generate_plan(
        self, owner: Owner, date: str, start_time: str, available_minutes: int
    ) -> Schedule:
        pass

    def sort_by_priority(self, tasks: list[Task]) -> list[Task]:
        pass
