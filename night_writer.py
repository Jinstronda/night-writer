import os
import sys
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import time as t
from pathlib import Path
from openai import OpenAI

def read_tasks(path):
    p = Path(path)
    if not p.exists():
        print(f"Tasks file not found at {p.resolve()}")
        sys.exit(1)
    txt = p.read_text(encoding="utf-8").strip()
    if not txt:
        return []
    if txt.lstrip().startswith("["):
        return [str(x) for x in json.loads(txt)]
    return [line.strip() for line in txt.splitlines() if line.strip()]

def next_window_start(tz, start_hh_mm):
    now = datetime.now(tz)
    hh, mm = [int(x) for x in start_hh_mm.split(":")]
    today_start = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if now < today_start:
        return today_start
    return today_start + timedelta(days=1)

def wait_until(ts):
    while True:
        now = datetime.now(ts.tzinfo)
        if now >= ts:
            return
        t.sleep(1.0)

def within_window(start_dt, duration_minutes):
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return datetime.now(start_dt.tzinfo) < end_dt

def save_output(out_dir, idx, prompt, content):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = out_dir / f"task_{idx:03d}_{ts}"
    (base.with_suffix(".prompt.txt")).write_text(prompt, encoding="utf-8")
    (base.with_suffix(".response.txt")).write_text(content, encoding="utf-8")
    return str(base)

def run_session(model, tasks, interval_seconds, tzname, start_time, duration_minutes, out_dir, system_msg):
    tz = ZoneInfo(tzname)
    start_dt = next_window_start(tz, start_time)
    print(f"Next window starts at {start_dt.isoformat()}")
    wait_until(start_dt)
    client = OpenAI()
    idx = 0
    for prompt in tasks:
        if not within_window(start_dt, duration_minutes):
            print("Window ended")
            break
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )
            content = resp.choices[0].message.content
            save_path = save_output(out_dir, idx, prompt, content)
            print(f"Wrote {save_path}")
            idx += 1
        except Exception as e:
            print(f"Error: {e}")
        t.sleep(max(1, int(interval_seconds)))
    print("Session complete")

def prompt_input(prompt_text, default=None, validator=None):
    while True:
        s = input(f"{prompt_text} " + (f"[default {default}]: " if default is not None else ": ")).strip()
        if not s and default is not None:
            s = str(default)
        if validator:
            ok = validator(s)
            if not ok:
                print("Invalid value, try again")
                continue
        return s

def valid_time(s):
    try:
        hh, mm = [int(x) for x in s.split(":")]
        return 0 <= hh < 24 and 0 <= mm < 60
    except:
        return False

def valid_int_pos(s):
    try:
        return int(s) > 0
    except:
        return False

def main():
    print("Night Writer for OpenAI")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Set OPENAI_API_KEY in your environment")
        sys.exit(1)

    model = prompt_input("Model name", default="gpt-5")
    tzname = prompt_input("Timezone", default="America/Sao_Paulo")
    start_time = prompt_input("Window start time HH:MM local", default="04:00", validator=valid_time)
    duration_minutes = int(prompt_input("Window duration minutes", default="60", validator=valid_int_pos))
    interval_seconds = int(prompt_input("Seconds between tasks", default="20", validator=valid_int_pos))
    tasks_path = prompt_input("Path to tasks file", default="tasks.txt")
    out_dir = prompt_input("Output folder", default="night_writer_outputs")
    system_msg = prompt_input("System message", default="You are a senior software engineer. Be concise and safe.")

    tasks = read_tasks(tasks_path)
    if not tasks:
        print("No tasks found")
        sys.exit(1)

    run_session(model, tasks, interval_seconds, tzname, start_time, duration_minutes, out_dir, system_msg)

if __name__ == "__main__":
    main()
