import os
import re


def count_real_variables(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            # Look for declarations of Real variables
            matches = re.findall(
                r'\(declare-fun\s+\w+\s*\(\s*\)\s*Real\)', content)
            return len(matches)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0


def main():
    # Get all .smt2 files in current directory
    smt2_files = [f for f in os.listdir('.') if f.endswith('.smt2')]

    # Create list of (filename, count) tuples
    results = []
    for file_name in smt2_files:
        count = count_real_variables(file_name)
        results.append((file_name, count))

    # Sort by count in ascending order
    results.sort(key=lambda x: x[1])

    # Print results
    for file_name, count in results:
        print(f"{file_name}: {count} Real variables")


if __name__ == "__main__":
    main()
