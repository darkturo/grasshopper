from dataclasses import dataclass
from datetime import datetime
from flask import Flask
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db
from sqlite3 import IntegrityError


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
        """ Create a new testrun, will raise an error if the testrun already exists """
        try:
            db = get_db()
            db.execute(
                "INSERT INTO testrun (user_id, name, description, threshold) VALUES (?, ?, ?, ?)",
                (user_id, name, description, threshold),
            )
            db.commit()
        except IntegrityError as e:
            raise TestRunAlreadyExistsError(e)

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
            "INSERT INTO cpu_usage (testrun_id, cpu_usage) VALUES (?, ?)",
            (self.id, cpu_usage),
        )
        db.commit()

    def has_passed_threshold(self):
        db = get_db()
        cpu_usage = db.execute(
            "SELECT MAX(usage) as max_usage FROM cpu_usage WHERE testrun_id = ? GROUP BY test_run_id",
            (self.id)
        ).fetchone()['max_usage']
        return cpu_usage > self.threshold

    def fetch_current_cpu_usage(self):
        db = get_db()
        usage_time_series = []
        for entry in db.execute(
            "SELECT cpu_usage, time FROM cpu_usage WHERE testrun_id = ? ORDER BY time DESC LIMIT 1",
            (self.id)
        ).fetchall():
            usage_time_series.append(CPUUsage(usage=entry['cpu_usage'],
                                              timestamp=entry['time'],
                                              testrun_id=self.id))

def calculate_total_time_overpassing_threshold(threshold, usage_time_series):
    total_time = 0
    for periods in zip(usage_time_series, usage_time_series[1:]):
        period_duration = (periods[1].timestamp - periods[0].timestamp).total_seconds()
        if periods[0].usage > threshold:
            total_time += period_duration
    return total_time


@dataclass
class CPUUsage:
    testrun_id: str
    timestamp: str
    usage: float
