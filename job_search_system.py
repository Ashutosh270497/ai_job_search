#!/usr/bin/env python3
"""AI Job Search Autopilot.

A lightweight local automation system for job-search operations.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any


DATE_FMT = "%Y-%m-%d"


@dataclass
class Job:
    id: str
    company: str
    role_title: str
    url: str
    requirements: List[str]
    priority: int


def today_iso() -> str:
    return dt.date.today().strftime(DATE_FMT)


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: Any) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def init_workspace(base_dir: Path) -> None:
    ensure_dir(base_dir)
    ensure_dir(base_dir / "templates")
    ensure_dir(base_dir / "out")

    profile_path = base_dir / "profile.json"
    jobs_path = base_dir / "jobs.json"
    resume_tpl_path = base_dir / "templates" / "resume_template.md"
    cover_tpl_path = base_dir / "templates" / "cover_letter_template.md"
    apps_path = base_dir / "applications.csv"

    if not profile_path.exists():
        write_json(
            profile_path,
            {
                "candidate_name": "Your Name",
                "email": "you@example.com",
                "phone": "+1-555-123-4567",
                "location": "City, ST",
                "skills": ["Python", "SQL", "APIs", "Automation"],
                "experience_summary": "Results-driven professional with strong delivery record.",
                "highlights": [
                    "Built automation that reduced manual effort by 60%",
                    "Delivered cross-functional projects from idea to launch",
                ],
            },
        )

    if not jobs_path.exists():
        write_json(
            jobs_path,
            {
                "jobs": [
                    {
                        "id": "JOB-001",
                        "company": "ExampleCorp",
                        "role_title": "Software Engineer",
                        "url": "https://example.com/jobs/1",
                        "requirements": ["Python", "APIs", "Problem solving"],
                        "priority": 5,
                    }
                ]
            },
        )

    if not resume_tpl_path.exists():
        resume_tpl_path.write_text(
            """# {{candidate_name}}

Email: {{email}} | Phone: {{phone}} | Location: {{location}}

## Summary
{{experience_summary}}

## Skills
{{skills}}

## Target Role
{{role_title}} at {{company}}

## Relevant Highlights
{{highlights}}

## Match to Job
{{targeted_skill_overlap}}
""",
            encoding="utf-8",
        )

    if not cover_tpl_path.exists():
        cover_tpl_path.write_text(
            """{{today}}

Hiring Team, {{company}}

I am applying for the {{role_title}} role. My background in {{skills}} aligns with your needs, especially {{targeted_skill_overlap}}.

Relevant context: {{experience_summary}}

I would value the opportunity to contribute. Job posting: {{job_url}}

Best,
{{candidate_name}}
""",
            encoding="utf-8",
        )

    if not apps_path.exists():
        with apps_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "job_id",
                    "company",
                    "role_title",
                    "status",
                    "applied_date",
                    "followup_date",
                    "notes",
                ],
            )
            writer.writeheader()


def load_jobs(base_dir: Path) -> List[Job]:
    raw = read_json(base_dir / "jobs.json")["jobs"]
    return [
        Job(
            id=j["id"],
            company=j["company"],
            role_title=j["role_title"],
            url=j["url"],
            requirements=j.get("requirements", []),
            priority=int(j.get("priority", 1)),
        )
        for j in raw
    ]


def score_job(profile: Dict[str, Any], job: Job) -> int:
    profile_skills = {s.lower() for s in profile.get("skills", [])}
    req = {r.lower() for r in job.requirements}
    overlap = len(profile_skills.intersection(req))
    return job.priority * 10 + overlap * 5


def generate_context(profile: Dict[str, Any], job: Job) -> Dict[str, str]:
    profile_skills = profile.get("skills", [])
    overlap = [r for r in job.requirements if r.lower() in {s.lower() for s in profile_skills}]

    return {
        "candidate_name": profile.get("candidate_name", ""),
        "email": profile.get("email", ""),
        "phone": profile.get("phone", ""),
        "location": profile.get("location", ""),
        "skills": ", ".join(profile_skills),
        "experience_summary": profile.get("experience_summary", ""),
        "highlights": "\n".join(f"- {h}" for h in profile.get("highlights", [])),
        "company": job.company,
        "role_title": job.role_title,
        "job_url": job.url,
        "job_requirements": ", ".join(job.requirements),
        "targeted_skill_overlap": ", ".join(overlap) if overlap else "transferable problem solving",
        "today": today_iso(),
    }


def render_template(template_text: str, context: Dict[str, str]) -> str:
    out = template_text
    for key, value in context.items():
        out = out.replace(f"{{{{{key}}}}}", value)
    return out


def plan_jobs(base_dir: Path) -> None:
    profile = read_json(base_dir / "profile.json")
    jobs = load_jobs(base_dir)
    scored = sorted(
        ((score_job(profile, j), j) for j in jobs),
        key=lambda x: x[0],
        reverse=True,
    )

    print("Daily ranked job queue:")
    for rank, (score, job) in enumerate(scored, start=1):
        print(f"{rank}. {job.id} | {job.company} | {job.role_title} | score={score}")


def build_artifacts(base_dir: Path, job_id: str) -> None:
    profile = read_json(base_dir / "profile.json")
    jobs = {j.id: j for j in load_jobs(base_dir)}
    if job_id not in jobs:
        raise ValueError(f"Unknown job_id: {job_id}")

    job = jobs[job_id]
    ctx = generate_context(profile, job)

    resume_tpl = (base_dir / "templates" / "resume_template.md").read_text(encoding="utf-8")
    cover_tpl = (base_dir / "templates" / "cover_letter_template.md").read_text(encoding="utf-8")

    out_resume = render_template(resume_tpl, ctx)
    out_cover = render_template(cover_tpl, ctx)

    out_dir = base_dir / "out"
    ensure_dir(out_dir)

    resume_path = out_dir / f"{job_id}_resume.md"
    cover_path = out_dir / f"{job_id}_cover_letter.md"
    resume_path.write_text(out_resume, encoding="utf-8")
    cover_path.write_text(out_cover, encoding="utf-8")

    print(f"Built artifacts:\n- {resume_path}\n- {cover_path}")


def record_application(base_dir: Path, job_id: str, notes: str = "") -> None:
    jobs = {j.id: j for j in load_jobs(base_dir)}
    if job_id not in jobs:
        raise ValueError(f"Unknown job_id: {job_id}")

    job = jobs[job_id]
    apps_path = base_dir / "applications.csv"
    applied = dt.date.today()
    followup = applied + dt.timedelta(days=7)

    with apps_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "job_id",
                "company",
                "role_title",
                "status",
                "applied_date",
                "followup_date",
                "notes",
            ],
        )
        writer.writerow(
            {
                "job_id": job.id,
                "company": job.company,
                "role_title": job.role_title,
                "status": "applied",
                "applied_date": applied.strftime(DATE_FMT),
                "followup_date": followup.strftime(DATE_FMT),
                "notes": notes,
            }
        )

    print(f"Application recorded for {job.id}. Follow up on {followup.strftime(DATE_FMT)}")


def show_followups(base_dir: Path) -> None:
    apps_path = base_dir / "applications.csv"
    today = dt.date.today()

    with apps_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    due = []
    for row in rows:
        if not row.get("followup_date"):
            continue
        follow_date = dt.datetime.strptime(row["followup_date"], DATE_FMT).date()
        if follow_date <= today and row.get("status") in {"applied", "interviewing"}:
            due.append(row)

    if not due:
        print("No follow-ups due today.")
        return

    print("Follow-ups due:")
    for row in due:
        print(
            f"- {row['job_id']} | {row['company']} | {row['role_title']} "
            f"(follow-up date: {row['followup_date']})"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AI Job Search Autopilot")
    parser.add_argument("--dir", default="./job_search_data", help="Workspace directory")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Initialize workspace with starter files")
    sub.add_parser("plan", help="Print ranked job queue")

    build_cmd = sub.add_parser("build", help="Build tailored docs for one job")
    build_cmd.add_argument("--job-id", required=True)

    apply_cmd = sub.add_parser("apply", help="Record submitted application")
    apply_cmd.add_argument("--job-id", required=True)
    apply_cmd.add_argument("--notes", default="")

    sub.add_parser("followups", help="List follow-ups due today")

    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(args.dir)

    if args.command == "init":
        init_workspace(base_dir)
        print(f"Initialized job search workspace at {base_dir}")
    elif args.command == "plan":
        plan_jobs(base_dir)
    elif args.command == "build":
        build_artifacts(base_dir, args.job_id)
    elif args.command == "apply":
        record_application(base_dir, args.job_id, args.notes)
    elif args.command == "followups":
        show_followups(base_dir)


if __name__ == "__main__":
    main()
