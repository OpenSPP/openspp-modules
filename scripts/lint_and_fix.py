import subprocess
import os

def run_linting():
    """Run the linting command and return the output."""
    result = subprocess.run(['pre-commit', 'run', 'pylint_odoo', '--all-files'], capture_output=True, text=True)
    return result.stdout

def parse_linting_output(output):
    """Parse the linting output to get a list of files with issues."""
    files_with_issues = set()
    for line in output.splitlines():
        if '************* Module' in line:
            file_path = line.split()[-1].replace('.', '/') + '.py'
            files_with_issues.add(file_path)
    return list(files_with_issues)

def fix_file_with_aider(file_path):
    """Use Aider to fix the file."""
    subprocess.run(['aider', file_path])

def main():
    linting_output = run_linting()
    files_with_issues = parse_linting_output(linting_output)
    
    for file_path in files_with_issues:
        fix_file_with_aider(file_path)

if __name__ == "__main__":
    main()
