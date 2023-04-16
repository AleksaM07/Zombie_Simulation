import numpy as np
# The matplotlib is not used because it slows down the process, but we have some useful graphs for demonstration
import matplotlib.pyplot as plt
import simpy
import pandas as pd
# For our fuzzy decision-making, instead of calculating manually, we import the library, which has
# "Mamadani minimum interference system" for fuzzification of the decision-making of our humans,
# and The Centre-of-Area (CoA) method or the Centre-of-Gravity method for defuzzication
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from sys import exit


class ZombieApocalypse():
    def __init__(self, env, num_humans, num_zombies):
        self.env = env
        self.end_event = env.event()
        self.num_humans = num_humans
        self.humans = simpy.Resource(env, self.num_humans)
        self.s = []
        self.z = []
        self.r = []
        self.t = []
        self.warning = []
        self.s.append(num_humans)
        self.z.append(num_zombies)
        self.r.append(0)
        # We use this indicator for displaying the warning level less times
        self.indicator = 0
        # We're writing everything down for our animation later
        self.result_df = pd.DataFrame(columns=['Time', 'Number of Humans', 'Number of Zombies', 'Alert Level'])
        # these are for the latent infection model
        # self.i = []
        # self.i.append(0)

    def SIR_infectious_model(self, num_humans, a, b, ze, d, ts, dt):
        """
        This function will solve the system of ODE’s for the basic model
        It will then plot the curve of the zombie population based on time.
        time is calcualted in days
        """
        t = np.arange(0, ts + dt, dt)

        # Our ordinary diferential Zombie equations
        self.s.append(self.s[-1] + dt * (- b * self.s[-1] * self.z[-1] - d * self.s[-1] + d))  # here we assume birth rate = background deathrate, so
        self.z.append(self.z[-1] + dt * (b * self.s[-1] * self.z[-1] - a * self.s[-1] * self.z[-1] + ze * self.r[-1]))
        self.r.append(self.r[-1] + dt * (a * self.s[-1] * self.z[-1] + d * self.s[-1] - ze * self.r[-1]))
        self.num_humans = round(self.s[-1])
        """
        In case of i - latent infection, we didn't use this approach because it requires quite a bit of computer power
        # ro - the chance that the infected become a zombie # RO = 0.005
        # self.i.append(self.i[-1] + dt * (b * self.s[-1] * self.z[-1] - ro * self.i[-1] - d * self.i[-1]))
        # self.z.append(self.z[-1] + dt * (ro * self.i[-1] - a * self.s[-1] * self.z[-1] + ze * self.r[-1]))
        # self.r.append(self.r[-1] + dt * (a * self.s[-1] * self.z[-1] + d * self.s[-1] + d * self.i[-1] - ze * self.r[-1]))

        Our function includes error checking to ensure that the solution remains
        within the bounds of the problem. If any of the bounds are violated,
        the function breaks out of the loop to prevent further computation.
        """
        if round(self.s[-1]) <= 0 or round(self.s[-1]) > num_humans:
            # we can use matplot lib to figure out if our math is correct.
            '''
            plt.plot(t[0:np.shape(self.s)], self.s, label="Humans")
            plt.plot(t[0:np.shape(self.z)], self.z, label="Zombies")
            plt.legend(['Susceptibles', 'Zombies'])
            plt.show()
            '''

            for i in range(len(self.s)):
                # We use num_of_change to decide  if the system changed during time, if it did, we display a message
                try: num_of_change = round(self.s[i]) - round(self.s[i + 1])
                except IndexError: num_of_change = round(self.s[i-1]) - round(self.s[i])
                # When we have a big enough set, we can calculate our fuzzy values
                # y is the return of our fuzzy_decision_making function, and it goes from 30 to 100
                try: y = self.fuzzy_decision_making(num_humans, current_num_humans=self.s[i], current_num_zombies=self.z[i])
                except ValueError: y = 100
                if y < 50: # this is the bound for the "no warning" level of warning
                    self.warning.append('No Warning')
                    if self.indicator < 50:
                        print("\nThe warning level doesn't exist yet\n----------------------------")
                        self.indicator = 60
                    else: self.indicator -= 0.1
                    if num_of_change >= 1:
                        yield self.env.timeout((t[i] - t[i - 1]) * 86400)
                        print(f"{round(self.s[i])} Humans are left. At the hour {round(self.env.now / 3600)}, "
                              f"day {round((self.env.now) / (86400))} of apocalypse\n"
                              f"There is currently {round(self.z[i])} zombies")
                    self.t.append(self.env.now)
                elif 50 <= y < 70:
                    self.warning.append('Alert')
                    if self.indicator < 60:
                        print("\nThe warning level is ALARM\n-----------------------\n")
                        self.indicator = 70
                    else: self.indicator -= 1
                    yield self.env.timeout((t[i] - t[i - 1]) * 86400 * 2)
                    print(f"{round(self.s[i])} Humans are left. At the hour {round(self.env.now / 3600)}, "
                          f"day {round((self.env.now) / (86400))} of apocalypse\n"
                          f"There is currently {round(self.z[i])} zombies")
                    self.t.append(self.env.now)
                elif 70 <= y < 80:
                    self.warning.append('Caution')
                    if self.indicator < 80:
                        print("\nThe warning level is CAUTION\n-----------------------\n")
                        self.indicator = 90
                    else: self.indicator -= 1
                    yield self.env.timeout((t[i] - t[i - 1]) * 86400 * 4)
                    print(f"{round(self.s[i])} Humans are left. At the hour {round(self.env.now / 3600)}, "
                          f"day {round((self.env.now) / (86400))} of apocalypse\n"
                          f"There is currently {round(self.z[i])} zombies")
                    self.t.append(self.env.now)
                elif 90 <= y <= 100:
                    if self.indicator < 100:
                        self.warning.append('Critical')
                        print("\nThe warning level is CRITICAL\n-----------------------\n")
                        self.indicator = 110
                    else: self.indicator -= 1
                    yield self.env.timeout((t[i] - t[i - 1]) * 86400 * 6)
                    print(f"{round(self.s[i])} Humans are left. At the hour {round(self.env.now / 3600)}, "
                          f"day {round((self.env.now) / (86400))} of apocalypse\n"
                          f"There is currently {round(self.z[i])} zombies")
                    self.t.append(self.env.now)

            # Write the results into a csv file
            self.result_df['Time'] = self.t
            self.result_df['Number of Humans'] = self.s
            self.result_df['Number of Zombies'] = self.z
            self.result_df['Alert Level'] = self.warning
            self.result_df.to_csv('output.csv')

            exit()
        elif round(self.z[-1]) < 0 or round(self.z[-1]) > num_humans:
            exit()
        elif round(self.r[-1]) < 0 or round(self.r[-1]) > num_humans:
            exit()

        # This check is for if we used latent infection
        # elif round(self.i[-1]) < 0 or round(self.i[-1]) > num_humans:
        #     self.end_event.succeed()

    def fuzzy_decision_making(self, num_humans, current_num_humans, current_num_zombies):
        """
        Fuzzy Control Systems: The Warning Level of the Zombie Infected
        ==========================================
        We formulate this problem as:
        * Antecedents (Inputs)
           - `x1`
              * Universe (ie, crisp value range): The number of infected individuals
              * Fuzzy set (ie, fuzzy value range): low, average, high
           - 'x2' - The number of uninfected individuals
           - `x1 - x2`
              * Universe: The number of infected minus the number of uninfected individuals
              * Fuzzy set: low, average, high
        * Consequences (Outputs)
           - `Warning`
              * Universe: The level of alarm, on a scale of 1 to 10
              * Fuzzy set: alarm, caution, critical
        * Rules
           - ALARM - The number of infected individuals is greater than a specified amount α1, the ‘unsafe’ level.
           - CAUTION - The number of infected individuals is unsafe and the number of infected individuals is greater
           than the number of uninfected individuals by a specified amount α2, but does not outnumber uninfected individuals by a specified amount α3.
           - CRITICAL -The number of infected individuals is unsafe and the number of
           infected individuals outnumbers uninfected individuals by a specified amount α3.

        First, let's define fuzzy variables
        """

        # New Antecedent/Consequent objects hold universe variables and membership functions
        x1 = np.array(self.z)
        x2 = np.array(self.s)
        infected = ctrl.Antecedent(x1, 'infected')
        uninfected = ctrl.Antecedent(np.subtract(x1, x2), 'uninfected')
        warning = ctrl.Consequent(np.arange(0, 101, 1), 'warning')

        a1 = num_humans / 5  # the unsafe level of zombies
        # the number of infected individuals is greater by a2 than the number of uninfected individuals
        a2 = num_humans / 10
        a3 = num_humans / 5  # the number of infected individuals outnumbers uninfected individuals by a3

        # Trapezoidal membership function generator for NUM of humans
        infected['low'] = fuzz.trapmf(infected.universe, [0, 0, 4, 40])
        infected['average'] = fuzz.trapmf(infected.universe, [0.1*a1, 0.3*a1, a1, a1])
        infected['high'] = fuzz.trapmf(infected.universe, [x1[-1]/4, x1[-1]/2, x1[-40], x1[-1]])
        uninfected['low'] = fuzz.trapmf(uninfected.universe, [-x2[1], -x2[50], a3-a3*0.3, a3])
        uninfected['average'] = fuzz.trapmf(uninfected.universe, [a2, a3-a3*0.3, a3+a3*0.3, a3+70])
        uninfected['high'] = fuzz.trapmf(uninfected.universe, [a3, a3+a3*0.3, x1[-1]/1.7, x1[-1]])

        # Membership function for the consequence
        warning['alarm'] = fuzz.trapmf(warning.universe, [0, 0, 20, 60])
        warning['caution'] = fuzz.trapmf(warning.universe, [20, 30, 60, 80])
        warning['critical'] = fuzz.trapmf(warning.universe, [40, 80, 100, 100])

        # To help understand what the membership looks like, we use the ``view`` method. This method uses matplotlib
        # infected.view()
        # uninfected.view()
        # warning.view()
        """
        Our Fuzzy rules:
        Now, to make these trapezoids useful, we define the *fuzzy relationship*
        between input and output variables. consider three simple rules:
        1. IF x1 > a1: warning = "Alert".
        2. IF x1 > a1 and x1 >= x2 + a2 and x1 < x2 + a3: warning = "Caution".
        3. IF x1 > a1 and x1 >= x2 + a2 and x1 >= x2 + a3: warning = "Critical".
        """

        rule1 = ctrl.Rule(infected['average'], warning['alarm'])
        rule2 = ctrl.Rule(infected['average'] | uninfected['average'] | uninfected['low'], warning['caution'])
        rule3 = ctrl.Rule(infected['average'] | uninfected['average'] | uninfected['high'], warning['critical'])

        # We can see the graphs with this function
        # rule1.view()
        # rule2.view()
        # rule3.view()

        """
        Control System Creation and Simulation
        Now that we have our rules defined, we can simply create a control system via:
        """
        warning_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        """
        In order to simulate this control system, we will create a ``ControlSystemSimulation``.  
        This is an object representing our controller applied to a specific set of circumstances.  
        """
        warning_system = ctrl.ControlSystemSimulation(warning_ctrl)
        """
        We can now simulate our control system by simply specifying the inputs
        and calling the ``compute`` method.  For the input we use the current number of zombies and humans.
        """
        warning_system.input['infected'] = current_num_zombies
        warning_system.input['uninfected'] = current_num_zombies - current_num_humans
        warning_system.compute()

        return warning_system.output['warning']
        # We can view it with this function, also uses matplotlib
        # warning.view(sim=warning_system)





