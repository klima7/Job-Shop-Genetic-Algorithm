class Job:

    def __init__(self, id):
        self.id = id
        self.tasks = []

    def __repr__(self):
        return f'Job(id={self.id}, tasks={self.tasks})'


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
