import subprocess
import os

def run_linting():
    """Run the linting command and return the output."""
    result = subprocess.run(['pre-commit', 'run', 'pylint_odoo', '--all-files'], capture_output=True, text=True)
    return result.stdout

def parse_linting_output(output):
    """Parse the linting output to get a dictionary of files with issues and their errors."""
    files_with_issues = {}
    for line in output.splitlines():
        if line.startswith('************* Module'):
            continue
        if ':' in line:
            file_path = line.split(':')[0]
            if file_path not in files_with_issues:
                files_with_issues[file_path] = []
            files_with_issues[file_path].append(line)
    return files_with_issues

def fix_file_with_aider(file_path, errors):
    """Use Aider to fix the file with the provided errors."""
    error_instructions = "\n".join(errors)
    subprocess.run(['aider', file_path, '--message', error_instructions])

def main():
    linting_output = run_linting()
    files_with_issues = parse_linting_output(linting_output)
    
    for file_path in files_with_issues:
        fix_file_with_aider(file_path, files_with_issues[file_path])

if __name__ == "__main__":
    main()
