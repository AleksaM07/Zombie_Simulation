from random import choice, randint, randrange, random, choices
# the guide for creating this evolutionary algorithm suggested using type suggestion.
from typing import List, Optional, Callable, Tuple, Any
import numpy as np


# we use the same values as in our main function, we are also using latent infection here
# ze - zeta value in model: zombie resurrection rate
ZE = 0.0001
# d - delta value in model: background death rate (very generous number - random background deaths are much higher)
D = 0.0001
# ts - Simulation stopping time in days (for calculations), simulation will use minutes
TS = 10 # time is in days
# dt - time step for numerical solutions
DT = 0.001
# ro - the chance that the infected become a zombie
RO = 0.005
# Optimal values : a=0.005, b=0.0095, ze=0.0001, d=0.0001, ts=10, dt=0.001
# Weapon - A zombie is killed by a human depending upon weaponry and training ability
WEAPON = 0.1
# fi - he chance of them encountering zombies while at an advantage
FI = 0.0001
# gama - percentage of immunity to the virus
GAMA = 0.1
# α = ρφ -> quantifies human agression
A = WEAPON * FI
# δ(delta) - the aggressiveness of the zombies
DELTA = [A/2, A, 2*A, 3*A, 4*A, 5*A, 10*A] # different types of zombies
# ω(omega) - the chance that an encounter with a zombie will cause infection
OMEGA = 1
# b value used in other models is therefore the conjunction of these factors: \
B = (1 - GAMA) * float(choice(DELTA)) * OMEGA
# awareness of the human population
AWARE = 0.0001
VAX = 0.001
name = ""

# size of the population
NUM_HUMANS = 1000
NUM_ZOMBIES = 5

Genome = List[List[Any]]
Population = List[Genome]
PopulateFunc = Callable[[], Population]
FitnessFunc = Callable[[Genome], float]
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
MutationFunc = Callable[[Genome], Genome]
PrinterFunc = Callable[[Population, int, FitnessFunc], None]


def sizr_model(a, b, ro, d, ze, ts, dt):
    N = NUM_HUMANS
    Z = NUM_ZOMBIES
    n = int(ts / dt)
    s = np.zeros((n + 1,))
    z = np.zeros((n + 1,))
    r = np.zeros((n + 1,))
    i = np.zeros((n + 1,))
    s[0] = N
    z[0] = Z
    r[0] = 0
    i[0] = 0
    t = np.arange(0, ts + dt, dt)
    # Define the ODE’s of the model and solve numerically by Euler’s method:
    for j in np.arange(0, n):
        s[j + 1] = s[j] + dt * (- b * s[j] * z[j] - d * s[j] + d)  # here we assume birth rate = background deathrate, so
        i[j + 1] = i[j] + dt * (b * d * z[j] - ro * i[j] - d * i[j])
        z[j + 1] = z[j] + dt * (ro * i[j] - a * s[j] * z[j] + ze * r[j])
        r[j + 1] = r[j] + dt * (a * s[j] * z[j] + d * s[j] - ze * r[j] + d * i[j])
        if s[j + 1] + i[j + 1] == 0:
            break
    return s[-1], i[-1], z[-1], r[-1], z[-1] > s[-1], z[-1] < s[-1]


# this is a genetic representation of a solution. This is making an individual
def generate_genome() -> Genome:
    global OMEGA, AWARE, WEAPON, VAX, GAMA, NUM_HUMANS
    s, i, z, r, z_, s_ = sizr_model(A, B, RO, D, ZE, TS, DT)
    OMEGA = 1
    AWARE = 0.0001
    WEAPON = 0.1
    VAX = 0
    GAMA = 0.1
    NUM_HUMANS = 500

    def quarantine():
        global OMEGA, AWARE, name
        name = "Q"
        OMEGA = (2 * OMEGA + 0) / 3
        AWARE = (2 * AWARE + 0)/3

    def army():
        global WEAPON, AWARE, NUM_HUMANS, name
        name = "A"
        if random() < AWARE:
            WEAPON = (WEAPON + 1) / 2
        NUM_HUMANS = NUM_HUMANS + 100
        if z_:
            AWARE = (AWARE + 0)/2

    def kill():
        global OMEGA, WEAPON, name
        name = "K"
        WEAPON = (WEAPON + 1) / 2
        OMEGA = (2 * OMEGA + 1) / 3

    def warn():
        global WEAPON, AWARE, name
        name = "W"
        WEAPON = (3 * WEAPON + 1) / 4
        AWARE = (2*AWARE + 1)/3

    def fearmonger():
        global WEAPON, AWARE, name
        name = "F"
        WEAPON = (2 * WEAPON + 1) / 3
        AWARE = (3 * AWARE + 1)/4

    def science():
        global VAX, AWARE, name
        name = "S"
        if random() < AWARE:
            VAX = (VAX + 1)/2

    def vaccinate():
        global GAMA, AWARE, name
        name = "V"
        if random() < VAX:
            GAMA = (3 * GAMA + 1/4)
        if s_:
            AWARE = (AWARE + 0)/2

    list_of_solutions = []
    for i in range(10):
        list_of_functions = [quarantine, army, kill, warn, fearmonger, science, vaccinate]
        choice(list_of_functions)()
        list_of_solutions.append(name)

    a = WEAPON * FI
    b = (1 - GAMA) * float(choice(DELTA)) * OMEGA
    s, i, z, r, z_, s_ = sizr_model(a, b, RO, D, ZE, TS, DT)
    answer = [z + i, a, b, list_of_solutions]
    return answer


# A list of genomes. We call our generate_genomes multiple times until our population has a desirable length
# making a population
def generate_population(size: int) -> Population:
    return [generate_genome() for _ in range(size)]


# Fitness function to evalueate solutions.
def fitness(genome: Genome) -> float:
    return genome


# for calculating average fitness
def population_fitness(population: Population, fitness_func: FitnessFunc) -> int:
    return sum([fitness_func(genome[0]) for genome in population])


# sorting our list
def sort_population(population: Population, fitness_func: FitnessFunc) -> Population:
    return sorted(population, key=fitness_func, reverse=True)


# Selection pair, that will select parents for the new generation
def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    return choices(
        population=population,
        weights=[fitness_func(gene[0]) for gene in population],
        k=2
    )


# Crossover function
def single_point_crossover(parent1: Genome, parent2: Genome) -> Tuple[Genome, Genome]:
    # Selecting a random crossover point
    crossover_point = randint(0, len(parent1[3]))

    # Swap genetic material beyond the crossover point to create two offspring
    offspring1 = [parent1[0], parent1[1], parent1[2], parent1[3][:crossover_point] + parent2[3][crossover_point:]]
    offspring2 = [parent2[0], parent2[1], parent2[2], parent2[3][:crossover_point] + parent1[3][crossover_point:]]

    return offspring1, offspring2


# Mutation function
def mutation(genome: Genome, num: int = 9, probability: float = 0.5) -> Genome:
    for _ in range(num):
        index = randrange(len(genome[3])-1)
        genome[3][index] = genome[3][index] if random() > probability else choice(["Q", "A", "K", "W", "F", "S", "V"])
    return genome


def genome_to_string(genome: Genome) -> str:
    return "".join(map(str, genome))


def print_stats(population: Population, generation_id: int, fitness_func: FitnessFunc):
    print("GENERATION %02d" % generation_id)
    print("=============")
    print("Population: [%s]" % ", ".join([genome_to_string(gene) for gene in population]))
    print("Avg. Fitness: %f" % (population_fitness(population, fitness_func) / len(population)))
    sorted_population = sort_population(population, fitness_func)
    print("")

    return sorted_population[0]


def run_evolution(
        populate_func: PopulateFunc,
        fitness_func: FitnessFunc = fitness,
        selection_func: SelectionFunc = selection_pair,
        crossover_func: CrossoverFunc = single_point_crossover,
        mutation_func: MutationFunc = mutation,
        generation_limit: int = 100,
        printer: Optional[PrinterFunc] = print_stats) \
        -> Tuple[Population, int]:

    population = populate_func()
    for i in range(generation_limit):
        population = sorted(population, key=(lambda genome: fitness_func(genome[0])), reverse=False)

        if printer is not None:
            printer(population, i, fitness_func)

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation
        print(population)

    return population, i

