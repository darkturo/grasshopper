from dataclasses import dataclass
from datetime import datetime
from sqlite3 import IntegrityError
from uuid import uuid4

from .db import get_db


class TestRunAlreadyExistsError(Exception):
    pass


@dataclass
class TestRun:
    id: str
    user_id: str
    name: str
    description: str
    threshold: float = 0.0
    start_time: str = None
    end_time: str = None

    @staticmethod
    def create(user_id, name, description, threshold):
        """
        Create a new testrun.
        Raise an error if the testrun already exists
        """
        try:
            db = get_db()
            id = uuid4().bytes
            db.execute(
                '''
                INSERT INTO
                    test_run (id, user_id, name, description, threshold)
                VALUES (?, ?, ?, ?, ?)
                ''',
                (id, user_id, name, description, threshold),
            )
            db.commit()
            res = db.execute('''
                SELECT id, start_time FROM
                    test_run
                WHERE id = ?
                ''', (id)).fetchone()
        except IntegrityError as e:
            raise TestRunAlreadyExistsError(e)
        return {'id': res['id'], 'start_time': res['start_time']}

    @property
    def is_active(self):
        return self.start_time is not None and self.end_time is None

    @property
    def started_at(self):
        return datetime.fromisoformat(self.start_time)

    @property
    def ended_at(self):
        if self.end_time is None:
            return None
        return datetime.fromisoformat(self.end_time)

    @property
    def duration(self):
        if self.end_time is None:
            ended_at = datetime.now()
        else:
            ended_at = self.ended_at
        return (ended_at - self.started_at).total_seconds()

    def finish(self):
        db = get_db()
        self.end_time = datetime.now().isoformat()
        db.execute(
            "UPDATE testrun SET end_time = ? WHERE id = ?",
            (self.end_time, self.id),
        )
        db.commit()

    def record_cpu_usage(self, cpu_usage):
        db = get_db()
        db.execute(
            '''
            INSERT INTO
                cpu_usage (id, testrun_id, cpu_usage)
            VALUES (?, ?, ?)
            ''',
            (uuid4().bytes, self.id, cpu_usage),
        )
        db.commit()

    def has_passed_threshold(self):
        db = get_db()
        cpu_usage = db.execute(
            '''
            SELECT MAX(usage) as max_usage FROM
                cpu_usage
            WHERE testrun_id = ?
            GROUP BY test_run_id
            ''', (self.id)).fetchone()['max_usage']
        return cpu_usage > self.threshold

    def fetch_current_cpu_usage(self):
        db = get_db()
        usage_time_series = []
        for entry in db.execute(
                '''
                SELECT cpu_usage, time FROM
                    cpu_usage
                WHERE testrun_id = ?
                ORDER BY time DESC LIMIT 1
                ''', (self.id)).fetchall():
            usage_time_series.append(CPUUsage(usage=entry['cpu_usage'],
                                              timestamp=entry['time'],
                                              testrun_id=self.id))

    def get_test_execution_stats(self):
        time_series = self.fetch_current_cpu_usage()
        total_time = 0

        for periods in zip(time_series, time_series[1:]):
            period_duration = (periods[1].timestamp -
                               periods[0].timestamp).total_seconds()
            if periods[0].usage > self.threshold:
                total_time += period_duration
        return {
            'measurements': len(time_series),
            'time_above_threshold': total_time,
            'total_time': self.duration,
        }


@dataclass
class CPUUsage:
    testrun_id: str
    timestamp: str
    usage: float
