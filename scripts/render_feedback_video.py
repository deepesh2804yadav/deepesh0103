#!/usr/bin/env python3
"""Render a project-feedback slideshow video with narration."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = Path("/tmp/feedback-video")
REPO_VIDEO = Path("/workspace/docs/project_feedback.mp4")
VOICE = "en-IN-PrabhatNeural"

SLIDES = [
    {
        "file": "01.png",
        "title": "Project Feedback",
        "kicker": "Unified Mentor · European Banking Analytics",
        "points": [
            "Customer Segmentation and Churn Pattern Analytics",
            "Experience, methods, and what I would do next",
            "Deepesh Yadav",
        ],
        "narration": (
            "Hello. This is my project feedback for Customer Segmentation and Churn Pattern "
            "Analytics in European Banking, completed for Unified Mentor. In this video I will "
            "explain what I built, how the work felt in practice, and the main things I learned."
        ),
    },
    {
        "file": "02.png",
        "title": "What I delivered",
        "kicker": "End-to-end analytics, not a generic churn rate",
        "points": [
            "Validated 10,000-customer extract for France, Spain, and Germany",
            "Segmentation by geography, age, credit, tenure, and balance",
            "Research paper, executive summary, and a live Streamlit dashboard",
        ],
        "narration": (
            "I started from a customer-level bank extract of ten thousand unique customers. "
            "I validated identifiers, binary flags, and the churn label, then designed segments "
            "for country, age, credit score, tenure, and account balance. The deliverables are a "
            "research paper, a government-facing executive summary, and an interactive Streamlit app."
        ),
    },
    {
        "file": "03.png",
        "title": "My experience on the project",
        "kicker": "From a headline rate to a retention map",
        "points": [
            "The 20.4 percent overall churn rate hid the real story",
            "Germany was an intensity problem; France was a volume problem",
            "High-balance customers were not the safe group I first assumed",
        ],
        "narration": (
            "My biggest shift in experience was realising that a single churn percentage is not a "
            "strategy. Twenty point four percent of customers had exited, but Germany churned at "
            "thirty-two percent, about one point five nine times the book average, while France "
            "still produced a similar count of exits because it is half the book. I also expected "
            "low-balance accounts to dominate churn. Instead, high-balance customers generated "
            "about sixty percent of exits, so revenue risk sat in premium relationships."
        ),
    },
    {
        "file": "04.png",
        "title": "What I learned from the data",
        "kicker": "Age, engagement, and product holding matter most",
        "points": [
            "Ages 46 to 60 churned at 51 percent, and 67 percent in Germany",
            "Inactive members churned 1.88 times as often as active members",
            "Two-product customers were sticky; one-product and 3–4 product cells were not",
        ],
        "narration": (
            "The strongest patterns were life-stage, activity, and product holding, not credit score. "
            "Customers aged forty-six to sixty churned at fifty-one percent, and sixty-seven percent "
            "in Germany. Inactive members left almost twice as often as active members. Two-product "
            "relationships were the stability core, at only seven point six percent churn, while "
            "single-product customers produced most exits, and three or four products were rare "
            "and almost fully churned. That last cell taught me not to treat more products as "
            "automatically healthier."
        ),
    },
    {
        "file": "05.png",
        "title": "What I learned as an analyst",
        "kicker": "Method, KPIs, and communication",
        "points": [
            "Validate binary labels and unique IDs before drawing charts",
            "Report both rate and contribution, plus balance at risk",
            "Decision-makers need a short executive story as well as EDA",
        ],
        "narration": (
            "On method, I learned to lock data quality first: unique customer IDs, no missing cells, "
            "and strictly binary churn and activity flags. I also learned to pair a segment churn "
            "rate with its share of all exits, and to quantify balance at risk, not just headcount. "
            "Writing the executive summary forced me to translate those numbers into a map that a "
            "non-technical stakeholder could use: intensity in Germany, volume in France, and "
            "priority cells where probability and balance coincide."
        ),
    },
    {
        "file": "06.png",
        "title": "Challenges I had to solve",
        "kicker": "Making the analysis usable",
        "points": [
            "Designing bands that were interpretable, not just statistically convenient",
            "Keeping Streamlit filters, KPIs, and drill-down on one logic path",
            "Deploying a live dashboard so the work can be reviewed without installing Python",
        ],
        "narration": (
            "The hard parts were design and packaging. Age, credit, tenure, and balance bands had "
            "to be explainable in a meeting, not only in a notebook. The Streamlit app had to reuse "
            "the same segmentation and KPI code as the tests, so filters actually update the cards. "
            "Finally, I deployed the dashboard to Streamlit Community Cloud so a mentor can open "
            "the live analytics without running the project locally."
        ),
    },
    {
        "file": "07.png",
        "title": "If I continued this work",
        "kicker": "From diagnosis toward action",
        "points": [
            "Add a time dimension so churn is a hazard, not only a cross-section label",
            "Build a retention playbook for the Germany, age 46–60, inactive, high-balance cell",
            "Audit three- and four-product exits for suitability versus genuine deepening",
        ],
        "narration": (
            "If I continued, I would move from a snapshot to a panel, so we can see when customers "
            "go inactive before they exit. I would also design a specific save programme for German "
            "customers aged forty-six to sixty who are inactive and high-balance, and I would audit "
            "three- and four-product churn for possible distress or mis-sale rather than celebrating "
            "product count. Those are the practical next steps from this project."
        ),
    },
    {
        "file": "08.png",
        "title": "Thank you",
        "kicker": "Links for review",
        "points": [
            "GitHub: github.com/deepesh2804yadav/deepesh0103",
            "Dashboard: deepesh0103-eyfv25shiquxssrps5v8pf.streamlit.app",
            "I am grateful for the chance to turn a churn extract into a segmentation story",
        ],
        "narration": (
            "Thank you for reviewing this project. The repository, research paper, and live Streamlit "
            "dashboard are linked in the submission. This work taught me that churn management starts "
            "with who is leaving, where they sit in the book, and how much value is at risk. Thank you."
        ),
    },
]


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def write_slide_png(slide: dict, dest: Path) -> None:
    img = Image.new("RGB", (1280, 720), "#0B1F3A")
    draw = ImageDraw.Draw(img)
    for i in range(720):
        mix = i / 720
        r = int(11 + (31 - 11) * mix)
        g = int(31 + (122 - 31) * mix)
        b = int(58 + (140 - 58) * mix)
        draw.line([(0, i), (1280, i)], fill=(r, g, b))
    kicker_font = _font(18, True)
    title_font = _font(44, True)
    body_font = _font(26)
    footer_font = _font(14)
    draw.text((72, 56), slide["kicker"].upper(), fill="#C4A35A", font=kicker_font)
    draw.text((72, 100), slide["title"], fill="#F8F4EA", font=title_font)
    y = 190
    for point in slide["points"]:
        draw.text((72, y), "▸  " + point, fill="#F8F4EA", font=body_font)
        y += 72
    draw.text(
        (72, 670),
        "Customer Segmentation & Churn Pattern Analytics in European Banking",
        fill="#D6E8E4",
        font=footer_font,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG")


async def synth(text: str, mp3: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
    await communicate.save(str(mp3))


def duration_seconds(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


async def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    concat_lines: list[str] = []
    for i, slide in enumerate(SLIDES, start=1):
        png = OUT_DIR / slide["file"]
        mp3 = OUT_DIR / f"{i:02d}.mp3"
        clip = OUT_DIR / f"{i:02d}.mp4"
        write_slide_png(slide, png)
        await synth(slide["narration"], mp3)
        seconds = duration_seconds(mp3) + 0.6
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-loop",
                "1",
                "-i",
                str(png),
                "-i",
                str(mp3),
                "-c:v",
                "libx264",
                "-tune",
                "stillimage",
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-pix_fmt",
                "yuv420p",
                "-shortest",
                "-t",
                f"{seconds:.3f}",
                "-vf",
                "scale=1280:720",
                str(clip),
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        concat_lines.append(f"file '{clip}'")
        print(f"slide {i}: {seconds:.1f}s")

    list_file = OUT_DIR / "concat.txt"
    list_file.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")
    REPO_VIDEO.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(list_file),
            "-c:v",
            "libx264",
            "-crf",
            "26",
            "-preset",
            "medium",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-movflags",
            "+faststart",
            str(REPO_VIDEO),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    size_mb = REPO_VIDEO.stat().st_size / 1e6
    total = duration_seconds(REPO_VIDEO)
    print(f"wrote {REPO_VIDEO} ({size_mb:.1f} MB, {total:.1f}s)")


if __name__ == "__main__":
    asyncio.run(main())
