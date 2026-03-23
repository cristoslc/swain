---
source-id: "wikipedia-cpm"
title: "Critical path method - Wikipedia"
type: web
url: "https://en.wikipedia.org/wiki/Critical_path_method"
fetched: 2026-03-22T00:00:00Z
hash: "9650965a7bf9aec75804b502ee375731351949577e8f4e0fec2db1270fbf1094"
---

# Critical path method - Wikipedia

The **critical path method** (**CPM**), or **critical path analysis** (**CPA**), is an algorithm for scheduling a set of project activities. A critical path is determined by identifying the longest stretch of dependent activities and measuring the time required to complete them from start to finish. It is commonly used in conjunction with the program evaluation and review technique (PERT).

## History

The CPM is a project-modeling technique developed in the late 1950s by Morgan R. Walker of DuPont and James E. Kelley Jr. of Remington Rand. The precursors of what came to be known as critical path were developed and put into practice by DuPont between 1940 and 1943 and contributed to the success of the Manhattan Project.

Critical path analysis is commonly used with all forms of projects, including construction, aerospace and defense, software development, research projects, product development, engineering, and plant maintenance.

## Basic techniques

### Components

The essential technique for using CPM is to construct a model of the project that includes:

1. A list of all activities required to complete the project (typically categorized within a work breakdown structure)
2. The time (duration) that each activity will take to complete
3. The dependencies between the activities
4. Logical end points such as milestones or deliverable items

Using these values, CPM calculates the **longest path** of planned activities to logical end points or to the end of the project, and the earliest and latest that each activity can start and finish without making the project longer. This process determines which activities are "critical" (i.e., on the longest path) and which have "total float" (i.e., can be delayed without making the project longer).

In project management, a critical path is the sequence of project network activities that adds up to the longest overall duration, regardless of whether that longest duration has float or not. This determines the shortest time possible to complete the project.

A project can have several, parallel, near-critical paths, and some or all of the tasks could have free float and/or total float.

### Visualizing critical path schedule

Activity-on-node diagrams show critical path schedule, along with total float and critical path drag computations:

- If a critical path activity has nothing in parallel, its drag is equal to its duration.
- If a critical path activity has another activity in parallel, its drag is equal to whichever is less: its duration or the total float of the parallel activity with the least total float.

These results, including the drag computations, allow managers to prioritize activities for the effective management of project, and to shorten the planned critical path by:
- **Pruning** critical path activities
- **Fast tracking** (performing more activities in parallel)
- **Crashing the critical path** (shortening durations by adding resources)

Critical path drag analysis has also been used to optimize schedules in processes outside of strict project-oriented contexts, such as to increase manufacturing throughput.

### Expansion

Originally, CPM considered only logical dependencies. Since then, it has been expanded to allow for resource-related constraints through **resource leveling** and **resource smoothing**. A related concept is the **critical chain**, which attempts to protect activity and project durations from unforeseen delays due to resource constraints.

Since project schedules change on a regular basis, CPM allows continuous monitoring of the schedule, alerting the project manager to the possibility that non-critical activities may be delayed beyond their total float, creating a new critical path.

### Flexibility

A schedule generated using CPM is often not realized precisely, as estimations are used to calculate times. An important element of project postmortem analysis is the **'as built critical path' (ABCP)**, which analyzes the specific causes and impacts of changes between the planned schedule and eventual schedule as actually implemented.

## Key concepts

- **Critical path**: The longest sequence of dependent activities determining minimum project duration
- **Total float (slack)**: Time an activity can be delayed without affecting project completion
- **Critical path drag**: The amount by which a critical path activity extends project duration
- **Forward pass**: Calculates earliest start/finish times
- **Backward pass**: Calculates latest start/finish times
- **Fast tracking**: Performing sequential activities in parallel
- **Crashing**: Adding resources to shorten critical path activity durations

## See also

- Critical chain project management
- Gantt chart
- Program evaluation and review technique (PERT)
- Work breakdown structure
