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

import warnings
from mcp.server.fastmcp import FastMCP
from agent import git_diff_tool, file_reader_tool, file_writer_tool

# Suppress all warnings from the 'authlib' module to silence deprecation messages
warnings.filterwarnings("ignore", module="authlib")

# Initialize FastMCP server for LocaReviewer
# This allows any MCP-compatible client (like Claude Desktop or Cursor) 
# to discover and use these code review tools.
mcp = FastMCP("LocaReviewer")

@mcp.tool()
def fetch_git_diff(repo_path: str, commit_ids: str = "") -> str:
    """
    Fetches the git diff for given commit IDs in a repository.
    
    Args:
        repo_path: Path to the repository. '.' or empty string means current working directory.
        commit_ids: A single commit hash or multiple commit hashes separated by spaces.
    """
    return git_diff_tool(repo_path, commit_ids)

@mcp.tool()
def read_file_content(repo_path: str, file_path: str) -> str:
    """
    Reads the content of a single file for code review.
    
    Args:
        repo_path: Path to the repository. '.' or empty string means current working directory.
        file_path: Path to the file to read, relative to repo_path or absolute.
    """
    return file_reader_tool(repo_path, file_path)

@mcp.tool()
def save_review_report(report_content: str, repo_path: str = "", file_path: str = "") -> str:
    """
    Saves the generated markdown code review report to the correct directory with a UTC timestamp.
    
    Args:
        report_content: The full markdown text of the code review report.
        repo_path: The repository path (if provided by user).
        file_path: The reviewed file path (if provided by user).
    """
    return file_writer_tool(report_content, repo_path, file_path)

if __name__ == "__main__":
    # Run the MCP server using Stdio transport (default for FastMCP)
    mcp.run()
