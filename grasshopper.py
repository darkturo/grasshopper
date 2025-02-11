#!/usr/bin/python3
import argparse

def TrackerClient:
    pass

def Runner:
    pass

def grasshopper():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grasshopper tracks the time of your tests')
    parser.add_argument('--jwt', type=str, help='The JWT token to authenticate with the API')
    parser.add_argument('--name', type=str, help='The name of the testrun.')
    parser.add_argument('--description', type=str, help='The description of the testrun.')
    parser.add_argument('--threshold', type=float, default=1, help='The threshold for the testrun.')
    parser.add_argument('--no-command', action='store_true', help='Run grasshopper to just listen for the cpu usage until is terminated.')
    parser.add_argument('command', nargs='*', help='The command to run after the testrun is finished.')

    args = parser.parse_args()

    tracker_client = TrackerClient(args.jwt)
    if args.no_command:
        runner = Runner()
    else:
        runner = Runner(args.command)

    grasshopper(tracker_client, runner, args.name, args.description, args.threshold)
