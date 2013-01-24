gts
===

## What is GTS
Galah Testing Suite (GTS) is an automated marking, feedback and grading
suite.  It is designed to best work within Galah, a web based automated
testing and feedback framework but is not tied exclusively to the Galah
system.  Work on Galah can be found at: https://github.com/brownhead/galah

# History
The Galah Testing Suite (GTS) has a mutli-step past that started out as
simply a way to eliminate hand grading of programming assignments.

### Initial Premise
The initial design of the testing suite was developed entirely as an
automated testing and marking generation framework for CS 10 (Introduction
to Computer Science) at University of California, Riverside. These sripts
were written in an amalgamation of bash and C++ and as they were developed
immediately prior to their use, they became quickly bloated due to the lack
of design priciples beyond: it must work and must be done before the
assignment is due.

### Widening the net
The initial implementation was sound enough to be utilized for a few
quarters.  However, expanding on the implemenation for additional
assignments was impractical. Additionally, utilizing the suite in courses
beyond the very first programming course was impossible.

With these faults in mind.  A more clear design strategy was created to
generalize many pieces utilized in the initial implementation into modules.
These modules optionally combined with more specific assignment oriented
tests would create a test harness to be utilized for a single assignment.
Additionally, a uniform CSV output format was chosen so that outpt is
easily parsed for other purposes.

## Project Goals
The Galah Testing Suite has several project goals.  A few deserving more
length descriptions are listed below.

### Assignment Independece
A primary goal of the project is that each assignment test harness must be
independent of all other test harnesses. This means that there will
certainly be reproduced code when looking through multiple harnesses at
once but allows the replacement or swapping of assignments without any
concern for breaking assignments that are not being moved or modified.

### Easy Generation of Simple Harness
A simple test harness should easily be generated or created based on
generic modules. Some scripting knowledge will be required but the goal is
to have a basic test harness be a short non-confounding task.






