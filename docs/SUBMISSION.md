# Submission links

Copy these into the Unified Mentor form. Every field is an `https://` URL.

| Field | Link |
| --- | --- |
| GitHub Repository | https://github.com/deepesh2804yadav/deepesh0103 |
| Research paper | https://github.com/deepesh2804yadav/deepesh0103/blob/main/docs/research_paper.md |
| Deployed Streamlit app | https://deepesh0103-eyfv25shiquxssrps5v8pf.streamlit.app/ |
| Project feedback video | https://github.com/deepesh2804yadav/deepesh0103/blob/main/docs/project_feedback.mp4 |

Direct file (if the form prefers a raw media URL):  
https://raw.githubusercontent.com/deepesh2804yadav/deepesh0103/main/docs/project_feedback.mp4

The paper is the project research write-up in this repository. It is not a journal publication. If the form insists on Drive, upload `docs/research_paper.md` (or a PDF export of it) and paste that Drive link instead.

## Deployed Streamlit app

Live dashboard: https://deepesh0103-eyfv25shiquxssrps5v8pf.streamlit.app/

Redeploy from [share.streamlit.io](https://share.streamlit.io) if that URL ever expires. Use repository `deepesh2804yadav/deepesh0103`, branch `main`, main file `streamlit_app.py`.

## Project feedback video

The video covers experience and learnings: what was delivered, how a headline churn rate hid Germany vs France, age and engagement patterns, method lessons, challenges, and next steps.

Regenerate with:

```bash
python3 -m pip install edge-tts
python3 scripts/render_feedback_video.py
```
