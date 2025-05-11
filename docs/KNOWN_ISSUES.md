# Known Issues and Limitations

This document outlines known issues, limitations, and workarounds for the DAOC Sprint Manager v0.3.0.

## Detection Related

### Template Matching

1. **UI Scale Sensitivity**
   - **Issue:** Template matching can be sensitive to UI scaling changes
   - **Impact:** May require reconfiguration of ROI
   - **Workaround:** Create separate profiles for different UI scales

2. **Lighting Conditions**
   - **Issue:** Extreme in-game lighting can affect detection
   - **Impact:** Reduced detection accuracy in certain areas
   - **Workaround:** Adjust game brightness/contrast settings

3. **UI Mod Compatibility**
   - **Issue:** Custom UI mods may affect sprint icon appearance
   - **Impact:** Template matching might fail
   - **Workaround:** Use ML detection method or create custom templates

### ML Detection

1. **Model Requirements**
   - **Issue:** ML detection requires user-provided ONNX model
   - **Impact:** Not available out-of-box
   - **Workaround:** Use template matching until model is provided

2. **Resource Usage**
   - **Issue:** Higher CPU/memory usage compared to template matching
   - **Impact:** May affect game performance on lower-end systems
   - **Workaround:** Use template matching on lower-end systems

## Performance Related

1. **High FPS Impact**
   - **Issue:** FPS > 30 increases CPU usage significantly
   - **Impact:** May affect game performance
   - **Workaround:** Keep FPS at 30 or lower

2. **Multiple Profiles**
   - **Issue:** Large number of profiles increases memory usage
   - **Impact:** Slower profile switching
   - **Workaround:** Remove unused profiles

3. **Auto-Profile Switching**
   - **Issue:** Can cause brief CPU spikes during switches
   - **Impact:** Momentary performance impact
   - **Workaround:** Disable if not needed

## System Tray Related

1. **Icon Persistence**
   - **Issue:** Icon may remain after abnormal shutdown
   - **Impact:** Visual annoyance
   - **Workaround:** Manual removal via Task Manager

2. **Menu Response**
   - **Issue:** Menu may be slow to respond during heavy detection
   - **Impact:** UI feels less responsive
   - **Workaround:** Pause detection before configuration changes

## Configuration Related

1. **Settings File**
   - **Issue:** Manual edits to settings.json not validated
   - **Impact:** Could cause application errors
   - **Workaround:** Use Configuration GUI

2. **ROI Selection**
   - **Issue:** ROI helper tool requires game in windowed mode
   - **Impact:** Cannot configure in fullscreen
   - **Workaround:** Temporarily switch to windowed mode

## Game Integration

1. **Window Detection**
   - **Issue:** May not detect game window immediately after launch
   - **Impact:** Delayed start of detection
   - **Workaround:** Wait a few seconds after game launch

2. **Multi-Monitor**
   - **Issue:** ROI coordinates may shift on resolution changes
   - **Impact:** Incorrect detection area
   - **Workaround:** Reconfigure ROI after display changes

## Error Recovery

1. **Game Window Loss**
   - **Issue:** May take up to 5 seconds to detect window loss
   - **Impact:** Brief continued operation without valid window
   - **Workaround:** None needed, auto-recovers

2. **Profile Corruption**
   - **Issue:** Corrupted profiles not automatically repaired
   - **Impact:** Profile may need manual deletion
   - **Workaround:** Delete corrupted profile file

## Testing Coverage

1. **Edge Cases**
   - **Issue:** Not all game UI variations tested
   - **Impact:** May encounter issues with unusual setups
   - **Workaround:** Report issues for investigation

2. **Error Paths**
   - **Issue:** Some rare error conditions not fully tested
   - **Impact:** May not handle all error cases gracefully
   - **Workaround:** Report unexpected behavior

## Future Improvements

1. **Planned Enhancements**
   - Automatic ROI adjustment
   - Improved error recovery
   - Better profile corruption handling
   - Enhanced performance monitoring

2. **Known Limitations to Address**
   - Limited multi-character support
   - Basic profile management
   - Simple detection methods

## Reporting Issues

If you encounter any issues not listed here:
1. Check the latest documentation
2. Verify your configuration
3. Submit an issue on GitHub with:
   - Detailed description
   - Steps to reproduce
   - System information
   - Log files 