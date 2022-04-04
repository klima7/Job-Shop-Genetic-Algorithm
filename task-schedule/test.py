from models import Job
from genetic import JobShopProblem

jobs = Job.read_from_excel('tasks.xlsx')
problem = JobShopProblem(jobs)
solution = problem.solve()
print(solution)
