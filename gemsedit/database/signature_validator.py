"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2021-2026 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal
import webbrowser

from gemsedit.database.yamlsqlexchange import migrate_old_playvideo, migrate_old_portalto


class IssueType(Enum):
    UNKNOWN_NAME = "unknown_name"
    PARAM_COUNT_MISMATCH = "param_count"
    PARSE_ERROR = "parse_error"


@dataclass
class SignatureIssue:
    """Represents a single signature validation issue."""

    issue_type: IssueType
    signature_type: Literal["action", "condition", "trigger"]
    raw_string: str
    parsed_name: str
    context_type: str  # 'global', 'pocket', 'view', 'object'
    view_id: str | None = None
    view_name: str | None = None
    object_id: str | None = None
    object_name: str | None = None
    action_id: str | None = None
    message: str = ""
    expected_params: int = 0
    actual_params: int = 0
    expected_template: list[str] = field(default_factory=list)
    actual_values: list = field(default_factory=list)


@dataclass
class ValidationResult:
    """Holds all validation results for a database."""

    issues: list[SignatureIssue] = field(default_factory=list)
    total_actions_checked: int = 0
    total_conditions_checked: int = 0
    total_triggers_checked: int = 0
    yaml_file_path: str = ""

    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0

    @property
    def issue_count(self) -> int:
        return len(self.issues)


def _parse_params(args_str: str) -> list[str]:
    """
    Parse comma-separated parameters, respecting quoted strings.

    Example: '"hello, world",42,True' -> ['"hello, world"', '42', 'True']
    """
    params = []
    current = ""
    in_quotes = False
    quote_char = None
    bracket_depth = 0

    for char in args_str:
        if char in ('"', "'") and bracket_depth == 0:
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
            current += char
        elif char == "[":
            bracket_depth += 1
            current += char
        elif char == "]":
            bracket_depth -= 1
            current += char
        elif char == "," and not in_quotes and bracket_depth == 0:
            params.append(current.strip())
            current = ""
        else:
            current += char

    if current.strip():
        params.append(current.strip())

    return params


def parse_signature_string(sig_str: str) -> tuple[str, list[str]] | None:
    """
    Parse a function-call style string like 'PortalTo(1,"")' or 'MouseClick()'.

    Returns:
        tuple of (function_name, list_of_param_strings) or None if parse fails

    Examples:
        'PortalTo(1,"")' -> ('PortalTo', ['1', '""'])
        'MouseClick()' -> ('MouseClick', [])
        'PlayVideo("file.mp4",0,0,0,1.0,False)' -> ('PlayVideo', ['"file.mp4"', '0', '0', '0', '1.0', 'False'])
    """
    if not sig_str or not isinstance(sig_str, str):
        return None

    sig_str = sig_str.strip()
    if not sig_str:
        return ("", [])  # Empty action/condition/trigger is valid (means "none")

    try:
        paren_start = sig_str.index("(")
        paren_end = sig_str.rindex(")")

        name = sig_str[:paren_start].strip()
        args_str = sig_str[paren_start + 1 : paren_end].strip()

        if not args_str:
            return (name, [])

        params = _parse_params(args_str)
        return (name, params)

    except (ValueError, IndexError):
        return None


def build_signature_lookup(db_dict: dict) -> dict[str, dict[str, dict]]:
    """
    Build lookup dictionaries from the *_lst tables.

    Returns:
        {
            'action': {'PortalTo': {'template': ['viewnum', 'vidfile'], 'labels': ['View', 'VidFile']}, ...},
            'condition': {...},
            'trigger': {...}
        }
    """
    lookup: dict[str, dict[str, dict]] = {"action": {}, "condition": {}, "trigger": {}}

    for list_type in ("action_lst", "condition_lst", "trigger_lst"):
        sig_type = list_type.replace("_lst", "")
        for entry in db_dict.get(list_type, {}).values():
            name = entry.get("Name", "")
            if name:  # Skip empty entries (Id=0)
                template_str = entry.get("Template", "[]")
                labels_str = entry.get("Labels", "[]")
                # Templates are stored as JSON-like strings: '["viewnum","vidfile"]'
                try:
                    template = eval(template_str) if template_str else []
                    labels = eval(labels_str) if labels_str else []
                except Exception:
                    template = []
                    labels = []
                lookup[sig_type][name] = {"template": template, "labels": labels}

    return lookup


def validate_signature(
    sig_str: str,
    sig_type: Literal["action", "condition", "trigger"],
    lookup: dict[str, dict[str, dict]],
    context: dict,
) -> SignatureIssue | None:
    """
    Validate a single action/condition/trigger string.

    Args:
        sig_str: The function-call string like 'PortalTo(1,"")'
        sig_type: One of 'action', 'condition', 'trigger'
        lookup: The lookup dict from build_signature_lookup()
        context: Dict with keys like 'context_type', 'view_id', 'view_name', etc.

    Returns:
        SignatureIssue if validation fails, None if valid
    """
    # Empty strings are valid (means no action/condition/trigger)
    if not sig_str or not sig_str.strip():
        return None

    parsed = parse_signature_string(sig_str)

    if parsed is None:
        return SignatureIssue(
            issue_type=IssueType.PARSE_ERROR,
            signature_type=sig_type,
            raw_string=sig_str,
            parsed_name="",
            message=f"Could not parse {sig_type} string: '{sig_str}'",
            **context,
        )

    name, params = parsed

    # Empty name is valid (Id=0 in *_lst)
    if not name:
        return None

    type_lookup = lookup.get(sig_type, {})

    # Check if name exists
    if name not in type_lookup:
        return SignatureIssue(
            issue_type=IssueType.UNKNOWN_NAME,
            signature_type=sig_type,
            raw_string=sig_str,
            parsed_name=name,
            message=f"Unknown {sig_type} name: '{name}'",
            actual_params=len(params),
            actual_values=params,
            **context,
        )

    # Check parameter count
    expected = type_lookup[name]
    expected_count = len(expected["template"])
    actual_count = len(params)

    if expected_count != actual_count:
        return SignatureIssue(
            issue_type=IssueType.PARAM_COUNT_MISMATCH,
            signature_type=sig_type,
            raw_string=sig_str,
            parsed_name=name,
            message=f"Parameter count mismatch for '{name}': expected {expected_count}, got {actual_count}",
            expected_params=expected_count,
            actual_params=actual_count,
            expected_template=expected["template"],
            actual_values=params,
            **context,
        )

    return None


def validate_database(db_dict: dict) -> ValidationResult:
    """
    Scan the entire database dictionary and collect all signature issues.

    Args:
        db_dict: The loaded database as a dict (from load_yaml_as_dict)

    Returns:
        ValidationResult with all issues found
    """
    result = ValidationResult()
    lookup = build_signature_lookup(db_dict)

    # Get environment version for migration checks
    env_version = db_dict.get("Global", {}).get("Options", {}).get("Version", "")

    def apply_migrations(action_str: str) -> str:
        """Apply known migrations to an action string before validation."""
        if not action_str:
            return action_str
        # Apply PortalTo migration
        migrated, _ = migrate_old_portalto(action_str)
        # Apply PlayVideo migration
        migrated, _ = migrate_old_playvideo(migrated, env_version)
        return migrated

    def check_action(action: dict, context: dict):
        """Check action, condition, and trigger for a single action entry."""
        nonlocal result

        action_context = {**context, "action_id": str(action.get("Id", ""))}

        # Check Action (apply migrations first to validate post-migration state)
        action_str = apply_migrations(action.get("Action", ""))
        if action_str:
            result.total_actions_checked += 1
            issue = validate_signature(action_str, "action", lookup, action_context)
            if issue:
                result.issues.append(issue)

        # Check Condition
        condition_str = action.get("Condition", "")
        if condition_str:
            result.total_conditions_checked += 1
            issue = validate_signature(condition_str, "condition", lookup, action_context)
            if issue:
                result.issues.append(issue)

        # Check Trigger
        trigger_str = action.get("Trigger", "")
        if trigger_str:
            result.total_triggers_checked += 1
            issue = validate_signature(trigger_str, "trigger", lookup, action_context)
            if issue:
                result.issues.append(issue)

    # Check Global Actions
    for action in db_dict.get("Global", {}).get("GlobalActions", {}).values():
        check_action(action, {"context_type": "global"})

    # Check Pocket Actions
    for action in db_dict.get("Global", {}).get("PocketActions", {}).values():
        check_action(action, {"context_type": "pocket"})

    # Check View and Object Actions
    for view_id, view in db_dict.get("Views", {}).items():
        view_context = {
            "context_type": "view",
            "view_id": view_id,
            "view_name": view.get("Name", ""),
        }

        # View actions
        for action in view.get("Actions", {}).values():
            check_action(action, view_context)

        # Object actions
        for obj_id, obj in view.get("Objects", {}).items():
            obj_context = {
                "context_type": "object",
                "view_id": view_id,
                "view_name": view.get("Name", ""),
                "object_id": obj_id,
                "object_name": obj.get("Name", ""),
            }
            for action in obj.get("Actions", {}).values():
                check_action(action, obj_context)

    return result


def generate_html_report(result: ValidationResult) -> str:
    """
    Generate an HTML report from validation results.

    Returns:
        HTML string
    """
    # Group issues by type
    issues_by_type: dict[str, list[SignatureIssue]] = {}
    for issue in result.issues:
        key = issue.issue_type.value
        if key not in issues_by_type:
            issues_by_type[key] = []
        issues_by_type[key].append(issue)

    summary_class = "summary-ok" if not result.has_issues else "summary-error"
    summary_text = "No Issues Found" if not result.has_issues else f"{result.issue_count} Issue(s) Found"
    page_title = "Environment Validation Passed" if not result.has_issues else "Issues Were Found With Your Environment"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Environment Validation Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{ color: #333; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #4a90d9; margin-top: 30px; }}
        .summary {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .summary-ok {{ border-left: 4px solid #28a745; }}
        .summary-error {{ border-left: 4px solid #dc3545; }}
        .issue {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #dc3545;
        }}
        .issue-type {{
            font-weight: bold;
            color: #dc3545;
            text-transform: uppercase;
            font-size: 0.8em;
        }}
        .signature {{
            font-family: monospace;
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .context {{ color: #666; font-size: 0.9em; margin-top: 8px; }}
        .details {{
            margin-top: 10px;
            padding: 10px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4a90d9; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>{page_title}</h1>

    <div class="summary {summary_class}">
        <h3>{summary_text}</h3>
        <p>
            <strong>File:</strong> {result.yaml_file_path}<br>
            <strong>Actions checked:</strong> {result.total_actions_checked}<br>
            <strong>Conditions checked:</strong> {result.total_conditions_checked}<br>
            <strong>Triggers checked:</strong> {result.total_triggers_checked}
        </p>
    </div>
"""

    if result.has_issues:
        # Issue type descriptions
        type_titles = {
            "unknown_name": "Unknown Names",
            "param_count": "Parameter Count Mismatches",
            "parse_error": "Parse Errors",
        }

        for issue_type, issues in issues_by_type.items():
            html += f"""
    <h2>{type_titles.get(issue_type, issue_type)} ({len(issues)})</h2>
"""
            for issue in issues:
                context_parts = []
                if issue.context_type:
                    context_parts.append(f"Context: {issue.context_type}")
                if issue.view_name:
                    context_parts.append(f"View: {issue.view_id} ({issue.view_name})")
                elif issue.view_id:
                    context_parts.append(f"View ID: {issue.view_id}")
                if issue.object_name:
                    context_parts.append(f"Object: {issue.object_id} ({issue.object_name})")
                elif issue.object_id:
                    context_parts.append(f"Object ID: {issue.object_id}")
                if issue.action_id:
                    context_parts.append(f"Action ID: {issue.action_id}")
                context_str = " | ".join(context_parts)

                html += f"""
    <div class="issue">
        <span class="issue-type">{issue.signature_type}</span>
        <p><strong>{issue.message}</strong></p>
        <p>Value: <span class="signature">{issue.raw_string}</span></p>
        <p class="context">{context_str}</p>
"""
                if issue.issue_type == IssueType.PARAM_COUNT_MISMATCH:
                    html += f"""
        <div class="details">
            <strong>Expected template:</strong> {issue.expected_template}<br>
            <strong>Actual values:</strong> {issue.actual_values}
        </div>
"""
                html += "    </div>\n"

    html += """
</body>
</html>
"""
    return html


def show_validation_report(result: ValidationResult, tmp_folder: TemporaryDirectory) -> Path:
    """
    Save HTML report to temp folder and open in browser.

    Args:
        result: The validation result
        tmp_folder: TemporaryDirectory from GemsDB connection

    Returns:
        Path to the report file
    """
    html_content = generate_html_report(result)
    report_path = Path(tmp_folder.name, "signature_validation_report.html")
    report_path.write_text(html_content)

    webbrowser.open(str(report_path.absolute().as_uri()), autoraise=True)

    return report_path


def validate_and_report(
    db_dict: dict,
    yaml_file_path: str,
    tmp_folder: TemporaryDirectory,
    show_report: bool = True,
) -> ValidationResult:
    """
    Main entry point: validate database and optionally show report.

    Args:
        db_dict: The loaded database dict
        yaml_file_path: Path to the YAML file (for display in report)
        tmp_folder: TemporaryDirectory for saving report
        show_report: Whether to open browser with report

    Returns:
        ValidationResult
    """
    result = validate_database(db_dict)
    result.yaml_file_path = yaml_file_path

    if show_report and result.has_issues:
        show_validation_report(result, tmp_folder)

    return result
