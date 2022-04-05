import math

import pandas as pd


class Job:

    def __init__(self, id):
        self.id = id
        self.tasks = []

    def __repr__(self):
        return f'Job(id={self.id}, tasks={self.tasks})'

    @staticmethod
    def read_from_excel(path, n_jobs=math.inf):
        jobs = {}
        excel = pd.read_excel(path, header=None)
        data = excel.values[2:]

        for i in range(data.shape[1]//2):
            if i >= n_jobs:
                break
            job = Job(i+1)
            job_cols = data[:, i*2:i*2+2]
            for task in job_cols:
                machine, time = task
                task = Task(job, machine, time)
                job.tasks.append(task)
            jobs[job.id] = job

        return jobs


class Task:

    def __init__(self, job, machine, time):
        self.job = job
        self.machine = machine
        self.time = time

    def __repr__(self):
        return f'{self.job_id}-{self.machine}({self.time})'

    @property
    def job_id(self):
        return self.job.id


class ScheduledTask:

    def __init__(self, *, start_time, end_time=None, task=None):
        self.start_time = start_time
        self.task = task
        self.end_time = end_time if end_time is not None else start_time + self.task.time

    def __repr__(self):
        return f'{self.start_time}-{self.end_time}|{self.task}'
