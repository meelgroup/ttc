import argparse
import os
import re


def replace_in_file(file_path):
  with open(file_path, 'r') as file:
    content = file.read()

  int_to_real_count = len(re.findall(r'Int', content))
  qf_lia_to_qf_lra_count = len(re.findall(r'QF_LIA', content))

  content = content.replace('Int', 'Real')
  content = content.replace('QF_LIA', 'QF_LRA')

  with open(file_path, 'w') as file:
    file.write(content)

  return int_to_real_count, qf_lia_to_qf_lra_count


def process_files(file_paths):
  total_int_to_real = 0
  total_qf_lia_to_qf_lra = 0

  for file_path in file_paths:
    int_to_real_count, qf_lia_to_qf_lra_count = replace_in_file(file_path)
    total_int_to_real += int_to_real_count
    total_qf_lia_to_qf_lra += qf_lia_to_qf_lra_count
    print(f"Processed file: {file_path}")
    print(f"Replaced 'Int)' with 'Real)': {int_to_real_count} times")
    print(f"Replaced 'QF_LIA' with 'QF_LRA': {qf_lia_to_qf_lra_count} times")

  print(f"Total 'Int)' to 'Real)' replacements: {total_int_to_real}")
  print(f"Total 'QF_LIA' to 'QF_LRA' replacements: {total_qf_lia_to_qf_lra}")


def main():
  parser = argparse.ArgumentParser(
      description="Replace 'Int)' with 'Real)' and 'QF_LIA' with 'QF_LRA' in files.")
  parser.add_argument('file', nargs='?', help="The file to process")
  parser.add_argument('--folder', action='store_true',
                      help="Process all .smt2 files in the current directory")

  args = parser.parse_args()

  if args.folder:
    file_paths = [f for f in os.listdir('.') if f.endswith('.smt2')]
  elif args.file:
    file_paths = [args.file]
  else:
    print("Please provide a file or use --folder option.")
    return

  process_files(file_paths)


if __name__ == "__main__":
  main()
