#!/usr/bin/env python
"""
DAOC Sprint Manager - Session Starter
This script displays key reminders about the communication protocol with Gemini
at the beginning of each development session.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import textwrap

class SessionStarter:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.workflow_file = self.project_root / "WORKFLOW.md"
        
    def display_header(self):
        """Display session header with date and time"""
        print("\n" + "="*80)
        print(f"DAOC SPRINT MANAGER - SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
        
    def display_protocol_reminders(self):
        """Display key protocol reminders for working with Gemini"""
        reminders = """
        KEY REMINDERS FOR COLLABORATING WITH GEMINI:
        
        1. ALWAYS provide complete file content to Gemini before requesting changes
        
        2. Use this format for providing file context:
           ```python name=src/path/to/file.py
           # entire current content of file.py
           ```
           
        3. After applying Gemini's changes, explicitly confirm:
           "Confirmed: The changes have been applied to `path/to/file.py`"
           
        4. For errors, provide:
           - Full error message and traceback
           - Relevant log content
           - Screenshots for UI issues
           - Steps that led to the error
           
        5. Remember: Gemini cannot see your screen, access your file system,
           or run commands directly
        """
        print(textwrap.dedent(reminders))
        
    def check_workflow_file(self):
        """Check if the WORKFLOW.md file exists and offer to display it"""
        if not self.workflow_file.exists():
            print("WARNING: WORKFLOW.md file not found! Communication protocol documentation is missing.")
            return
            
        response = input("Would you like to review the full communication protocol? (y/n): ")
        if response.lower() in ('y', 'yes'):
            with open(self.workflow_file, 'r') as f:
                print("\n" + "="*80)
                print("COMMUNICATION PROTOCOL WITH GEMINI:")
                print("="*80 + "\n")
                print(f.read())
                
    def run(self):
        """Run the session starter"""
        self.display_header()
        self.display_protocol_reminders()
        self.check_workflow_file()
        print("\n" + "="*80)
        print("SESSION PREPARATION COMPLETE - READY TO COLLABORATE WITH GEMINI")
        print("="*80 + "\n")
        
if __name__ == "__main__":
    starter = SessionStarter()
    starter.run() 