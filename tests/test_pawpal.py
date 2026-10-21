from datetime import date, time

from pawpal_system import Pet, Priority, ScheduledTask, Status, Task



def test_scheduled_task_mark_done():
    # mark_done() should change the scheduled task's status to DONE and
    # record the completion date on the underlying Task.
    task = Task("Morning walk", 30, Priority.HIGH)
    item = ScheduledTask(task, time(8, 0), time(8, 30))
    today = date(2026, 10, 21)
    assert item.status is Status.PENDING

    item.mark_done(today)

    assert item.status is Status.DONE
    assert item.is_done
    assert task.last_completed == today


def test_task_addition():
    # Adding a task to a Pet should increase that pet's task count.
    pet = Pet("Rex", "dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", 10, Priority.HIGH))

    assert len(pet.tasks) == 1


