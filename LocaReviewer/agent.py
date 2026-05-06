# Copyright 2026 Shital Babaso Patil
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Shital Babaso Patil
# Email: shitalbabasopatil@gmail.com
# Website: https://shitalam.in

import os
import subprocess
from datetime import datetime, timezone
import re
import warnings

# Suppress all warnings from the 'authlib' module to silence deprecation messages
warnings.filterwarnings("ignore", module="authlib")

from google.adk.agents.llm_agent import Agent

_COMMIT_ID_REGEX = re.compile(r"^[0-9a-fA-F]{7,40}$")

def _is_valid_commit_hash(commit_id: str) -> bool:
    return bool(_COMMIT_ID_REGEX.fullmatch(commit_id))

def git_diff_tool(repo_path: str, commit_ids: str) -> str:
    """
    Fetches the git diff for given commit IDs in a repository.
    Args:
        repo_path: Path to the repository. '.' or empty string means current working directory.
        commit_ids: A single commit hash or multiple commit hashes separated by spaces.
                    If multiple commit hashes are provided, the tool calculates the diff
                    between the first and the last commit in the list.
    """
    if not repo_path or repo_path == ".":
        repo_path = os.getcwd()
    
    if not commit_ids:
        cmd = ["git", "log", "-1", "-p"]
    else:
        commits = commit_ids.split()
        for commit in commits:
            if not _is_valid_commit_hash(commit):
                return f"GitDiffError: Invalid commit ID format '{commit}'"
        
        if len(commits) == 1:
            cmd = ["git", "show", commits[0]]
        else:
            cmd = ["git", "diff", commits[0], commits[-1]]
            
    try:
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        return result.stdout or "No changes found."
    except subprocess.CalledProcessError as e:
        return f"GitDiffError: Error executing git command: {e.stderr}"
    except Exception as e:
        return f"GitDiffError: {e}"

def file_reader_tool(repo_path: str, file_path: str) -> str:
    """
    Reads the content of a single file for code review.
    
    Args:
        repo_path (str): Path to the repository. '.' or empty string means current working directory.
        file_path (str): Path to the file to read, relative to repo_path or absolute.
    """
    if not repo_path or repo_path == ".":
        repo_path = os.getcwd()
        
    full_path = os.path.join(repo_path, file_path) if not os.path.isabs(file_path) else file_path
    
    abs_repo_path = os.path.realpath(repo_path)
    abs_full_path = os.path.realpath(full_path)
    
    # Ensure the requested file is within the repository path
    if not abs_full_path.startswith(abs_repo_path + os.sep) and abs_full_path != abs_repo_path:
        return f"FileReaderError: Attempted path traversal detected for {file_path}"
    
    try:
        with open(abs_full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"FileReaderError: Error reading file: {e} at {abs_full_path}"

def remove_emojis(text: str) -> str:
    """Removes standard emoji characters."""
    # A simple regex to strip out characters typically in emoji ranges
    # This might catch some other unicode symbols but fulfills the "no emojis" strict requirement safely
    return re.sub(r'[\U00010000-\U0010ffff]', '', text)

def file_writer_tool(report_content: str, repo_path: str = "", file_path: str = "") -> str:
    """
    Saves the generated markdown code review report to the correct directory with a UTC timestamp.
    
    Args:
        report_content (str): The full markdown text of the code review report.
        repo_path (str): The repository path (if provided by user).
        file_path (str): The reviewed file path (if provided by user).
    """
    try:
        # Determine target directory
        if repo_path and repo_path != ".":
            target_dir = repo_path
        elif file_path:
            target_dir = os.path.dirname(os.path.abspath(file_path)) or os.getcwd()
        else:
            target_dir = os.getcwd()
            
        # Ensure directory exists
        os.makedirs(target_dir, exist_ok=True)
        
        # Verify writability
        if not os.access(target_dir, os.W_OK):
            return f"FileWriterError: Directory '{target_dir}' is not writable. Please check permissions."
        
        # Generate accurate UTC timestamp filename
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"code_review_report_{timestamp}.md"
        full_path = os.path.join(target_dir, filename)
        
        # Strip emojis as per constraints
        clean_content = remove_emojis(report_content)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass # fsync might fail on some filesystems
        
        abs_final_path = os.path.abspath(full_path)
        return f"Successfully saved report to {abs_final_path}"
    except Exception as e:
        return f"FileWriterError: Error writing file: {str(e)}"

INSTRUCTION = """\
You are LocaReviewer, an Advanced Code Reviewer Agent.
You perform intelligent code reviews using:
- Commit IDs (single or multiple)
- OR a single file
- OR fallback repo scan

# 📥 Inputs you may receive from the user:
- repo_path: "." OR empty → use current working directory
- commit_ids: One OR multiple commit hashes (optional)
- file_path: Optional single file review
- review_mode: strict | moderate | unstrict (default = moderate)

# ⚙️ Input Resolution Logic
1. If repo_path is "." or empty: resolve to current working directory
2. If file_path is provided: review ONLY that file using file_reader_tool(repo_path, file_path)
3. Else if commit_ids provided: fetch and analyze diffs using git_diff_tool
4. Else: fallback to latest changes OR lightweight repo scan using git_diff_tool (pass empty commit_ids)

# 🔍 Review Modes
🔴 STRICT: Detect ALL issues, include negative points, provide fixes + suggestions, include code snippets if needed.
🟡 MODERATE (DEFAULT): Validate correctness, no harsh/negative phrasing, minimal suggestions (only critical), acceptable changes justified.
🟢 UNSTRICT: Concise, assume correctness unless major issue, focus on approval reasoning.

# 🧪 Review Dimensions
Evaluate across: Correctness, Performance, Security, Code Quality, Design & Architecture, Standards Compliance.
Follow clean code principles, Python best practices.

# ⚙️ ADK Tool Usage Pattern
You MUST prefer tools over assumptions.
Available tools:
- git_diff_tool(repo_path, commit_ids)
- file_reader_tool(repo_path, file_path)
- file_writer_tool(report_content, repo_path, file_path)

Behavior: Use tools appropriately. Do NOT hallucinate file contents.
Ensure your tool calls are valid JSON. Pass the full markdown string into `report_content`.

# 🧠 Processing Steps
1. Resolve inputs
2. Fetch data (diff/file)
3. Understand context (not just diff)
4. Apply review_mode filtering
5. Generate structured report
6. Persist report as `.md`

# 📤 Output Format (STRICT MARKDOWN)
# 🧾 Code Review Report
## 📌 Summary
- What was reviewed
- Review Mode: <mode>
- Risk Level: LOW / MEDIUM / HIGH
---
## 🔍 Findings
### 🔴 Critical Issues (only if present or strict mode)
### 🟠 Observations / Improvements (mode dependent)
### 🟢 Positives (at least one when possible)
---
## 🧠 Context Understanding
- Intent of changes or file
---
## 📊 Metrics
- Files reviewed
- LOC impact (if commits)
---
## ✅ Final Verdict
- APPROVED / NEEDS CHANGES / ACCEPTABLE
---

# 💾 Report Persistence (MANDATORY AND CRITICAL)
- You MUST execute the `file_writer_tool` function call to physically save the report to disk! DO NOT just output text saying you saved it.
- You must explicitly duplicate the full markdown report into the `report_content` argument of the tool call. Do not skip this step just because you already printed it in the chat.
- Pass the `repo_path` and/or `file_path`. The tool automatically handles the target folder and timestamp.
- Your final output MUST trigger the execution of `file_writer_tool`.

# 🔁 Execution Behavior
- Once the report is generated, your goal is to BOTH display it to the user and persist it.
- 1. Output the full markdown report in the chat so the user can see it in the Web UI.
- 2. IMMEDIATELY follow up by calling `file_writer_tool` with the exact same content to save it to disk.
- This ensures the user sees the results immediately and has a permanent record.
"""

def create_agent(model_name: str = 'gemini-3.1-flash-lite-preview'):
    """Creates the LocaReviewer agent with the specified model."""
    try:
        return Agent(
            model=model_name,
            name='LocaReviewer',
            description='Advanced Code Reviewer Agent',
            instruction=INSTRUCTION,
            tools=[git_diff_tool, file_reader_tool, file_writer_tool]
        )
    except Exception as e:
        # Fallback to a more standard model if the requested one is unavailable
        print(f"Warning: Model '{model_name}' initialization failed: {e}. Falling back to 'gemini-1.5-flash'.")
        return Agent(
            model='gemini-2.5-flash',
            name='LocaReviewer',
            description='Advanced Code Reviewer Agent (Fallback Mode)',
            instruction=INSTRUCTION,
            tools=[git_diff_tool, file_reader_tool, file_writer_tool]
        )

# Initialize the root agent
root_agent = create_agent()
