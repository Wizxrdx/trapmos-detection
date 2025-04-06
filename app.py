import argparse
from src.detection import run_detection


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-dev", action="store_true", help="Run in development mode")
    args = parser.parse_args()

    print("Running in development mode..." if args.dev else "Running in normal mode...")
    run_detection(args.dev)

if __name__ == "__main__":
    main()
