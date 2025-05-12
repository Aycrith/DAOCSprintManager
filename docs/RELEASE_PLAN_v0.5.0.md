# Release Plan: Version 0.5.0

## Release Date
May 13, 2024

## Feature Summary
1. Performance Statistics Display
2. Diagnostic Report Export
3. Enhanced UI (Start Minimized, Minimize to Tray)
4. Background Update Check & Notification
5. Pydantic V2 Validator Updates

## Pre-Release Checklist

### Code Completion
- [x] Task 8.1: Performance Statistics Display
- [x] Task 8.2: Diagnostic Report Export
- [x] Task 8.3: UI Customization Options
- [x] Task 8.4: Background Update Check & Notification
- [x] Task 8.5: Pydantic V2 Validator Updates

### Testing
- [ ] Run comprehensive unit tests
  ```
  cd src && python -m pytest ../tests -v
  ```
- [ ] Run specific UI tests for background update feature
  ```
  cd src && python -m pytest ../tests/ui/test_tray_app.py -v
  ```
- [ ] Manual testing of all new features
  - [ ] Performance Statistics window
  - [ ] Diagnostic Report generation and contents
  - [ ] UI customization options
  - [ ] Background update check (use mock updates for testing)

### Documentation
- [x] Update CHANGELOG.md with v0.5.0 information
- [x] Update README.md with new features
- [x] Update CONFIGURATION.md with new settings
- [x] Create developer documentation for new features
- [ ] Update user guide (if applicable)

### Version Updates
- [x] Update version in src/daoc_sprint_manager/__init__.py

## Release Package Preparation

### Build Steps
1. Clean build directories:
   ```
   python clean_build.py
   ```

2. Run PyInstaller build:
   ```
   python -m PyInstaller --noconfirm .\build_scripts\daoc_sprint_manager.spec
   ```

3. Verify build contents:
   ```
   dir dist\DAOC Sprint Manager
   ```

4. Test packaged application:
   ```
   .\dist\DAOC Sprint Manager\DAOC Sprint Manager.exe --version
   ```

### Package Contents Verification
- [ ] Executable: `DAOC Sprint Manager.exe`
- [ ] Config directory with template
- [ ] Data directory with icons and templates
- [ ] Document files (README, LICENSE)
- [ ] All required DLLs and dependencies

## GitHub Release Process

1. Create a release ZIP file:
   ```
   cd dist
   powershell Compress-Archive -Path "DAOC Sprint Manager" -DestinationPath "DAOC_Sprint_Manager_v0.5.0.zip" -Force
   ```

2. Generate SHA256 checksum:
   ```
   certutil -hashfile DAOC_Sprint_Manager_v0.5.0.zip SHA256 > DAOC_Sprint_Manager_v0.5.0.sha256
   ```

3. Create GitHub release:
   - Title: `v0.5.0: Performance, Diagnostics & UI Enhancements`
   - Tag: `v0.5.0`
   - Description: Copy content from CHANGELOG.md
   - Attach `DAOC_Sprint_Manager_v0.5.0.zip`
   - Attach `DAOC_Sprint_Manager_v0.5.0.sha256`

## Post-Release Tasks
- [ ] Announce release on channels (Discord, etc.)
- [ ] Create new development branch for next version
- [ ] Update roadmap for next release
- [ ] Close version milestone on GitHub
- [ ] Review and triage open issues 