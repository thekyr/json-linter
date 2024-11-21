import json
import re

def detect_unbalanced_brackets_with_report(content):
    """
    Detect unbalanced brackets or braces in JSON content.
    Reports missing or extra brackets with line details.
    """
    stack = []  # Tracks unmatched opening brackets with line numbers
    reports = []  # Store error reports
    lines = content.splitlines()

    for i, line in enumerate(lines, start=1):
        for char in line:
            if char in "{[":
                stack.append((char, i))  # Push opening bracket and line number
            elif char in "}]":
                if stack and ((stack[-1][0] == "{" and char == "}") or (stack[-1][0] == "[" and char == "]")):
                    stack.pop()  # Match found, remove from stack
                else:
                    reports.append(f"Extra closing bracket '{char}' at line {i}.")

    # If stack is not empty, report missing closing brackets
    while stack:
        unmatched = stack.pop()
        reports.append(f"Missing closing bracket for '{unmatched[0]}' opened at line {unmatched[1]}.")
    return reports

def detect_missing_commas_with_report(lines):
    """
    Detect and add missing commas between JSON elements and report their locations.
    """
    corrected_lines = []
    reports = []  # Store details of missing commas
    for i in range(len(lines) - 1):
        current_line = lines[i].strip()
        next_line = lines[i + 1].strip()

        # If current line ends with `}` or `]` and next line starts with `"key":`, `{`, or `[`, a comma is missing
        if (current_line.endswith("}") or current_line.endswith("]")) and (
            next_line.startswith('"') or next_line.startswith("{") or next_line.startswith("[")
        ):
            corrected_lines.append(lines[i] + ",")  # Add missing comma
            reports.append(f"Missing comma ',' at line {i + 1}.")
        else:
            corrected_lines.append(lines[i])

    # Add the last line
    corrected_lines.append(lines[-1])
    return corrected_lines, reports

def remove_trailing_commas(content):
    """Remove trailing commas in objects and arrays."""
    return re.sub(r",\s*([\]}])", r"\1", content)

def fix_unbalanced_brackets(content):
    """Fix unbalanced brackets by adding missing closing braces."""
    unbalanced_message = detect_unbalanced_brackets_with_report(content)
    if unbalanced_message:
        print("\n".join(unbalanced_message))

    open_braces = 0
    corrected_lines = []
    for line in content.splitlines():
        open_braces += line.count("{") - line.count("}")
        corrected_lines.append(line)

    # Add missing closing braces
    while open_braces > 0:
        corrected_lines.append(" " * (open_braces - 1) * 4 + "}")
        open_braces -= 1

    return "\n".join(corrected_lines)

def reformat_json(content):
    """Reformat the JSON content to ensure consistent indentation."""
    try:
        data = json.loads(content)
        return json.dumps(data, indent=4)  # Proper indentation
    except json.JSONDecodeError as e:
        raise e

def json_linter_and_fixer(file_path):
    """
    Validate and fix JSON, reporting detailed errors for:
    - Missing or unbalanced brackets
    - Missing commas
    - Trailing commas
    - Proper indentation
    """
    def apply_fixes(content):
        """Apply fixes for trailing commas, unbalanced brackets, and missing commas."""
        fixed = False
        reports = []

        # Remove trailing commas
        content_no_commas = remove_trailing_commas(content)
        if content_no_commas != content:
            fixed = True
        content = content_no_commas

        # Fix unbalanced brackets/braces
        unbalanced_reports = detect_unbalanced_brackets_with_report(content)
        if unbalanced_reports:
            reports.extend(unbalanced_reports)
        content_balanced = fix_unbalanced_brackets(content)
        if content_balanced != content:
            fixed = True
        content = content_balanced

        # Detect and fix missing commas
        lines = content.splitlines()
        corrected_lines, comma_reports = detect_missing_commas_with_report(lines)
        if corrected_lines != lines:
            fixed = True
        reports.extend(comma_reports)
        content = "\n".join(corrected_lines)

        return content, fixed, reports

    try:
        with open(file_path, "r") as file:
            content = file.read()

        original_content = content  # Store original content for comparison
        max_attempts = 10
        attempt = 0

        while attempt < max_attempts:
            try:
                # Validate JSON
                json.loads(content)
                formatted_content = reformat_json(content)  # Ensure proper indentation
                if formatted_content == original_content:
                    print("JSON is already valid and properly formatted. No changes were needed.")
                    return "No file saved; JSON is already valid and properly formatted."

                corrected_path = file_path.replace(".json", "_corrected.json")
                # Compare with last saved content to avoid redundancy
                try:
                    with open(corrected_path, "r") as corrected_file:
                        saved_content = corrected_file.read()
                        if formatted_content == saved_content:
                            print("No further changes; skipping save.")
                            return "No further fixes were necessary."
                except FileNotFoundError:
                    pass  # No previous file, proceed to save

                with open(corrected_path, "w") as corrected_file:
                    corrected_file.write(formatted_content)
                print(f"JSON fixed and saved to: {corrected_path}")
                return "Fix successful."
            except json.JSONDecodeError as e:
                content, fixed, reports = apply_fixes(content)
                if not fixed:
                    for report in reports:
                        print(report)
                    raise ValueError("No further fixes could be applied.")
            attempt += 1

        raise ValueError("Reached maximum attempts to fix the JSON.")
    except FileNotFoundError:
        return "File not found. Please provide a valid path."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# Example Usage
if __name__ == "__main__":
    file_path = input("Enter the path to the JSON file: ")
    result = json_linter_and_fixer(file_path)
    print(result)
