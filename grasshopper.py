#!/usr/bin/python3
import argparse
import asyncio
import os
from collections import namedtuple
import psutil
import requests
from signal import SIGINT, SIGTERM, signal
import warnings

BASE_PATH = '/v1/api/testrun'


class TrackerClient:

    def __init__(self, jwt, server_url):
        self.jwt = jwt
        self.tracker_url = f"{server_url}"
        self.test_run_id = None

        if not self.jwt:
            raise Exception('No JWT token provided')

        try:
            requests.head(f'{self.tracker_url}{BASE_PATH}', timeout=1)
        except requests.exceptions.ConnectionError:
            raise Exception(f'Tracker unreachable {self.tracker_url}')

    def create_testrun(self, name, description, threshold):
        r = requests.post(f'{self.tracker_url}{BASE_PATH}', json={
            'name': name,
            'description': description,
            'threshold': threshold
        }, headers={'Authorization': f'Bearer {self.jwt}'})

        if r.status_code != 201:
            raise Exception(f'Error creating testrun: {r.text}')

        self.test_run_id = r.json().get('id')
        return namedtuple('TestRun',
                          ['id', 'start_time'])(self.test_run_id,
                                                r.json().get('start_time'))

    def record_usage(self, usage):
        r = requests.post(
            f'{self.tracker_url}{BASE_PATH}/{self.test_run_id}/usage',
            json={'usage': usage},
            headers={'Authorization': f'Bearer {self.jwt}'})

        if r.status_code != 201:
            warnings.warn(f'Could not report usage: {r.text}')

    def stop_testrun(self):
        stop_url = f'{self.tracker_url}{BASE_PATH}/{self.test_run_id}/stop'
        r = requests.post(stop_url,
                          headers={'Authorization': f'Bearer {self.jwt}'})
        if r.status_code != 200:
            warnings.warn(f'Could not stop testrun: {r.text}')

    def get_testrun_stats(self):
        r = requests.get(f'{self.tracker_url}{BASE_PATH}/{self.test_run_id}',
                         headers={'Authorization': f'Bearer {self.jwt}'})
        if r.status_code != 200:
            warnings.warn(f'Could not get testrun stats: {r.text}')
        print(f"GOT STATS: {r.text}")
        return r.json()


class Runner:
    def __init__(self, tracker_client, command=None, poll_interval=0.5):
        self.tracker_client = tracker_client
        self.command = command
        self.poll_interval = poll_interval
        self.runner = None
        self.reporter = None
        self.testrun_id = None

    def terminate_runner(self, signum, frame):
        if self.reporter:
            self.reporter.cancel()

    async def report_cpu_usage(self):
        if self.testrun_id:
            while True:
                print("REPORTING USAGE")
                usage = psutil.cpu_percent()
                print(f"CPU usage: {usage}")
                await asyncio.sleep(self.poll_interval)
        else:
            print("No testrun id set, can't report usage")

    def run_command(self):
        signal(SIGINT, self.terminate_runner)
        signal(SIGTERM, self.terminate_runner)
        if self.command:
            os.system(" ".join(self.command))

    async def run(self, testrun_id):
        self.testrun_id = testrun_id
        try:
            self.reporter = asyncio.create_task(self.report_cpu_usage())
            print("START REPORTER")

            self.runner = asyncio.create_task(asyncio.to_thread(self.run_command))
            print("START COMMAND")

            await asyncio.wait([self.runner, self.reporter])
            print("NOT YET... WHAT HAPPENED?")
        except asyncio.CancelledError:
            print("User close tasks")


async def grasshopper(tracker, runner, name, description, threshold):
    testrun = tracker.create_testrun(name, description, threshold)

    print(f"Testrun starts with id: {testrun.id} at {testrun.start_time}")

    await runner.run(testrun.id)

    tracker.stop_testrun()

    stats = tracker.get_testrun_stats()
    print(stats)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
                        Grasshopper tracks the cpu usage of your tests
                        suites, programs, or any other command you want
                        to run and measure its cpu usage.
    ''')
    parser.add_argument('--jwt', type=str,
                        help='The JWT token to authenticate with the API')
    parser.add_argument('--name', type=str, help='The name of the testrun.')
    parser.add_argument('--description', type=str,
                        help='The description of the testrun.')
    parser.add_argument('--threshold', type=float, default=1,
                        help='The threshold for the testrun.')
    parser.add_argument('--poll-interval', type=float, default=0.5,
                        help='The interval in seconds to poll the CPU usage.')
    parser.add_argument('--server', type=str, default='http://127.0.0.1:5000',
                        help='The URL of the server to connect to.')
    parser.add_argument('--no-command', action='store_true',
                        help='Run grasshopper to just listen for the cpu '
                             'usage until is terminated.')
    parser.add_argument('--debug', action='store_true',
                        help='Run grasshopper in debug mode.')
    parser.add_argument('command', nargs='*',
                        help='The command to execute and measure.')

    args = parser.parse_args()

    if args.no_command and args.command:
        print("The --no-command flag cannot be used with a command")
        exit(1)
    elif not args.no_command and not args.command:
        print("Specify a command to run or use the --no-command flag to "
              "just listen for the CPU usage.")
        exit(1)
    if args.no_command:
        args.command = 'read -p waiting...'

    if args.name is None:
        if not args.no_command and args.command:
            args.name = args.command[0]
            if not args.description:
                args.description = " ".join(args.command[1:])
        else:
            args.name = "Unnamed testrun"
            if args.description is None:
                args.description = "No description"

    try:
        tracker_client = TrackerClient(args.jwt, args.server)
        runner = Runner(tracker_client, args.command)

        asyncio.get_event_loop().run_until_complete(
            grasshopper(tracker_client,
                        runner,
                        args.name,
                        args.description,
                        args.threshold)
        )
    except Exception as e:
        if args.debug:
            raise e
        else:
            print(f"An error occurred: {e}")
        exit(1)
