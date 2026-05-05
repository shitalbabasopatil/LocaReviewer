<div align="center">
  <h1>✨ LocaReviewer ✨</h1>
  <p><strong>Advanced AI-Powered Code Review Agent</strong></p>
  <p>
    <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License"></a>
    <a href="https://shitalam.in"><img src="https://img.shields.io/badge/Author-Shital_Babaso_Patil-brightgreen.svg" alt="Author"></a>
  </p>
</div>

---

> **LocaReviewer** is an intelligent, tool-driven Code Reviewer Agent built on top of the **ADK-Python (Google ADK)** framework. It analyzes source code changes and provides context-aware, senior-level engineering feedback directly generated into comprehensive markdown reports.

## 🎯 Objective
Perform intelligent code reviews across a variety of scopes and persist the findings natively into your local repository. 

### 🚀 Core Capabilities
- 🔄 Review by **Commit IDs** (single or range)
- 📄 Review by **Single File**
- 🔎 Fallback **Repository Scans** (latest uncommitted or last commit changes)

---

## 🧱 Tech Stack

| Component | Technology |
|---|---|
| **Framework** | ADK-Python (Google ADK) |
| **Execution Modes** | CLI (`adk run`) & Web UI (`adk web`) |
| **Backend Language** | Python |
| **LLM Engine** | Gemini 2.5 Flash (Default) |

---

## 📥 Inputs & Prompt Usage

When interacting with LocaReviewer in the CLI or Web UI, you can provide the following inputs in your prompt:

- `repo_path`: Path to the repository. (e.g., `.` or leave empty to use current working directory).
- `commit_ids`: One or multiple commit hashes. (e.g., `a1b2c3d` or `a1b2c3d f4g5h6i`).
- `file_path`: Path to a specific file to review.
- `review_mode`: 
  - `strict`: Detects all issues, includes negative points, provides fixes, and demands code snippets.
  - `moderate` (default): Validates correctness, uses constructive phrasing, only flags critical issues.
  - `unstrict`: Concise, assumes correctness unless there is a major blocker, focuses on approval reasoning.

### 💡 Example Prompts:
> "Please review the current directory in strict mode."

> "Review commit 9a8b7c6 in /path/to/repo using unstrict mode."

---

## 🔬 Review Dimensions
LocaReviewer evaluates code across the following dimensions:
1. **Correctness & Logic**
2. **Performance**
3. **Security**
4. **Code Quality (Clean Code Principles)**
5. **Design & Architecture**
6. **Standards Compliance (Python best practices, etc.)**

---

## ⚙️ How It Works (Tool-Driven Architecture)
The agent operates autonomously using strict deterministic logic through ADK tools:
1. **`git_diff_tool`**: Intelligently fetches git diffs or logs based on the provided commit hashes or directory context.
2. **`file_reader_tool`**: Localized tool to read a specific file explicitly provided by the user.
3. **`file_writer_tool`**: Persists the final structured markdown report locally without hallucinating or adding emojis.

---

## 🚀 Execution Guide

Make sure you have ADK installed and configured.

### 1. Navigate to the agent directory
```bash
cd LocaReviewer
```

### 2. CLI Mode (Interactive Terminal)
```bash
adk run agent.py:root_agent
```
*Best for fast, text-based interactive reviews.*

### 3. Web UI Mode
```bash
adk web agent.py:root_agent
```
*Spins up a local FastAPI server. Open the provided `localhost` URL in your browser to interact with LocaReviewer in a clean, sectioned Web interface.*

#### 🧑‍💻 User Interaction Steps in Web UI

**A. Performing a Commit ID Review:**
1. Open the Web UI in your browser.
2. In the chat input box, type your request specifying the commit hash(es) and the repository path. 
   - *Example Input:* `"Review commit abc1234 in the repository at C:/projects/my_app using strict mode."*
   - *Example Input (Multiple Commits):* `"Review changes between abc1234 and def5678 in ."`
3. Press **Send**.
4. The agent will invoke the `git_diff_tool`, analyze the diff, and stream the formatted Markdown code review back into the UI.
5. Once complete, check your repository folder to find the automatically generated `code_review_report_<timestamp>.md` file.

**B. Performing a File Review:**
1. Open the Web UI in your browser.
2. In the chat input box, type your request specifying the absolute or relative file path you want reviewed.
   - *Example Input:* `"Perform a moderate review on the file C:/projects/my_app/src/utils.py."*
3. Press **Send**.
4. The agent will use the `file_reader_tool` to read the entire file content, analyze its logic/quality, and return the structured report.
5. The final `.md` report will be saved to your working repository.

---

## 💾 Report Persistence
By design, all generated code reviews are automatically saved locally into the target repository directory under the naming convention:  
`code_review_report_YYYYMMDD_HHMMSS.md`

All files are strictly formatted in Markdown and encoded in UTF-8.

---

## 🤝 Contributing
Contributions, issues and feature requests are welcome!  
Feel free to check [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## ⚖️ License & Ownership

This project is open-sourced software licensed under the **[Apache License 2.0](LICENSE)**.

**Code Authorship & Maintainer:**
- 👤 **Shital Babaso Patil**
- 📧 **Email**: [shitalbabasopatil@gmail.com](mailto:shitalbabasopatil@gmail.com)
- 🌐 **Website**: [https://shitalam.in](https://shitalam.in)

> _"Empowering developers with intelligent, automated code feedback."_
