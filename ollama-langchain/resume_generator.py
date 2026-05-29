import os
from datetime import datetime
import requests

# --- Set your model names (must match `ollama list`) ---
LOCAL_MODEL = "qwen3:0.6b"   # 0.5B or 1B class only, e.g. qwen2.5:0.5b
CLOUD_MODEL = "gpt-oss:120b-cloud"  # your Ollama Cloud tag; set export OLLAMA_API_KEY first
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")

CANDIDATE = {
    "name": "Aarav Mehta",
    "email": "aarav.mehta@example.com",
    "phone": "+91-98765-43210",
    "location": "Roorkee, Uttarakhand",
    "education": "B.Tech Computer Science, IIT Roorkee (expected 2026), CGPA 8.4",
    "skills": ["Python", "REST APIs", "SQL", "Git", "Basic ML"],
    "experience": "Summer intern at TechBridge Labs (Jun–Aug 2025): built internal dashboards with FastAPI and PostgreSQL.",
    "projects": "Hostel Room Booking CLI (Python) — 200+ active users on campus.",
}

RESUME_PROMPT = f"""You are a professional resume writer. Create a complete, single-page resume in valid HTML only.

Rules:
- Return ONLY HTML starting with <!DOCTYPE html> — no markdown fences, no explanation before or after.
- Do not invent employers, degrees, or facts not listed below.

Layout (required):
- Use a **two-column** layout for the main body (e.g. CSS flexbox or CSS grid with two columns).
- **Left column (narrower, ~30–35%):** contact block, Skills, Education.
- **Right column (wider, ~65–70%):** Experience, Projects.
- **Full-width header** above the columns: candidate name (large), one-line title or tagline, email / phone / location on one line.

Styling (use a <style> block in <head> — make it look polished):
- Font: a clean sans-serif stack (e.g. Arial, Helvetica, or system-ui).
- **Accent color:** one professional color (e.g. #2563eb blue or #0f766e teal) for headings, section titles, and subtle borders.
- Section headings: uppercase or small-caps, accent color, bottom border or left border.
- Consistent spacing: padding inside columns, margin between sections, readable line-height (1.4–1.6).
- Skills: show as a neat list or small pill/tag style — not a plain comma-separated paragraph.
- Page: max-width ~900px, centered on screen; light background (#f8fafc) with white column areas or a white card look.
- Print-friendly: avoid horizontal scroll; keep everything on one screen-height page if possible.

Candidate data:
Name: {CANDIDATE['name']}
Email: {CANDIDATE['email']}
Phone: {CANDIDATE['phone']}
Location: {CANDIDATE['location']}
Education: {CANDIDATE['education']}
Skills: {', '.join(CANDIDATE['skills'])}
Experience: {CANDIDATE['experience']}
Projects: {CANDIDATE['projects']}
"""


def save_resume_html(html_text: str, mode: str) -> str:
    """
    Save model output to an HTML file. USE THIS FUNCTION AS-IS — do not change the logic.

    File name pattern:
      Local  -> Local_Resume_YYYYMMDD_HHMMSS.html
      Cloud  -> Cloud_Resume_YYYYMMDD_HHMMSS.html
    """
    prefix = "Local" if mode == "local" else "Cloud"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_Resume_{stamp}.html"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_text)

    print(f"Saved {filename}")
    return filename


def ask_ollama(mode: str, prompt_text: str) -> str:
    """
    TODO (you implement):
    - mode "local": POST http://localhost:11434/api/chat, model LOCAL_MODEL, no API key
    - mode "cloud": POST https://ollama.com/api/chat, model CLOUD_MODEL,
      header Authorization: Bearer <OLLAMA_API_KEY from os.environ>
      if key missing, raise ValueError with a clear message
    - JSON body: model, messages=[{{"role":"user","content": prompt_text}}], stream=False
    - timeout=120
    - return response.json()["message"]["content"]
    """
    # YOUR CODE HERE
    if mode == "local":
        API_PATH = "http://localhost:11434/api/chat"
        payload = {
            "model": LOCAL_MODEL,
            "messages":[
                {
                    "role": "user",
                    "content": RESUME_PROMPT
                }
            ],
            "stream" : False
        }
        local_response = requests.post(
            API_PATH,
            json = payload,
            timeout = 120
        )
        return local_response.json()["message"]["content"]
    elif mode == "cloud":
        if not OLLAMA_API_KEY:
            raise ValueError("API key not found. Please set the OLLAMA_API_KEY environment variable.")
        API_CLOUD_PATH = "https://ollama.com/api/chat"
        header = {
            "Authorization": f"Bearer {OLLAMA_API_KEY}"
        }
        payload = {
            "model" : CLOUD_MODEL,
            "messages":[{
                "role": "user",
                "content": RESUME_PROMPT
            }],
            "stream" : False
        }
        cloud_response = requests.post(
            API_CLOUD_PATH,
            json = payload,
            headers = header,
            timeout = 120
        )
        return cloud_response.json()['message']['content']


def generate_resume_html(mode: str) -> str:
    """Call Ollama, then save HTML using save_resume_html (do not change this function)."""
    html_from_model = ask_ollama(mode, RESUME_PROMPT)
    return save_resume_html(html_from_model, mode)


if __name__ == "__main__":
    print("Generating local resume...")
    generate_resume_html("local")

    print("Generating cloud resume...")
    try:
        generate_resume_html("cloud")
    except ValueError as e:
        print(f"Cloud skipped: {e}")

    print("Open both HTML files in your browser and compare quality.")

# TODO after comparing both files in the browser — replace the lines below (2 lines; mention styling):
# Local resume quality: Local Resume Quality was not so good having some styling issues and not following the layout instructions properly. The sections were not clearly defined and the overall look was quite cluttered.
# Cloud resume quality: Cloud Resume Quality was significantly better than the local one. It followed the two-column layout instructions accurately, with a clear distinction between the left and right columns. The styling was polished, using a clean font and a professional accent color for headings. The skills were presented in a neat list format, and the overall spacing and readability were excellent, making it look like a professionally designed resume.
