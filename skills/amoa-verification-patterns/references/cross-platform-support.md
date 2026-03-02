# Cross-Platform Support


## Contents

- [Table of Contents](#table-of-contents)
- [6.1 Platform-Specific Behavior](#61-platform-specific-behavior)
- [6.2 UTF-8 Encoding](#62-utf-8-encoding)
- [6.3 Platform Detection](#63-platform-detection)
- [6.4 Path Handling](#64-path-handling)
- [6.5 Command Execution](#65-command-execution)

---

## Table of Contents

- [6.1 Platform-Specific Behavior](#61-platform-specific-behavior)
  - 6.1.1 Port checking across platforms
  - 6.1.2 Process detection differences
  - 6.1.3 File operations with pathlib
  - 6.1.4 Subprocess platform-aware handling
- [6.2 UTF-8 Encoding](#62-utf-8-encoding)
  - 6.2.1 Explicit encoding for file operations
- [6.3 Platform Detection](#63-platform-detection)
  - 6.3.1 Using platform.system()
- [6.4 Path Handling](#64-path-handling)
  - 6.4.1 Using pathlib.Path for cross-platform paths
- [6.5 Command Execution](#65-command-execution)
  - 6.5.1 run_command() helper for platform-aware subprocess

---

## 6.1 Platform-Specific Behavior

All verification scripts work on Windows, macOS, and Linux.

| Feature | Windows | macOS/Linux |
|---------|---------|-------------|
| Port checking | Socket bind test | Socket bind test |
| Process detection | `netstat` | `lsof` |
| File operations | `pathlib.Path` | `pathlib.Path` |
| Subprocess | Shell-aware `run_command()` | Shell-aware `run_command()` |

---

## 6.2 UTF-8 Encoding

All file operations use explicit UTF-8 encoding for cross-platform text handling.

```python
# Always specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    content = f.read()

with open('file.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

---

## 6.3 Platform Detection

Scripts automatically detect the operating system:

```python
import platform

os_type = platform.system()  # Returns 'Windows', 'Darwin', or 'Linux'

if os_type == 'Windows':
    # Windows-specific behavior
    pass
elif os_type == 'Darwin':
    # macOS-specific behavior
    pass
else:
    # Linux/Unix behavior
    pass
```

---

## 6.4 Path Handling

Always use `pathlib.Path` for cross-platform path operations:

```python
from pathlib import Path

# Works on all platforms
config_path = Path.home() / ".config" / "app" / "config.json"
data_dir = Path.cwd() / "data"

# Check existence
if config_path.exists():
    content = config_path.read_text(encoding='utf-8')

# Create directories
data_dir.mkdir(parents=True, exist_ok=True)
```

---

## 6.5 Command Execution

Use the `run_command()` helper for platform-aware subprocess execution:

```python
import platform
import subprocess

def run_command(cmd, shell=False, check=True):
    """Run command with platform-aware shell handling."""
    if isinstance(cmd, str) and not shell:
        # Auto-enable shell for string commands on Windows
        shell = platform.system() == 'Windows'
    return subprocess.run(cmd, shell=shell, check=check, capture_output=True, text=True)

# Usage
result = run_command(['python3', 'script.py'])
print(result.stdout)
```
