import os
import json
import argparse

parser = argparse.ArgumentParser(description='Parse metha OAI XML files and insert metadata into SQLite database')

parser.add_argument('search_path', help='set folder to search')
parser.add_argument('output_file', help="name of output file (JSON)")

global args
args = parser.parse_args()

starting_folder = args.search_path

# dump_file = "tex_list_all.json"
dump_file = args.output_file

tex_counter = 0
num_dirs = 0
texs= []
error_count = 0

for root, dirs, files in os.walk(starting_folder):
    try:
        for name in files:
    #         print(os.path.join(root, name))
            if ".tex" in name:
    #             and name != "bibliography.tex"
                print(name)
                tex_counter += 1
                texs.append(os.path.join(root, name))
        for name in dirs:
            print("--- " + os.path.join(root, name))
        num_dirs += 1
    except UnicodeDecodeError as error:
        print("***** decode error!",error)
        error_count += 1
    except:
        print("***** general error")
        error_count += 1

with open(dump_file, "w") as f:
    json.dump(texs, f)

print("*" * 20)
print("tex_counter:",tex_counter)
print("num_dirs:",num_dirs)
print("error_count:",error_count)
