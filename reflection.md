# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

1. add a pet and owner profile - allows a user to enter name of their pet and edetails 
2. add or edit a care task create a task with a duration and priority and allows it to be changed or removed
3. generate a schedule - generates a schedule with task in order 

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, I made various changes from the recommendations given in the ai. First it pointing out missing or weak relantionships. 

Task.pet_name is a string, not a link to the Pet. Two pets with the same name, or a renamed pet, would break it. A reference to the Pet object, or an id, is safer.

Tasks are found by title. edit_task and remove_task look tasks up by title, but nothing keeps titles unique. Two "Walk" tasks would make the lookup ambiguous. Give each task an id.

completed lives on Task. A daily task is done today but not tomorrow, so the flag needs to reset or live on ScheduledTask. There's also nothing tracking when a task was last done, so frequency ("daily" or "weekly") has nothing to act on. A weekly task also has no day field, so the scheduler can't tell which days it belongs on.

completed lives on Task. A daily task is done today but not tomorrow, so the flag needs to reset or live on ScheduledTask. There's also nothing tracking when a task was last done, so frequency ("daily" or "weekly") has nothing to act on. A weekly task also has no day field, so the scheduler can't tell which days it belongs on.

date, start_time and end_time are strings. Adding durations and comparing times is much easier with datetime.date and datetime.time, or with minutes since midnight.

THese were the changes made: 
*Priority is now an Enum.
*Tasks and pets have ids, and edits and removals use task_id.
&Task.pet_name became pet_id.
completed became last_completed, with new days_of_week and is_due().
*preferred_time is new, so conflict checking means something.
*Dates and times use real date and time types.
*Schedule links back to its owner, and get_schedule() can return None.
*Added diagrams/uml_v2.mmd to show the revised design. The original uml.mmd is left untouched.


## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
