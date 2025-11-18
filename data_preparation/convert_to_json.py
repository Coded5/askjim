import os
from dotenv import load_dotenv, find_dotenv

def main():

    root = find_dotenv()
    scopus_dir = os.path.join(os.path.dirname(root), os.getenv("SCOPUS_DATA_PATH", ""))

    #Rename every file to end with .json
    for dir in os.listdir(scopus_dir):
        dir_path = os.path.join(scopus_dir, dir)
        for filename in os.listdir(dir_path):
            print(f"Processing file: {filename}")
            if not filename.endswith(".json"):
                base, _ = os.path.splitext(filename)
                new_filename = base + ".json"
                os.rename(
                    os.path.join(dir_path, filename),
                    os.path.join(dir_path, new_filename)
                )
    

if __name__ == '__main__':
    load_dotenv()
    main()
