from datetime import date, time

import streamlit as st

# Bring in the backend classes from the logic layer so the UI can build an
# owner, pets and tasks, and ask the Scheduler to generate the daily plan.
from pawpal_system import Owner, Pet, Priority, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Streamlit re-runs this whole file on every click, so the Owner is created
# only once and kept in st.session_state. Without this check, every click
# would build a new, empty Owner and the pets and tasks would disappear.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "Smith")

# From here on, `owner` is the same object on every re-run.
owner = st.session_state.owner

st.subheader("Owner")
# These boxes show the owner's current name and write edits straight back to
# the Owner object.
col_first, col_last = st.columns(2)
with col_first:
    owner.first_name = st.text_input("First name", value=owner.first_name)
with col_last:
    owner.last_name = st.text_input("Last name", value=owner.last_name)

# Start over: throw away the current Owner (and every pet, task and schedule
# on it) and begin again with a fresh one. An object can't delete itself, so
# the new Owner simply replaces the old one in session state.
if st.button("Start over"):
    st.session_state.owner = Owner("Jordan", "Smith")
    # Also forget any edit that was in progress for the old owner's data.
    st.session_state.editing_task = None
    st.session_state.editing_pet = None
    st.rerun()

st.subheader("Add a Pet")
col_pet, col_species = st.columns(2)
with col_pet:
    pet_name = st.text_input("Pet name", value="Mochi")
with col_species:
    species = st.selectbox("Species", ["dog", "cat", "other"])

# Adding a pet: create a Pet and hand it to Owner.add_pet().
if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species))

if owner.pets:
    st.write("Pets:")
    # One row per pet, each with its own Edit and Remove buttons. The button
    # keys include the pet id so every button is unique.
    for pet in owner.pets:
        # Same widths as the task rows so the buttons show their full labels.
        col_pet_info, col_pet_edit, col_pet_remove = st.columns([4, 1.2, 1.4])
        col_pet_info.write(
            f"**{pet.name}** ({pet.species}, age {pet.age}): {len(pet.tasks)} tasks"
        )
        if col_pet_edit.button("Edit", key=f"edit_pet_{pet.pet_id}"):
            # Remember which pet is being edited, then re-run so the edit
            # form below appears.
            st.session_state.editing_pet = pet.pet_id
            st.rerun()
        if col_pet_remove.button("Remove", key=f"remove_pet_{pet.pet_id}"):
            # Owner.remove_pet() deletes the pet and, with it, its tasks.
            owner.remove_pet(pet.pet_id)
            if st.session_state.get("editing_pet") == pet.pet_id:
                st.session_state.editing_pet = None
            st.rerun()
else:
    st.info("No pets yet. Add one above.")

# Edit-pet form: shown only while a pet is selected for editing.
editing_pet_id = st.session_state.get("editing_pet")
editing_pet = next((p for p in owner.pets if p.pet_id == editing_pet_id), None)
if editing_pet is not None:
    st.markdown("#### Edit pet")
    # Keys include the pet id so the boxes start from this pet's values.
    pkey = editing_pet.pet_id
    new_pet_name = st.text_input("Pet name", value=editing_pet.name, key=f"pname_{pkey}")
    col_sp, col_age = st.columns(2)
    with col_sp:
        species_options = ["dog", "cat", "other"]
        # If a pet's species isn't in the list, fall back to "other".
        sp_index = (
            species_options.index(editing_pet.species)
            if editing_pet.species in species_options
            else 2
        )
        new_species = st.selectbox(
            "Species", species_options, index=sp_index, key=f"pspecies_{pkey}"
        )
    with col_age:
        new_age = st.number_input(
            "Age", min_value=0, max_value=40, value=editing_pet.age, key=f"page_{pkey}"
        )
    col_pet_save, col_pet_cancel = st.columns(2)
    if col_pet_save.button("Save pet"):
        # Owner.edit_pet() updates the pet in place, so its tasks are kept.
        owner.edit_pet(editing_pet.pet_id, new_pet_name, new_species, int(new_age))
        st.session_state.editing_pet = None
        st.rerun()
    if col_pet_cancel.button("Cancel", key="cancel_pet"):
        st.session_state.editing_pet = None
        st.rerun()

st.markdown("### Tasks")
st.caption("Pick a pet, then add a task for it.")

if owner.pets:
    # Tasks belong to a pet, so the user chooses which pet this task is for.
    # Index positions are used because two pets could share a name.
    pet_index = st.selectbox(
        "Pet",
        range(len(owner.pets)),
        format_func=lambda i: owner.pets[i].name,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    # Extra Task options: how often it repeats, and an optional fixed time.
    col4, col5 = st.columns(2)
    with col4:
        frequency = st.selectbox("Repeats", ["daily", "weekly"])
    with col5:
        pin = st.checkbox("Pin to a specific time")
        pinned_time = st.time_input("Preferred time", value=time(8, 0), disabled=not pin)

    # Scheduling a task: build a Task and hand it to Pet.add_task(), which
    # links the task to that pet. The text choice becomes a Priority enum.
    if st.button("Add task"):
        owner.pets[pet_index].add_task(
            Task(
                task_title,
                int(duration),
                Priority[priority.upper()],
                frequency=frequency,
                preferred_time=pinned_time if pin else None,
            )
        )
else:
    st.info("Add a pet first, then you can add tasks for it.")

# Owner.get_all_tasks() gathers the tasks from every pet.
pet_names = {pet.pet_id: pet.name for pet in owner.pets}
# Each task knows its pet by id, so this lets us find the pet that owns it.
pets_by_id = {pet.pet_id: pet for pet in owner.pets}
all_tasks = owner.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    # One row per task, each with its own Edit and Remove buttons. The button
    # keys include the task id so every button is unique.
    for task in all_tasks:
        # The button columns are wide enough to show "Edit" and "Remove" in
        # full; narrower columns cut the label down to "...".
        col_info, col_edit, col_remove = st.columns([4, 1.2, 1.4])
        pinned_text = f", at {task.preferred_time:%H:%M}" if task.preferred_time else ""
        col_info.write(
            f"**{task.title}** for {pet_names.get(task.pet_id, '')}: "
            f"{task.duration_minutes} min, {task.priority.name.lower()}, "
            f"{task.frequency}{pinned_text}"
        )
        if col_edit.button("Edit", key=f"edit_{task.task_id}"):
            # Remember which task is being edited, then re-run so the edit
            # form below appears.
            st.session_state.editing_task = task.task_id
            st.rerun()
        if col_remove.button("Remove", key=f"remove_{task.task_id}"):
            # Pet.remove_task() deletes it by id. Re-run to refresh the list.
            pets_by_id[task.pet_id].remove_task(task.task_id)
            if st.session_state.get("editing_task") == task.task_id:
                st.session_state.editing_task = None
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

# Edit form: shown only while a task is selected for editing.
editing_id = st.session_state.get("editing_task")
editing = next((t for t in all_tasks if t.task_id == editing_id), None)
if editing is not None:
    st.markdown("#### Edit task")
    # Keys include the task id so the boxes start from this task's values
    # instead of keeping what was typed for a different task.
    key = editing.task_id
    new_title = st.text_input("Title", value=editing.title, key=f"title_{key}")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        new_duration = st.number_input(
            "Minutes", min_value=1, max_value=240,
            value=editing.duration_minutes, key=f"dur_{key}",
        )
    with col_b:
        levels = ["low", "medium", "high"]
        new_priority = st.selectbox(
            "Priority", levels,
            index=levels.index(editing.priority.name.lower()), key=f"pri_{key}",
        )
    with col_c:
        freqs = ["daily", "weekly"]
        new_frequency = st.selectbox(
            "Repeats", freqs,
            index=freqs.index(editing.frequency), key=f"freq_{key}",
        )
    new_pin = st.checkbox(
        "Pin to a specific time",
        value=editing.preferred_time is not None, key=f"pin_{key}",
    )
    new_time = st.time_input(
        "Preferred time",
        value=editing.preferred_time or time(8, 0),
        disabled=not new_pin, key=f"time_{key}",
    )
    col_save, col_cancel = st.columns(2)
    if col_save.button("Save changes"):
        # Pet.edit_task() swaps in the new Task and keeps the old task id.
        # last_completed and days_of_week are carried over so editing a task
        # doesn't forget when it was last done.
        pets_by_id[editing.pet_id].edit_task(
            editing.task_id,
            Task(
                new_title,
                int(new_duration),
                Priority[new_priority.upper()],
                frequency=new_frequency,
                days_of_week=editing.days_of_week,
                preferred_time=new_time if new_pin else None,
                last_completed=editing.last_completed,
            ),
        )
        st.session_state.editing_task = None
        st.rerun()
    if col_cancel.button("Cancel"):
        st.session_state.editing_task = None
        st.rerun()

st.divider()

st.subheader("Build Schedule")
st.caption("Choose when the day starts and how many minutes of care you have.")

col_start, col_minutes = st.columns(2)
with col_start:
    start_time = st.time_input("Day starts at", value=time(7, 0))
with col_minutes:
    available_minutes = st.number_input(
        "Available minutes", min_value=1, max_value=1440, value=90
    )

if st.button("Generate schedule"):
    # Scheduler builds the plan; Owner.set_schedule() keeps it (one per day).
    plan = Scheduler().generate_plan(
        owner, date.today(), start_time, int(available_minutes)
    )
    owner.set_schedule(plan)

# Read the saved schedule back from the owner, so it stays on screen after
# other clicks re-run the page.
schedule = owner.get_schedule(date.today())
if schedule is not None:
    st.success(
        f"Plan for {schedule.date.isoformat()}: "
        f"{schedule.total_minutes()} of {schedule.available_minutes} minutes used."
    )
    if schedule.scheduled:
        # One row per scheduled item, with Done and Skip buttons that update
        # that item's status.
        for item in schedule.scheduled:
            # Wide enough for the "Done" and "Skip" labels to show in full.
            col_time, col_task, col_status, col_done, col_skip = st.columns(
                [2, 4, 1.5, 1.2, 1.2]
            )
            col_time.write(f"{item.start_time:%H:%M}-{item.end_time:%H:%M}")
            col_task.write(
                f"**{item.title}** for {pet_names.get(item.task.pet_id, '')} "
                f"({item.duration_minutes} min)"
            )
            col_status.write(item.status.value)
            if col_done.button("Done", key=f"done_{item.task.task_id}"):
                # ScheduledTask.mark_done() sets the status and records the
                # date on the Task, so recurring tasks come due again later.
                item.mark_done(date.today())
                st.rerun()
            if col_skip.button("Skip", key=f"skip_{item.task.task_id}"):
                # ScheduledTask.mark_skipped() only changes the status.
                item.mark_skipped()
                st.rerun()
    else:
        st.info("Nothing could be scheduled.")
    if schedule.skipped:
        st.warning(
            "Skipped (did not fit): "
            + ", ".join(task.title for task in schedule.skipped)
        )
    # Schedule.explain() gives the full text version with the reasons.
    with st.expander("Why this plan?"):
        st.text(schedule.explain())
