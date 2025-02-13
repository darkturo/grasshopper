from dataclasses import dataclass
from datetime import datetime
from sqlite3 import IntegrityError
from uuid import uuid4

from .db import get_db


class TestRunAlreadyExistsError(Exception):
    pass

def calculate_duration(start_time, end_time):
    """
    Take two timestamps and return the duration in seconds
    """
    return (end_time - start_time).seconds / 1000

@dataclass
class TestRun:
    id: int
    user_id: int
    name: str
    description: str
    threshold: float = 0.0
    start_time: str = None
    end_time: str = None

    @staticmethod
    def find_by_id(testrun_id):
        db = get_db()
        testrun = db.execute(
            '''
            SELECT * FROM test_run WHERE id = ?
            ''',
            (testrun_id,),
        ).fetchone()
        if testrun is None:
            return None
        return TestRun(id=testrun['id'],
                       user_id=testrun['user_id'],
                       name=testrun['name'],
                       description=testrun['description'],
                       threshold=testrun['threshold'],
                       start_time=testrun['start_time'],
                       end_time=testrun['end_time'])

    @staticmethod
    def create(user_id, name, description, threshold):
        """
        Create a new testrun.
        Raise an error if the testrun already exists
        """
        try:
            db = get_db()
            db.execute(
                '''
                INSERT INTO
                    test_run (user_id, name, description, threshold)
                VALUES (?, ?, ?, ?);
                ''',
                (user_id, name, description, threshold),
            ).fetchone()
            id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            start_time = db.execute('SELECT start_time FROM test_run WHERE id = ?', (id,)).fetchone()[0]
            db.commit()
        except IntegrityError as e:
            raise TestRunAlreadyExistsError(e)
        return {'id': id, 'start_time': start_time}

    @property
    def is_active(self):
        return self.start_time is not None and self.end_time is None

    @property
    def started_at(self):
        return self.start_time

    @property
    def ended_at(self):
        if self.end_time is None:
            return None
        return self.end_time

    @property
    def duration(self):
        if self.end_time is None:
            ended_at = datetime.now()
        else:
            ended_at = self.ended_at
        return calculate_duration(self.started_at, self.ended_at)

    def finish(self):
        db = get_db()
        self.end_time = datetime.now().isoformat()
        db.execute(
            "UPDATE test_run SET end_time = ? WHERE id = ?",
            (self.end_time, self.id),
        )
        db.commit()

    def record_cpu_usage(self, cpu_usage):
        db = get_db()
        db.execute(
            '''
            INSERT INTO
                cpu_usage (test_run_id, usage)
            VALUES (?, ?)
            ''',
            (self.id, cpu_usage),
        )
        db.commit()

    def has_passed_threshold(self):
        db = get_db()
        cpu_usage = db.execute(
            '''
            SELECT MAX(usage) as max_usage FROM
                cpu_usage
            WHERE test_run_id = ?
            GROUP BY test_run_id
            ''', (self.id,)).fetchone()['max_usage']
        return cpu_usage > self.threshold

    def fetch_current_cpu_usage(self):
        db = get_db()
        usage_time_series = []

        for entry in db.execute(
                '''
                SELECT * FROM
                    cpu_usage
                WHERE test_run_id = ?
                ORDER BY time DESC
                ''', (self.id,)).fetchall():
            usage_time_series.append(CPUUsage(id=entry['id'],
                                              testrun_id=entry['test_run_id'],
                                              usage=entry['usage'],
                                              timestamp=entry['time']))
        return usage_time_series

    def get_test_execution_stats(self):
        time_series = self.fetch_current_cpu_usage()
        total_time = 0
        if not time_series:
            raise ValueError("No CPU usage data found")

        for periods in zip(time_series, time_series[1:]):
            period_duration = calculate_duration(periods[0].timestamp, periods[1].timestamp)
            if periods[0].usage > self.threshold:
                total_time += period_duration
        return {
            'measurements': len(time_series),
            'time_above_threshold': total_time,
            'total_time': self.duration,
        }


@dataclass
class CPUUsage:
    id: int
    testrun_id: int
    timestamp: str
    usage: float
