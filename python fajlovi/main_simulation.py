import random
import simpy
import zombie_apocalypse
# This library is for our multi-threading
import concurrent.futures
# evolutionary (genetic) algorithm for deciding how the government will get involved
import genetic
from functools import partial

# a - alpha value in model: "zombie destruction" rate
A = 0.005
# b - beta value in model: "new zombie" rate
B = 0.0095
# ze - zeta value in model: zombie resurrection rate
ZE = 0.0001
# d - delta value in model: background death rate (very generous number - random background deaths are much higher)
D = 0.0001
# ts - Simulation stopping time in days (for calculations), simulation will use minutes
TS = 10 # time is in days
# dt - time step for numerical solutions
DT = 0.001
# Close optimal values : a=0.005, b=0.0095, ze=0.0001, d=0.0001, ts=10, dt=0.001
# size of the population
NUM_HUMANS = 1000
NUM_ZOMBIES = 5


def government_action(env):
    global A, B
    # After 5 days, the government decision for implementing the policies on taking on the zombie infection
    # The government policies is implemented through a genetic algorithm
    yield env.timeout(5 * 86400)
    print("")
    print("This is the moment where the Government policy takes place")
    print("------------------------------------------------------------")
    population, generations = genetic.run_evolution(
        populate_func=partial(genetic.generate_population, size=100),
    )
    print(population)
    # Since the government policy decides on the best A, and B, through different methods, that is our return
    A = population[0][1]
    B = population[0][2]


def wake_up_zombies(env, num_humans, a, b, ze, d, ts, dt):
    # the zombies start attacking in somewhere between one and two days
    yield env.timeout((1 + random.random()) * 86400)
    while True:
        with start.humans.request() as request:
            yield request
            yield env.process(start.SIR_infectious_model(num_humans, a, b, ze, d, ts, dt))


def start_the_apocalypse():
    env.process(wake_up_zombies(env=env, num_humans=NUM_HUMANS, a=A, b=B, ze=ZE, d=D, ts=TS, dt=DT))


def start_government_processes():
    env.process(government_action(env))

# Run the simulation
env = simpy.Environment()
print("-----Running simulation-----")
start = zombie_apocalypse.ZombieApocalypse(env, NUM_HUMANS, NUM_ZOMBIES)

# We are setting up our pool of threads, with 2 threads
pool = concurrent.futures.ThreadPoolExecutor(max_workers=2)

# submit tasks to the pool
pool.submit(start_government_processes())
pool.submit(start_the_apocalypse)

# wait for all tasks to complete
pool.shutdown(wait=True)

# x86400 so it runs 10 days, since the default time is seconds
env.run(until=TS*86400)
