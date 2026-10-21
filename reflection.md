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
preferred time, due date , time budget, no overlaps, End of day
- How did you decide which constraints mattered most?
Due date comes first. A task that isn't due never gets to compete for anything else.
Preferred time is placed before priority. Pinned tasks are handled in a first pass, and flexible tasks only get what's left. So a low-priority task with a preferred time can use up budget before a high-priority task with no preferred time.
The time budget is a hard limit. Whoever is placed first gets the minutes, and later tasks are skipped once it runs out.
Priority decides the order within each group. It ranks the pinned tasks among themselves and the flexible tasks among themselves, but it doesn't rank across the two groups.
The no-overlap rule always holds. It can cause a skip but never gets relaxed 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The main tradeoff is that the scheduler is greedy. It places tasks one at a time and never reconsiders, so it can miss a better fit


- Why is that tradeoff reasonable for this scenario? The logic is short, fast and predictable.

It's easy to test.



---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project I used it through out the project to brainstorm as well as explain what was going on and what exactly each line of code was doing. 

- What kinds of prompts or questions were most helpful?
It was helpful to ask the AI to explain what it was doing and to also not go ahead of what I was asking as it seemed to want to jump ahead in tasks before I asked it do something. 
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

THe initial design and UML seemed convoluted so I had it change the UML design to something that fit my idea better. 

- How did you evaluate or verify what the AI suggested?

I went through the diagrams and the coding to make sure it was what I wanted. 
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Task completion
task addition
I also did a walk through seeing it added pets and tasks to the schedule

- Why were these tests important?
It is the basic function of the app
**b. Confidence**

- How confident are you that your scheduler works correctly?
I am pretty confident that it will work although I Have not gone through all cases. I am pretty sure there.
- What edge cases would you test next if you had more time?
I would want to test overlaps of schedules as well as see what happens if pets have the same name.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I did like that it could produce a basic schedule.
 
**b. What you would improve**

- If you had another iteration, what would you improve or redesign? I think the priority in the scheduling needs more work this was an initial first design but it defnitely needs more work to make sure that priorities are handled better.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project? That the AI seemed to want to rush ahead even when given instructions it would seem to want to predit what I wanted next even though it was not what I was asking for. I had to give it commands to stop and follow my instructions and not dive ahead before I was ready. 
