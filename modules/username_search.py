import json 
import re 
import subprocess 

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
    }


if __name__ == "__main__":
    # Change the name below to a username you know exists.
    print(json.dumps(search_sherlock("elenamarlowe"), indent=2))