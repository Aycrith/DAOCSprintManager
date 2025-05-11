# Phase 3 Profile Management System Testing Plan

## Overview

This document outlines a comprehensive testing plan for the Phase 3 Profile Management System implemented in the DAOC Sprint Manager. The testing will focus on verifying the correctness, reliability, and usability of all profile-related features.

## Test Environment Requirements

- Windows 10/11 operating system
- DAOC game client installed
- Multiple test DAoC character windows (can be simulated with renamed Notepad windows)
- Test profiles with different settings
- Backup of user profiles and settings

## 1. Profile Data Structure Tests

### 1.1 Profile Creation and Validation

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PDS-01 | Create a profile with valid data | Profile object is created with correct values |
| PDS-02 | Create a profile with empty name | Validation error |
| PDS-03 | Create a profile with duplicate name | Validation error or uniqueness check |
| PDS-04 | Verify UUID generation | Each profile has a unique ID |
| PDS-05 | Verify timestamp fields | `creation_date` and `last_used_date` are set correctly |

### 1.2 Profile Serialization/Deserialization

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PDS-06 | Serialize profile to JSON | Valid JSON with all fields |
| PDS-07 | Deserialize JSON to profile | Valid Profile object with all fields |
| PDS-08 | Handle datetime serialization | Dates correctly converted to/from ISO format |
| PDS-09 | Verify embedded AppSettings serialization | AppSettings correctly nested within Profile |

## 2. Profile Manager UI Tests

### 2.1 ProfileManagerDialog UI

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PMU-01 | Open Profile Manager from tray menu | Dialog appears correctly |
| PMU-02 | Display existing profiles in list | All profiles shown with correct names |
| PMU-03 | Show active profile indication | Active profile is visually distinct |
| PMU-04 | Verify dialog modal behavior | Cannot interact with app while dialog open |

### 2.2 Profile Creation

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PMU-05 | Click "New Profile" button | ProfileEditDialog appears |
| PMU-06 | Create profile with valid data | Dialog closes, new profile appears in list |
| PMU-07 | Try creating duplicate profile | Error message shown |
| PMU-08 | Cancel profile creation | No new profile created |

### 2.3 Profile Editing

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PMU-09 | Select profile and click "Edit" | ProfileEditDialog opens with profile data |
| PMU-10 | Edit profile name | Name updated in list after save |
| PMU-11 | Edit game character name | Change saved correctly |
| PMU-12 | Edit application settings | Changes reflected in profile |
| PMU-13 | Edit window title pattern | Pattern saved correctly |
| PMU-14 | Cancel edit | No changes applied |

### 2.4 Profile Deletion

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PMU-15 | Select profile and click "Delete" | Confirmation dialog appears |
| PMU-16 | Confirm deletion | Profile removed from list |
| PMU-17 | Cancel deletion | Profile remains in list |
| PMU-18 | Delete active profile | Confirmation warns about active profile |

### 2.5 Profile Import/Export

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PMU-19 | Export profiles to file | File created with correct JSON format |
| PMU-20 | Import profiles from valid file | Profiles added to list |
| PMU-21 | Handle import conflicts | Prompted for action on name conflicts |
| PMU-22 | Import from invalid file | Appropriate error message |

## 3. Profile Switching Logic Tests

### 3.1 Manual Profile Switching

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PSL-01 | Select profile from tray menu | Profile activated, settings applied |
| PSL-02 | Set profile as active in Profile Manager | Profile activated, settings applied |
| PSL-03 | Switch between profiles | Settings correctly updated each time |
| PSL-04 | Switch to profile with different detection method | Detection method changed correctly |
| PSL-05 | Switch to profile with different ROI | ROI updated correctly |

### 3.2 Profile Persistence

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PSL-06 | Restart application after profile selection | Active profile remembered and loaded |
| PSL-07 | Verify global `active_profile_id` in settings.json | ID matches selected profile |
| PSL-08 | Verify profiles saved to profiles.json | All profiles correctly stored |
| PSL-09 | Backup and restore profiles | Profiles load correctly from backup |

### 3.3 Resource Handling

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| PSL-10 | Verify templates reload on profile switch | Correct templates loaded for profile |
| PSL-11 | Verify detector initialization on switch | Detector reinitialized with new settings |
| PSL-12 | Handle missing resources for profile | Appropriate error/fallback behavior |
| PSL-13 | Resource cleanup on profile switch | No resource leaks, memory usage stable |

## 4. Auto-Switching Feature Tests

### 4.1 Window Pattern Matching

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| ASW-01 | Set window title pattern for profile | Pattern saved correctly |
| ASW-02 | Launch window matching pattern | Profile auto-switches correctly |
| ASW-03 | Test with case-insensitive pattern | Matches regardless of case |
| ASW-04 | Multiple windows match different profiles | Most specific pattern profile selected |
| ASW-05 | No windows match any profiles | No auto-switching occurs |

### 4.2 Auto-Switch Configuration

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| ASW-06 | Enable auto-switching in ConfigGUI | Feature activated |
| ASW-07 | Disable auto-switching in ConfigGUI | Feature deactivated |
| ASW-08 | Verify auto-switch check interval | Checks occur at expected frequency |
| ASW-09 | Status updates during auto-switch | Logging shows switch events |

### 4.3 Edge Cases

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| ASW-10 | Rapid window switching | Auto-switching functions correctly |
| ASW-11 | Very long window titles | Pattern matching works correctly |
| ASW-12 | Special characters in window titles | Pattern matching handles special chars |
| ASW-13 | Switching during detection loop | Application remains stable |
| ASW-14 | Very similar window patterns | Most specific (longest) pattern wins |

## 5. Integration Tests

### 5.1 Full Application Flow

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| INT-01 | Create profiles through UI | Profiles created and saved |
| INT-02 | Configure auto-switching patterns | Patterns saved correctly |
| INT-03 | Launch multiple game windows | Auto-switching occurs correctly |
| INT-04 | Manual override of auto-switched profile | Manual selection takes precedence |
| INT-05 | Restart application | Profile state preserved |

### 5.2 Performance and Stress Tests

| Test ID | Description | Expected Result |
|---------|-------------|-----------------|
| INT-06 | Create large number of profiles (20+) | Application remains responsive |
| INT-07 | Rapid profile switching | Application remains stable |
| INT-08 | Profile with large templates | Loading and switching works correctly |
| INT-09 | Extended run time with auto-switching | No memory leaks or performance degradation |

## 6. Usability Tests

| Test ID | Description | Expected Areas of Focus |
|---------|-------------|-------------------|
| USR-01 | Profile creation workflow | Ease of creating first profile |
| USR-02 | Profile editing workflow | Intuitive access to settings |
| USR-03 | Auto-switching setup | Clear pattern configuration |
| USR-04 | Manual profile switching | Easy access to profile selection |
| USR-05 | Error messages | Clear, actionable feedback |

## Test Execution Checklist

- [ ] Prepare test environment with sample profiles and window configurations
- [ ] Execute all test cases and document results
- [ ] Identify and log any issues found
- [ ] Prioritize issues based on severity and impact
- [ ] Address critical issues before release
- [ ] Re-test fixed issues
- [ ] Conduct final integration test to verify overall system stability

## Issue Reporting

For each issue identified during testing, document:

1. Test ID and description
2. Steps to reproduce
3. Expected vs. actual result
4. Screenshot or log excerpt where applicable
5. Environment details (OS version, Python version, etc.)

## Conclusion

This testing plan provides comprehensive coverage of the Profile Management System. Successful execution of these tests will validate that the system meets all requirements for correctness, reliability, and usability. Any issues identified during testing should be addressed prior to release to ensure a high-quality user experience. 