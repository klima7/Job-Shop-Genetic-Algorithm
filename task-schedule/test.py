from models import Job
from genetic import JobShopGA

jobs = Job.read_from_excel('tasks.xlsx')
ga = JobShopGA(jobs)
solution = ga.solve()
print(solution)
