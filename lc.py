import __future__
import random
import math

''' Natural constants'''
Kb=1.3806488*(10**(-23)) #Boltzman constant in [m^2][kg]/([s^2][K])

''' system properties '''
N=3000 #num of columns
M=3000  #num of rows
delta=1 #cahnge of temperature in each step in [K]

d = 3   #dimentions of the system

T0=298.5  #initial temperature in [K]
#a=[[j*2, for j in xrange(N)] for i in xrange(M)]   #location of the spins
ang=[[random.uniform(0,359) for i in xrange(N)] for j in xrange(N)]  #initial angles of the spins with room temperature (random)

''' methods '''

def r(i,j): #returns the distance between 2 spins
    return abs(a[i]-a[j])

def P2(x):  #second order legendre polinomial
    return (3*(x**2)-1)/2

def prob(E,T): #probability of the canonial ensamble
    return math.exp(-(abs(E)/(Kb*T)))

def H():  #returns the current Hemiltonian of the system
    #TODO
    return 0
    
def U(part,angle=-1): #calcutes the potential of particle part from its nearest neighbours
    u=0
    new_angle=ang[part[0]][part[1]]
    if(angle==-1): new_angle = angle
    
    if (part[0]<N):
        u=u+P2((new_angle-ang[part[0]+1][part[1]])%360)
    if (part[1]<M):
        u=u+P2((new_angle-ang[part[0]][part[1]+1])%360)
    if (part[0]>0):
        u=u+P2((new_angle-ang[part[0]-1][part[1]])%360)
    if (part[1]>0):
        u=u+P2((new_angle-ang[part[0]][part[1]-1])%360)
        
    return u

def thermo_energy(T):
    return d*0.5*N*M*Kb*T

def is_equilliberated():
    #calculate the total potential energy and return 1 if it is the same as the thermodynamic energy and 0 elsewhere.
    return 1 

def choose_next():
    #foreach slight change in the position calculate the new hemiltonain and its prob.
    #multiply the number of times this change apear in the options array by the probablity out of the sum of probabilities (make an int)
    #choose one change randomly from the options array and change the positions array.
    part=(random.random(N),random.random(M))
    opts=[]   #array with the changing options
    
    prob_plus=prob(U(part,ang[part[0]][part[1]]+1)-U(part))
    prob_minus=prob(U(part,ang[part[0]][part[1]]-1)-U(part))
    
    plus_normalized=int((prob_plus*100)/(prob_plus+prob_minus))
    
    for i in xrange(plus_normalized):
        opts.append[1]
    for i in xrange(100-plus_normalized):
        opts.append[-1]
    
    ang[part[0]][part[1]] = ang[part[0]][part[1]]+opts[random.uniform(0,len(opts))] #changing the angle
    
    return 0

def MC(T): #Monte Carlo Step
    if T==0:
        print("end of simulation\n")
        #do something
        return 0
    
    while  not is_equilliberated():
        choose_next()

        
    print("cooling\n")
    return MC(T-delta)  #next step with lower temperature

    
    
