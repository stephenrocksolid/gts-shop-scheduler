"""
Test to guard against hard-coded URLs in JavaScript files.

Phase 5 of the frontend refactor eliminates hard-coded app routes in JS.
This test ensures that pattern doesn't creep back in.

Note: This test does not require Django and can run standalone.
Run with: python -m pytest tests/test_no_hardcoded_urls.py -p no:django
Or run as a script: python tests/test_no_hardcoded_urls.py
"""
import re
from pathlib import Path

import pytest


# Directories to scan for hard-coded URLs
SCAN_DIRS = [
    "rental_scheduler/static/rental_scheduler/js/calendar/",
    "rental_scheduler/static/rental_scheduler/js/entrypoints/",
    "rental_scheduler/static/rental_scheduler/js/shared/",
]

# Individual files to scan
SCAN_FILES = [
    "rental_scheduler/static/rental_scheduler/js/workspace.js",
]

# Patterns that indicate hard-coded app routes (forbidden)
FORBIDDEN_PATTERNS = [
    # App-prefixed routes (wrong prefix)
    r"['\"`]/rental_scheduler/",
    # Direct API routes
    r"['\"`]/api/jobs/",
    r"['\"`]/api/recurrence/",
    # Direct page routes
    r"['\"`]/jobs/",
    r"['\"`]/calendars/",
    r"['\"`]/call-reminders/",
]

# Files to exclude from scanning (e.g., legacy config that's out of scope)
EXCLUDE_FILES = [
    "rental_scheduler/static/rental_scheduler/js/config.js",
]

# Patterns that are allowed (false positives)
ALLOWLIST_PATTERNS = [
    # Static asset URLs are fine
    r"['\"`]/static/",
    # Comments explaining what not to do
    r"//.*['\"`]/",
    r"\*.*['\"`]/",
    # URLs in error messages or console logs
    r"console\.(log|error|warn|debug).*['\"`]/",
]


def get_project_root() -> Path:
    """Get the project root directory."""
    # This test file is in tests/, so project root is one level up
    return Path(__file__).parent.parent


def collect_js_files() -> list[Path]:
    """Collect all JS files that should be scanned."""
    project_root = get_project_root()
    files = []

    # Collect from directories
    for dir_path in SCAN_DIRS:
        full_dir = project_root / dir_path
        if full_dir.exists():
            files.extend(full_dir.glob("**/*.js"))

    # Add individual files
    for file_path in SCAN_FILES:
        full_path = project_root / file_path
        if full_path.exists():
            files.append(full_path)

    # Remove excluded files
    exclude_paths = {project_root / f for f in EXCLUDE_FILES}
    files = [f for f in files if f not in exclude_paths]

    return sorted(set(files))


def is_allowlisted(line: str) -> bool:
    """Check if a line matches any allowlist pattern."""
    for pattern in ALLOWLIST_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def find_violations(file_path: Path) -> list[tuple[int, str, str]]:
    """
    Find hard-coded URL violations in a file.
    
    Returns list of (line_number, line_content, matched_pattern) tuples.
    """
    violations = []
    
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        pytest.fail(f"Could not read {file_path}: {e}")
        return []
    
    lines = content.splitlines()
    
    for line_num, line in enumerate(lines, start=1):
        # Skip allowlisted lines
        if is_allowlisted(line):
            continue
        
        # Check each forbidden pattern
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                violations.append((line_num, line.strip(), pattern))
                break  # Only report one violation per line
    
    return violations


class TestNoHardcodedUrls:
    """Test suite for detecting hard-coded URLs in JavaScript files."""

    def test_js_files_exist(self):
        """Verify that we have JS files to scan."""
        files = collect_js_files()
        assert len(files) > 0, "No JS files found to scan"

    def test_no_hardcoded_urls_in_calendar_modules(self):
        """Check calendar modules for hard-coded URLs."""
        project_root = get_project_root()
        calendar_dir = project_root / "rental_scheduler/static/rental_scheduler/js/calendar/"
        
        if not calendar_dir.exists():
            pytest.skip("Calendar directory not found")
        
        all_violations = []
        for js_file in calendar_dir.glob("*.js"):
            violations = find_violations(js_file)
            for line_num, line, pattern in violations:
                all_violations.append(
                    f"{js_file.name}:{line_num}: {line[:80]}{'...' if len(line) > 80 else ''}"
                )
        
        if all_violations:
            msg = "Hard-coded URLs found in calendar modules:\n" + "\n".join(all_violations)
            pytest.fail(msg)

    def test_no_hardcoded_urls_in_entrypoints(self):
        """Check entrypoint scripts for hard-coded URLs."""
        project_root = get_project_root()
        entrypoints_dir = project_root / "rental_scheduler/static/rental_scheduler/js/entrypoints/"
        
        if not entrypoints_dir.exists():
            pytest.skip("Entrypoints directory not found")
        
        all_violations = []
        for js_file in entrypoints_dir.glob("*.js"):
            violations = find_violations(js_file)
            for line_num, line, pattern in violations:
                all_violations.append(
                    f"{js_file.name}:{line_num}: {line[:80]}{'...' if len(line) > 80 else ''}"
                )
        
        if all_violations:
            msg = "Hard-coded URLs found in entrypoints:\n" + "\n".join(all_violations)
            pytest.fail(msg)

    def test_no_hardcoded_urls_in_workspace(self):
        """Check workspace.js for hard-coded URLs."""
        project_root = get_project_root()
        workspace_file = project_root / "rental_scheduler/static/rental_scheduler/js/workspace.js"
        
        if not workspace_file.exists():
            pytest.skip("workspace.js not found")
        
        violations = find_violations(workspace_file)
        
        if violations:
            violation_strs = [
                f"Line {line_num}: {line[:80]}{'...' if len(line) > 80 else ''}"
                for line_num, line, pattern in violations
            ]
            msg = "Hard-coded URLs found in workspace.js:\n" + "\n".join(violation_strs)
            pytest.fail(msg)

    def test_all_scanned_files_summary(self):
        """Comprehensive check of all scanned files with summary."""
        files = collect_js_files()
        all_violations = {}
        
        for js_file in files:
            violations = find_violations(js_file)
            if violations:
                rel_path = js_file.relative_to(get_project_root())
                all_violations[str(rel_path)] = violations
        
        if all_violations:
            msg_parts = ["Hard-coded URLs found in the following files:"]
            for file_path, violations in sorted(all_violations.items()):
                msg_parts.append(f"\n{file_path}:")
                for line_num, line, pattern in violations[:5]:  # Show first 5 per file
                    truncated = line[:60] + "..." if len(line) > 60 else line
                    msg_parts.append(f"  Line {line_num}: {truncated}")
                if len(violations) > 5:
                    msg_parts.append(f"  ... and {len(violations) - 5} more violations")
            
            pytest.fail("\n".join(msg_parts))


# =========================================================================
# STANDALONE RUNNER
# Run this file directly: python tests/test_no_hardcoded_urls.py
# =========================================================================

def run_standalone():
    """Run the check without pytest."""
    print("Checking for hard-coded URLs in JavaScript files...")
    
    files = collect_js_files()
    print(f"Found {len(files)} JS files to scan")
    
    all_violations = {}
    for js_file in files:
        violations = find_violations(js_file)
        if violations:
            rel_path = js_file.relative_to(get_project_root())
            all_violations[str(rel_path)] = violations
    
    if all_violations:
        print("\n❌ VIOLATIONS FOUND:\n")
        for file_path, violations in sorted(all_violations.items()):
            print(f"{file_path}:")
            for line_num, line, pattern in violations:
                truncated = line[:70] + "..." if len(line) > 70 else line
                print(f"  Line {line_num}: {truncated}")
            print()
        return 1
    else:
        print("\n✅ SUCCESS: No hard-coded URLs found!")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_standalone())

