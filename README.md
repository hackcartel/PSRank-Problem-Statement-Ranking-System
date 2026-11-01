# PSRank
### Problem Statement Ranking System

**An internal HackCartel platform for submitting, analyzing, scoring, and ranking hackathon problem statements.**

---

## About the Project

PSRank is an internal platform being developed for the HackCartel community as part of our internal hackathon.

The platform provides a centralized system where members can submit problem statements (PS), get them analyzed and scored, and view an automatically sorted ranking based on their scores.

The objective is to make problem statement evaluation and comparison simple, structured, and accessible to all members.

## Workflow

```text
              DASHBOARD
                  |
          AUTHENTICATION
           /          \
      ADMIN LOGIN   MEMBER LOGIN
           \          /
                  |
              TEXT INPUT
           (Upload Problem
              Statement)
                  |
               ANALYZER
          (Generate PS Score)
                  |
            SORTING SYSTEM
          (Rank by PS Score)
                  |
           DISPLAY RESULTS
             FOR ALL USERS
```

## Core Features

| Module | Functionality |
|---|---|
| Dashboard | Central interface for the platform |
| Admin Login | Admin authentication and password management |
| Member Login | Member authentication |
| Text Input | Members can submit problem statements |
| Analyzer | Evaluates and generates a score for each PS |
| Sorting System | Automatically sorts problem statements by score |
| Results Display | Makes ranked problem statements visible to all users |

## User Roles

**Admin**
- Access the admin dashboard.
- Change admin password.

**Member**
- Log in to the platform.
- Submit problem statements.
- View ranked problem statements.

**All Users**
- View the final sorted problem statements.

## Project Scope

PSRank will focus strictly on the workflow defined for the HackCartel internal hackathon.

The development will follow a simple, structured approach without unnecessary features or additional modules.

## Development

This project is currently in its initial development and planning phase.

Further implementation details will be documented as development progresses.

## Organization

**Developed by [HackCartel](https://github.com/HackCartel)**

Building practical solutions through collaboration, technology, and innovation.

---

*PSRank — Making problem statement evaluation structured and accessible.*
