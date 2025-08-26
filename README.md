# Corbett's Eisenhower Matrix
This is a quick and dirty python flask app that organizes my tasks.

- find it here: [Eisenhower Matrix](https://eisenhower-matrix-03063f571e97.herokuapp.com/)
- based on this [earlier project](https://corbettbw.github.io/eisenhower-matrix/), hosted on github

## I've automated my executive function
I've got ADHD, and one of the key difficulties I have is knowing when to start tasks, especially if there are a bunch of them. I was motivated to start this project (maybe to procrastinate, what are you, a nark?) when I realized that I had the bad habit of waiting until the day an assignment was due to start it. This is fine when there's only one task, but pretty soon I was struggling to read and write summaries of 4-5 scientific research papers each week. That's where this Eisenhower Matrix will hopefully come in useful.

## How it Works
1. Assignments are exactly what they sound like: projects that have multiple sub-tasks
    - tasks in assignments are given an order and inherit the priority of the assignment.
2. Tasks can be standalone or associated with assignments
3. The sorting algorithm on the back end calculates the task start date by:
    - due date
    - duration
    - priority
    - order number (for tasks in an assignment)
4. If you're starting fresh or returning, you can
    - open: by selecting a saved list from the dropdown, you can load a preexisting list
    - import file or .ics: you can choose to import a JSON file or a calendar file
5. Once you're ready to pause work on your list, or you feel satisfied, you can do the following:
    - save: commits the list to browser storage
    - share link: creates a sharable link that you can use to send to others
    - Export .ics: downloads a calendar file to your computer, allows you to import to any calendar

## What's Next?
To be honest, it's not much of a matrix right now. Originally, Eisenhower would focus on the tasks that were due immediately and were most important, and would delegate the rest. I don't have the luxury of having interns, so this basically turns into a timeline, rather than a graph. I'm going to attempt some beautification in the future, and hopefully get a visual rendering of the tasks. My other project looked like this:

<img width="1682" height="1066" alt="image" src="https://github.com/user-attachments/assets/35e08fc2-fdcf-4963-9a85-fd7bbfa944f0" />

We'll see how it turns out.

## Specs
### Language
Python 3.11.6
### How to deploy
Run `Python app.py`<br>
Deploys locally on the port 5000
### Hosted
Heroku

