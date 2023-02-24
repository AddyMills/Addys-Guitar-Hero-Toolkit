from ska_classes import *

if __name__ == "__main__":
    with open("GHM_Singer_Male_One_1.ska.xen", 'rb') as f:
        ska_file = ska_bytes(f.read())

    print()