import random
import math

''' Natural constants'''
Kb=1.3806488*(10**(-23)) #Boltzman constant in [m^2][kg]/([s^2][K])

''' system properties '''
N=3000 #num of columns
M=3000  #num of rows
delta=1 #cahnge of temperature in each step in [K]

T0=298.5  #initial temperature in [K]
a=[[j*2, for j in xrange(N)] for i in xrange(M)]   #location of the spins
ang=[[random.uniform(0,359) for i in xrange(N)] for j in xrange(N)]  #initial angles of the spins with room temperature (random)

''' methods '''

def r(i,j): #returns the distance between 2 spins
    return abs(a[i]-a[j])

def P2(x):  #second order legendre polinomial
    return (3*(x**2)-1)/2

def prob(E,T): #probability of the canonial ensamble
    return math.exp((E/(Kb*T)))

def H():  #returns the cerrent hemiltonian of the system
    #TODO


def choose_next():
    #foreach slight change in the position calculate the new hemiltonain and its prob.
    #multiply the number of times this change apear in the options array by the probablity out of the sum of probabilities (make an int)
    #choose one change randomly from the options array and change the positions array.
    return 0

def MC(T): #Monte Carlo Step
    if T==0:
        print("end of simulation")
        #do something
        return 0
    choose_next() #choose the next change
    return MC(T-delta)

    
    
