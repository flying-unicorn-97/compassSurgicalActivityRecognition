import sys


def sum(a, b):
    return (a + b)


if __name__ == "__main__":
    a = sys.argv[1]
    b = sys.argv[2]
    print(sum(int(a), int(b)))