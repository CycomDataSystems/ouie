import os
import json
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
PROMPTS_FILE = Path("prompts.jsonl")
OUT_DIR = Path("results")
OUT_FILE = OUT_DIR / f"{MODEL.replace('/', '_')}.jsonl"

SYSTEM = (
    "You are a helpful assistant. Be concise. "
    "If you do not have enough information to answer, say so explicitly and ask a clarifying question."
)

client = OpenAI()  # reads OPENAI_API_KEY from env


def load_done_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
                if "id" in rec and ("response" in rec or "error" in rec):
                    done.add(rec["id"])
            except json.JSONDecodeError:
                continue
    return done


def call_model(prompt: str, max_retries: int = 5) -> str | None:
    for attempt in range(max_retries):
        try:
            resp = client.responses.create(
                model=MODEL,
                instructions=SYSTEM,
                input=prompt,
                temperature=0,
            )

            # Most SDK versions provide output_text; use it when available
            text = getattr(resp, "output_text", None)
            if text:
                return text.strip()

            # Fallback: extract output text manually
            chunks: list[str] = []
            for item in resp.output:
                # Only keep items that look like messages and have content
                if getattr(item, "type", None) != "message":
                    continue

                content = getattr(item, "content", None)
                if not content:
                    continue  # avoids iterating over None

                for c in content:
                    if getattr(c, "type", None) == "output_text":
                        text_piece = getattr(c, "text", None)
                        if isinstance(text_piece, str):
                            chunks.append(text_piece)

            return "".join(chunks).strip()

        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep((2 ** attempt) + random.random())


def main():
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit(
            "Missing OPENAI_API_KEY. Put it in .env (copy from .env.example).")

    if not PROMPTS_FILE.exists():
        raise SystemExit("Missing prompts.jsonl.")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    done_ids = load_done_ids(OUT_FILE)

    rows = []
    with PROMPTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    with OUT_FILE.open("a", encoding="utf-8") as out:
        for row in tqdm(rows, desc=f"Running {MODEL}"):
            pid = row["id"]
            if pid in done_ids:
                continue

            record = dict(row)
            record["model"] = MODEL
            record["system"] = SYSTEM
            record["ts"] = time.time()

            try:
                record["response"] = call_model(row["prompt"])
            except Exception as e:
                record["error"] = repr(e)

            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            out.flush()

    print(f"Wrote: {OUT_FILE}")


if __name__ == "__main__":
    main()
