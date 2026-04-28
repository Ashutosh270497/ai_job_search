# AI Job Search Autopilot

A local, configurable system that automates the repetitive parts of a job search:

- stores your profile and target roles/companies in JSON,
- generates tailored resume and cover letter drafts per job,
- tracks applications in a CSV pipeline,
- schedules follow-up dates,
- produces a daily action plan.

> Note: no tool can ethically guarantee fully hands-off applications across every site due to CAPTCHAs, account restrictions, and anti-bot rules. This system automates preparation, tracking, and drafting so you only review and click submit.

## Quick start

```bash
python3 job_search_system.py --dir ./job_search_data init
python3 job_search_system.py --dir ./job_search_data plan
python3 job_search_system.py --dir ./job_search_data build --job-id JOB-001
python3 job_search_system.py --dir ./job_search_data apply --job-id JOB-001
python3 job_search_system.py --dir ./job_search_data followups
```

## Data layout

After `init`, you get:

- `profile.json` — your reusable candidate profile
- `jobs.json` — jobs to target
- `templates/resume_template.md` — resume template
- `templates/cover_letter_template.md` — cover letter template
- `applications.csv` — tracking file
- `out/` — generated resume/cover-letter artifacts

## Customize your templates

The templates support these placeholders:

- `{{candidate_name}}`
- `{{email}}`
- `{{phone}}`
- `{{location}}`
- `{{skills}}`
- `{{experience_summary}}`
- `{{highlights}}`
- `{{company}}`
- `{{role_title}}`
- `{{job_url}}`
- `{{job_requirements}}`
- `{{targeted_skill_overlap}}`
- `{{today}}`

## Daily workflow

1. Add/edit job targets in `jobs.json`.
2. Run `plan` to get a ranked daily queue.
3. Run `build` per `job_id` to generate tailored docs.
4. Submit manually and then run `apply` to record status.
5. Run `followups` each day for outreach reminders.

## Why this is practical

“Entire job search” systems fail when they try to auto-click every application portal. This system instead gives you:

- **automation where reliability is high** (drafting, ranking, tracking),
- **human control where risk is high** (final review and submission).

That’s the fastest way to scale applications without getting accounts flagged.
