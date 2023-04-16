# Zombie simulation

This repository presents an object-oriented simulation model realized in the programming 
language of general application - Python. In addition to the simulation model of the zombie virus pandemic, 
a simple imaginary animation of the same is presented. A hypothetical zombie apocalypse is 
explored through the lens of disease spreading models used in practice for diseases such as HIV, malaria, HPV as well as various other tropical diseases.

### Reader can look at the Play-through of the mini-game when they click on the link:
<p align="center">
  <a href="https://vimeo.com/818051319" target="_blank">
    <img src="https://i.ibb.co/ZVLvMSM/bg-beg1.png" alt="A Play-through of the mini-game">
  </a>
</p>

## Content

This repository contains the codebase I used to simulate an zombie virus spreading. Methods used to simulate are SimPy for handling the simulation, an evolutionary algorithm, handling ODE computing, and scikit-fuzzy for handling fuzzy decision-making.

The codebase is structured into four modules: `main_simulation`, `main_animation`, `zombie_apocalypse`, and `genetics`.

`main_simulation.py` takes classes contained in `zombie_apocalypse.py` and `genetics.py` and fires up the simulation process.

`main_animation.py` contains all the code for animating a mini-game using PyGame, where the results of the simulation is played out in a creative way.

`zombie_apocalypse.py` contains fuzzy decision-making algorithm and the raw computing of ODE's.

`genetics.py` contains an evolutionary algorithm that helps the program decide on the best government policies that need to be in place.

If the reader is interested in the mechanics of the mathematics used there is a more detailed explanation in authors semester paper in Serbian titled 
<mark>"Zombie Pandemic Modeling An Object-Oriented Approach to Simulating Virus Outbreak Dynamics"</mark>. 
Else the reader can find more about the topic in the `Literature` section. 

Additionally, there is the folder `animation` which contains all the neede picture and music, as well as other things.

## Literature

[1] „Mathematical modeling of zombies“ Robert Smith? University of Ottawa Press 2014

[2] „When zombies attack!: Mathematical modelling of an outbreak of zombie infection“ Philip Munz, Ioan Hudea, Joe Imad, Robert J. Smith?
