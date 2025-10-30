# ETL Log Analyzer - Quick Reference

## Installation (30 seconds)
```bash
pip install pandas matplotlib
python etl_log_analyzer.py
```

## Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `Ctrl+O` | Open log file |
| `Ctrl+E` | Export report |
| `Ctrl+R` | Refresh analysis |
| `Ctrl+Q` | Quit |

## Common Tasks

### Analyze a Log File
1. Press `Ctrl+O`
2. Select log file
3. Review Summary tab
4. Check Errors tab if issues found

### Find Specific Errors
1. Go to Search tab (🔍)
2. Type error keyword
3. Click Search
4. Review results

### Export Report
1. Press `Ctrl+E`
2. Choose format (TXT/JSON)
3. Select save location
4. Click Save

## Tab Guide

| Tab | Purpose | Key Info |
|-----|---------|----------|
| 📋 Summary | Overview | Total stats, root causes |
| ❌ Errors | Error details | Line numbers, timestamps |
| 📈 Timeline | Visual events | When errors occurred |
| ⚡ Performance | Charts | Duration, volume analysis |
| 🔍 Search | Find text | Keyword search |

## Root Cause Indicators

| Message | Likely Cause | Action |
|---------|-------------|--------|
| Connection/Network Issues | DB unavailable | Check connectivity |
| Memory Issues | Low heap | Increase memory |
| Data Quality Issues | Bad data | Review validation |
| Permission Issues | Auth failed | Check credentials |
| Performance Bottlenecks | Slow ops | Optimize queries |

## Log Patterns Detected

### Timestamps
- `2025-10-29 08:00:00`
- `10/29/2025 08:00:00`
- `[2025-10-29T08:00:00]`

### Log Levels
- **ERROR**: Critical failures
- **WARNING**: Potential issues
- **INFO**: Normal operations
- **SUCCESS**: Completed tasks

### Metrics Extracted
- Job/workflow names
- Duration (seconds)
- Rows processed
- Error messages

## Performance Metrics

### Normal Ranges
- Error rate: <1%
- Warning rate: <5%
- Avg duration: Within SLA
- Success rate: >99%

### Red Flags
- ❌ Error rate >5%
- ❌ Multiple connection failures
- ❌ Memory errors
- ❌ Duration >2x baseline
- ❌ Zero rows processed

## Export Formats

### TXT Format
- Human-readable
- Complete analysis
- Good for documentation
- Easy to read/share

### JSON Format
- Machine-readable
- Structured data
- Good for automation
- API integration

## Troubleshooting Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| App won't start | `sudo apt install python3-tk` |
| Can't load file | Check file encoding (UTF-8) |
| No charts | `pip install --upgrade matplotlib` |
| App freezes | Wait for parsing (large files) |
| No timestamps | Verify log format |

## Sample Workflows

### Daily Check (2 minutes)
```
1. Load today's log
2. Check error count (should be 0)
3. Note any warnings
4. Export JSON for tracking
```

### Incident Response (5 minutes)
```
1. Load failed job log
2. Check root causes
3. Go to Errors tab
4. Read error messages
5. Check Timeline for pattern
6. Export report
```

### Performance Tuning (10 minutes)
```
1. Load log file
2. Check avg duration
3. Review Performance tab
4. Identify slow operations
5. Search for context
6. Document findings
```

## Command Line Usage

### Basic
```bash
python etl_log_analyzer.py
```

### With Launcher
```bash
# Windows
launch.bat

# Linux/Mac
chmod +x launch.sh
./launch.sh
```

### Test Installation
```bash
python test_analyzer.py
```

## File Organization

```
project/
├── etl_log_analyzer.py     # Main application
├── test_analyzer.py         # Test script
├── sample_etl.log           # Sample log 1
├── sample_informatica.log   # Sample log 2
├── requirements.txt         # Dependencies
├── README.md                # Full documentation
├── USER_GUIDE.md            # Detailed guide
└── launch.sh / launch.bat   # Launchers
```

## Common Search Terms

### Finding Errors
- `ERROR`
- `FATAL`
- `Exception`
- `failed`
- `timeout`

### Performance Issues
- `duration`
- `elapsed`
- `slow`
- `took`

### Data Issues
- `null`
- `invalid`
- `constraint`
- `duplicate`

### Connection Issues
- `connection`
- `timeout`
- `network`
- `denied`

## Configuration Tips

### For Large Files
- Split logs if >100MB
- Close other apps
- Be patient during parsing
- Use filters to focus

### For Better Analysis
- Ensure logs have timestamps
- Include duration metrics
- Log job names clearly
- Add row counts

## Best Practices

### ✅ DO
- Review Summary first
- Check root causes
- Use Timeline for context
- Export reports regularly
- Compare over time

### ❌ DON'T
- Skip error review
- Ignore warnings
- Delete logs before analysis
- Mix different log formats
- Forget to document findings

## Support Resources

- **README.md**: Full project documentation
- **USER_GUIDE.md**: Detailed usage guide
- **Sample logs**: Example files to test
- **Test script**: Verify installation

## Feature Checklist

- [x] Multi-format log parsing
- [x] Error detection
- [x] Warning tracking
- [x] Performance analysis
- [x] Visual timeline
- [x] Root cause suggestions
- [x] Search functionality
- [x] Export reports
- [x] Job statistics
- [x] Duration tracking

## Version Info
- **Version**: 1.0
- **Python**: 3.8+
- **Status**: Production Ready
- **Platform**: Cross-platform

---

**Quick Start**: `pip install pandas matplotlib && python etl_log_analyzer.py`

**Most Common Use**: Open log → Review Summary → Check Errors → Export report

**Remember**: Summary tab shows the big picture, Errors tab shows the details!
