import os

from black import main

if __name__ == "__main__":
    print("Formatting...")
    try:
        print(main(["cogs", "main.py", "db"]))
    except:
        pass

    print("Sorting imports...")
    os.system("isort main.py cogs db --profile black")
