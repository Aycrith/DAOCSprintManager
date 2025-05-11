# DAOC Sprint Manager - Communication & Workflow Protocol

## Purpose
This document outlines the communication protocol between the Cursor IDE Agent and Gemini LLM for the DAOC Sprint Manager project.

## Key Principles

1. **Gemini has no direct file system access or execution capabilities**
2. **IDE Agent is responsible for all file operations and execution**
3. **Complete file context must be provided to Gemini before requesting changes**

## Workflow Steps

1. **Task Assignment**
   - Human or Orchestrator provides a task for Gemini

2. **Context Provision**
   - IDE Agent provides complete file content to Gemini before requesting modifications
   - Example format:
     ```python name=src/daoc_sprint_manager/ui/config_gui.py
     # ... entire current content of config_gui.py ...
     ```

3. **Code Generation**
   - Gemini analyzes the context and generates code in file blocks
   - IDE Agent creates/modifies files based on these blocks

4. **Execution & Testing**
   - IDE Agent executes the code locally
   - IDE Agent performs testing as needed

5. **Result Reporting**
   - IDE Agent confirms file operations to Gemini
   - IDE Agent reports execution results or errors with full context

6. **Iteration**
   - Repeat steps 2-5 as needed until task is complete

## IDE Agent Responsibilities

1. **File Operations:**
   - Create, modify, and save all project files
   - Apply changes to correct files
   - Confirm all file operations to Gemini

2. **Execution & Testing:**
   - Run all Python scripts, tests, and commands
   - Perform local testing and debugging

3. **Context Provision:**
   - Provide complete file contents before requesting modifications
   - Include relevant snippets or full content of interacting modules

4. **Error Reporting:**
   - Capture full error messages and tracebacks
   - Provide log file content when relevant
   - Include screenshots for UI-related issues
   - Describe steps that led to the error

## Example Communication

**IDE Agent to Gemini:**
```
I need to implement [feature X] in the config_gui.py file. Here's the current content:

```python name=src/daoc_sprint_manager/ui/config_gui.py
# ... entire current content of config_gui.py ...
```
```

**Gemini to IDE Agent:**
```
Here's the implementation for [feature X]:

```python
# ... modified code with new feature ...
```
```

**IDE Agent to Gemini:**
```
Confirmed: The changes have been applied to `src/daoc_sprint_manager/ui/config_gui.py`.

Execution result: [success/error details]
```

## Important Reminders

- Gemini cannot see your screen, access your file system, or run commands directly
- All information Gemini has about the project state comes from what you provide
- Gemini's file block outputs are proposals for file content, not direct file operations 