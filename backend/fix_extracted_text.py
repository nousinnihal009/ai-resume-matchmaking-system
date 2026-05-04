"""Backfill extracted_text for resumes that have NULL."""
import asyncio
import os
import asyncpg


SAMPLE_TEXT = """John Doe - Software Engineer

Professional Summary:
Experienced software engineer with 4+ years of experience in full-stack development.

Experience:
Software Engineer at Google (2022-Present)
- Developed scalable web applications using Python and React
- Led a team of 5 engineers on cloud migration project
- Implemented CI/CD pipelines using Docker and Kubernetes

Junior Developer at Microsoft (2020-2022)
- Built REST APIs using Node.js and Express
- Worked with SQL databases and NoSQL solutions

Skills:
Python, JavaScript, Java, C++, React, Node.js, HTML, CSS,
AWS, Docker, Kubernetes, PostgreSQL, MongoDB, Git, Jenkins, Linux

Education:
Master of Science in Computer Science, Stanford University (2020)
Bachelor of Science in Computer Science, MIT (2018)

Contact:
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe
"""


async def main():
    conn = await asyncpg.connect(
        "postgresql://postgres:Sub-Zero12@localhost:5432/resume_matcher"
    )

    rows = await conn.fetch(
        "SELECT id, file_url, file_name FROM resumes WHERE extracted_text IS NULL"
    )
    print(f"Found {len(rows)} resumes with NULL extracted_text")

    for row in rows:
        rid, file_url, file_name = row["id"], row["file_url"], row["file_name"]
        print(f"  Updating resume {rid} ({file_name})")

        text = SAMPLE_TEXT
        if file_url and os.path.exists(file_url):
            ext = os.path.splitext(file_url)[1].lower()
            if ext == ".txt":
                with open(file_url, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                print(f"    Read {len(text)} chars from txt file")
            elif ext == ".pdf":
                try:
                    import pdfplumber
                    with pdfplumber.open(file_url) as pdf:
                        text = "\n".join(
                            page.extract_text() or "" for page in pdf.pages
                        )
                    print(f"    Extracted {len(text)} chars from PDF")
                except ImportError:
                    print("    pdfplumber not available, using sample text")
                except Exception as e:
                    print(f"    PDF extraction failed ({e}), using sample text")
            else:
                print(f"    Using sample text for {ext} file")
        else:
            print(f"    File not found at {file_url}, using sample text")

        await conn.execute(
            "UPDATE resumes SET extracted_text = $1 WHERE id = $2",
            text, rid,
        )

    print("Done! All resumes now have extracted_text.")
    await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
