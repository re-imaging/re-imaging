import os
import json

# starting_folder = "/home/rte/arXiv/src_all/1001/"
starting_folder = "/home/rte/arXiv/src_all/"
# starting_folder = "/home/rte/arXiv/src_all/1506"
dump_file = "tex_list_all.json"

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
