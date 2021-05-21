import asyncio
import datetime
import sys
import time

import plugins.basetypes
import plugins.configuration
import asyncio
import os
import aiofiles
import re
import time
import yaml
import fnmatch

GIT = "/usr/bin/git"
re_word = re.compile(r"\b([a-z]+)\b")


class ProgTimer:
    """A simple task timer that displays when a sub-task is begun, ends, and the time taken."""

    def __init__(self, title):
        self.title: str = title
        self.time: float = time.time()

    async def __aenter__(self):
        sys.stdout.write("[%s] %s...\n" % (datetime.datetime.now().strftime("%H:%M:%S"), self.title))
        sys.stdout.flush()
        self.start = time.time()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("[%s] Done in %.2f seconds" % (datetime.datetime.now().strftime("%H:%M:%S"), time.time() - self.start))


async def scan_project(server, path):
    """Scans a project repo, looking for potential wording issues"""
    now = time.time()
    all_files = []
    yml = yaml.safe_load(open(os.path.join(path, "_clc.yaml")))
    bad_words = server.config.words
    if "bad_words" in yml:
        bad_words = yml["bad_words"]
    excludes = server.config.excludes
    if "excludes" in yml:
        excludes = yml["excludes"]

    excludes_context = []
    if "excludes_context" in yml:
        excludes_context = yml["excludes_context"]

    scan_history = []
    history_file = os.path.join(path, "_clc_history.yaml")
    if os.path.exists(history_file):
        scan_history = yaml.safe_load(open(history_file))
    server.data.activity = f"Preparing to scan {path}..."
    git_dir = os.path.join(path, ".git")

    params = (
        "-C",
        path,
        "stash",
    )
    proc = await asyncio.create_subprocess_exec(
        GIT, *params, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    params = (
        "-C",
        path,
        "pull",
    )
    proc = await asyncio.create_subprocess_exec(
        GIT, *params, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode == 0:
        for root_path, directories, files in os.walk(path):
            if "/.git" in root_path:
                continue
            all_files.extend([os.path.join(root_path, file) for file in files if "_clc" not in file])
        files_processed = 0
        bytes_processed = 0
        problems_found = 0
        current_issues = []

        # Precompile all bad words
        bad_words_stacked = {}
        bad_words_re = {}
        for word in bad_words:
            bad_words_re[word] = re.compile(r"\b(" + word + r")\b")
            bad_words_stacked[word] = 0

        # How many files and when did we start scanning
        no_files = len(all_files)
        now = time.time()

        # Okay, start the scan!
        for file in sorted(all_files):
            pct = int(files_processed * 100 / no_files)
            duration = int(time.time() - now)
            server.data.activity = f"Scanning {path}. Currently {pct}% done ({files_processed} out of {no_files} files scanned, {duration} seconds spent)"
            if os.path.islink(file):
                continue  # no symlinks, please
            if any(
                fnmatch.fnmatch(file, foo) or fnmatch.fnmatch(file.replace(path, "", 1).lstrip("/"), foo)
                for foo in excludes
            ):
                continue  # don't match excludes
            try:
                async with aiofiles.open(file, encoding="utf-8") as f:
                    line_no = 0
                    async for line in f:
                        line_no += 1
                        bytes_processed += len(line)
                        word_no = 0
                        line_lowercase = line.lower()
                        for bad_word in bad_words:
                            if bad_word in line_lowercase:
                                bad_word_re = bad_words_re[bad_word]
                                word = bad_word_re.search(line_lowercase)
                                if word:
                                    word_no += 1
                                    matched_word = word.group(1)
                                    ctx_start = max(0, word.start(1) - 64)
                                    ctx_end = min(len(line), word.end(1) + 64)
                                    try:
                                        if any(
                                            ctx and re.search(ctx, line, flags=re.IGNORECASE)
                                            for ctx in excludes_context
                                        ):
                                            continue
                                    except SyntaxError:
                                        pass
                                    print(f"Found potential issue in {file} on line {line_no}: {matched_word}")
                                    bad_words_stacked[matched_word] += 1
                                    problems_found += 1
                                    current_issues.append(
                                        {
                                            "path": file,
                                            "line": line_no,
                                            "mark": word_no,
                                            "word": matched_word,
                                            "reason": bad_words[matched_word],
                                            "context": line[ctx_start:ctx_end].strip(),
                                            "resolution": None,
                                        }
                                    )
                    files_processed += 1
            except UnicodeDecodeError:
                pass  # Binary file
            # if files_processed % 100 == 0:
            #     print(f"Processed {files_processed} out of {len(all_files)} files in {path}...")
        taken = time.time() - now
        print(
            f"Processed {path} in {int(taken)} seconds, found {problems_found} potential issues in {files_processed} text files."
        )
        yml["lastrun"] = int(time.time())
        yml["scans"] += 1
        yml["status"] = {
            "files_processed": files_processed,
            "bytes_processed": bytes_processed,
            "issues": problems_found,
            "duration": taken,
            "epoch": int(now),
            "words_stacked": bad_words_stacked,
        }

        scan_history.append(yml["status"])

        # Compile current issues, merging in old ones
        clc_issues = []
        clc_issues_file = os.path.join(path, "_clc_issues.yaml")
        if os.path.exists(clc_issues_file):
            clc_issues = yaml.safe_load(open(clc_issues_file))
        for issue in current_issues:
            for old_issue in clc_issues:
                if old_issue["path"] == issue["path"]:
                    if old_issue["line"] in ("*", issue["line"]) and old_issue["word"] == issue["word"]:
                        issue["resolution"] = old_issue["resolution"]
                        issue["line"] = old_issue["line"]
                        issue["word"] = old_issue["word"]
                        if issue["resolution"] == "ignore":
                            problems_found -= 1

        yaml.dump(yml, open(os.path.join(path, "_clc.yaml"), "w"))
        yaml.dump(current_issues, open(clc_issues_file, "w"))
        yaml.dump(scan_history, open(history_file, "w"))
    else:
        print(f"Could not pull in latest changes for {path}, ignoring for now...")
        print(stderr)
    server.data.activity = "Idling..."


async def run_tasks(server: plugins.basetypes.Server):
    """
        Runs long-lived background data gathering tasks such as gathering repositories, projects and ldap/mfa data.

        Generally runs every 2½ minutes, or whatever is set in tasks/refresh_rate in boxer.yaml
    """

    await asyncio.sleep(3)
    while True:
        #  print("Running background tasks...")
        pqueue = server.data.project_queue[:]
        server.data.project_queue = []
        for item in pqueue:
            url = item["url"]
            branch = item["branch"]
            reponame = url.split("/")[-1]
            destination = os.path.join(server.config.dirs.scratch, reponame)
            params = ("clone", url, destination)
            if branch:
                params = ("clone", "-b", branch, url, destination)
            else:
                branch = "$default"
            print(f"Checking out {url} ({branch}) into {destination}")
            server.data.activity = f"Cloning repository into {destination}..."
            proc = await asyncio.create_subprocess_exec(
                GIT, *params, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                yml = {
                    "source": url,
                    "branch": branch,
                    "excludes": item["excludes"],
                    "bad_words": item["words"],
                    "excludes_context": item["excludes_context"],
                    "checkout": int(time.time()),
                    "lastrun": 0,
                    "scans": 0,
                    "scan_history": [],
                }
                with open(os.path.join(destination, "_clc.yaml"), "w") as f:
                    yaml.dump(yml, f)
                    server.data.projects[reponame] = yml
            print("Done!")
            server.data.activity = "Idling..."

        for repo in sorted(os.listdir(server.config.dirs.scratch)):
            path = os.path.join(server.config.dirs.scratch, repo)
            yml = yaml.safe_load(open(os.path.join(path, "_clc.yaml")))
            server.data.projects[repo] = yml
            if "lastrun" in yml and yml["lastrun"] > time.time() - server.config.tasks.refresh_rate:
                continue
            await scan_project(server, path)
            yml = yaml.safe_load(open(os.path.join(path, "_clc.yaml")))
            server.data.projects[repo] = yml

        await asyncio.sleep(5)
