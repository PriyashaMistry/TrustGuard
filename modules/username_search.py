# TrustGuard result format (agreed with Amruta)
# {
#   "username": "elenamarlowe",
#   "tool": "sherlock" or "maigret",
#   "results": [
#     {"platform": "GitHub", "status": "found",
#      "url": "https://github.com/elenamarlowe",
#      "low_confidence": false}
#   ]
# }
# Only "found" results are kept (decided with Amruta: <write her answer>).

import json 
import re 
import subprocess 
import tempfile
import os

LOW_CONFIDENCE = {
    "aniworld", "trakt", "fl", "fl.ru", "mastodon.cloud", "babyru",
    "boardgamegeek", "vero", "omg.lol", "chatujme.cz", "salon24.pl",
    "google scholar", "wishlistr", "ourdjtalk", "status cafe",
}

def parse_sherlock(raw_output, username):
    results = []
    for line in (raw_output or "").splitlines():
        m = re.match(r"\[\+\]\s+(.+?):\s+(https?://\S+)", line.strip())
        if not m:
            continue
        platform, url = m.group(1), m.group(2)
        results.append({"platform": platform, "status": "found",
                        "url": url,
                        "low_confidence": platform.lower() in LOW_CONFIDENCE})
    return {"username": username, "tool": "sherlock", "results": results}


def parse_maigret(report_data, username):
    results = []
    if isinstance(report_data, dict):
        for platform, info in report_data.items():
            if not isinstance(info, dict):
                continue
            st = info.get("status")
            if not isinstance(st, dict) or st.get("status") != "Claimed":
                continue
            url = st.get("url") or info.get("url_user")
            if not url:
                continue
            results.append({"platform": platform, "status": "found",
                            "url": url,
                            "low_confidence": platform.lower() in LOW_CONFIDENCE})
    return {"username": username, "tool": "maigret", "results": results}

def search_sherlock(username, timeout=10):
    """Run Sherlock on a username and return the sites where it was found."""
    username = username.lstrip("@").strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,50}", username):
        return {
            "username": username,
            "error": "invalid username",
            "found": [],
            "count": 0,
        }

    try:
        proc = subprocess.run(
            ["sherlock", username, "--print-found", "--timeout", str(timeout)],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {
            "username": username,
            "error": str(e),
            "found": [],
            "count": 0,
        }

    found = []
    for line in proc.stdout.splitlines():
        # Sherlock prints found sites like:  [+] GitHub: https://github.com/x
        m = re.match(r"\[\+\]\s+(.+?):\s+(https?://\S+)", line.strip())
        if m:
            found.append({"site": m.group(1), "url": m.group(2)})

    return {
        "username": username,
        "found": found,
        "count": len(found),
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip(),
        "raw_output": proc.stdout,
    }

def search_maigret(username, timeout=120):
    out_dir = tempfile.mkdtemp()
    cmd = ["maigret", username, "-J", "simple",
           "--folderoutput", out_dir, "--timeout", "10",
           "--dns-resolver", "threaded", "--no-recursion"]
    
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    
    try:
        result = subprocess.run(cmd, capture_output=True,
                        text=True, encoding="utf-8",
                        errors="replace", env=env,
                        timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"tool": "maigret", "error": "timeout", "hits": []}

    hits = []
    report = os.path.join(out_dir, f"report_{username}_simple.json")
    data = {}
    if os.path.exists(report):
        with open(report, encoding="utf-8") as f:
            data = json.load(f)
        for site, info in data.items():
            if info["status"]["status"] == "Claimed":
                hits.append({"site": site, "url": info["status"]["url"]})

    return {"tool": "maigret", "returncode": result.returncode,
            "stderr": result.stderr[-800:],
            "hits": hits,
            "report": data,
            }

if __name__ == "__main__":
        print(json.dumps(search_sherlock("elenamarlowe"), indent=2))
        print(json.dumps(search_maigret("elenamarlowe"), indent=2))