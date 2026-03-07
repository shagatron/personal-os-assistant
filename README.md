Personal OS Assistant (JARVIS)

A local AI-powered desktop automation assistant built with Python that can control your operating system, launch apps, manage windows, and execute actions inside applications.

This project explores building a personal AI operating system interface.

Features
Smart App / File / Project Opening

The assistant intelligently opens:

applications

files

saved project folders

Example:

open chrome
open vscode
open os assistant
open notes

It searches across:

apps

files

saved projects

and ranks results by relevance.

Multi-Step Commands

Commands can be chained using and / then.

Example:

focus chrome and new tab
focus vscode and quick open

The assistant parses the command and executes actions sequentially.

Window Management

Commands:

list windows
focus chrome
focus vscode
active window

Capabilities:

detect open windows

focus applications

restore minimized windows

identify active window

Implemented using:

pywin32
In-App Automation

The assistant can perform actions inside applications using keyboard automation.

Example commands:

chrome new tab
chrome address bar
vscode quick open
vscode command palette

Execution flow:

focus window
↓
wait briefly
↓
send keyboard shortcut

Libraries used:

keyboard
pywin32
File System Tools

Commands:

find notes
create file ideas.txt
summarize file notes.txt

Capabilities:

recursive file search

file creation

text summarization

Persistent Memory

The assistant uses SQLite to store data.

Database:

memory.db

Tables include:

command history

saved projects

Example commands:

save project C:\Projects\myapp
list projects
open my last project
Architecture
User Input
   ↓
Parser
   ↓
Executor
   ↓
Tools Layer
   ↓
Operating System
Project Structure
personal-os-assistant
│
├── main.py
├── memory.db
│
├── agent
│   ├── parser.py
│   └── executor.py
│
├── tools
│   ├── apps.py
│   ├── files.py
│   ├── projects.py
│   ├── windows.py
│   ├── shortcuts.py
│   ├── open_router.py
│   └── memory.py
│
└── README.md
Technologies

Core:

Python

Libraries:

sqlite3
keyboard
pywin32
pathlib
subprocess
Example Usage
open chrome
chrome new tab
chrome address bar
focus vscode and quick open
Future Roadmap

Planned improvements:

AI Intent Parsing

Allow natural language commands like:

open the browser and search for python sqlite
launch my last coding project
Voice Control

Integrate speech input/output.

Advanced App Control

Deeper integrations for:

VS Code

Browsers

Media players

Long-Term Vision

Build a local AI operating system assistant capable of:

controlling applications

automating workflows

understanding natural language

executing multi-step tasks
