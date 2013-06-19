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

T0=298  #initial temperature in [K]
#a=[[j*2, for j in xrange(N)] for i in xrange(M)]   #location of the spins
ang=[[random.uniform(0,359) for i in xrange(N)] for j in xrange(N)]  #initial angles of the spins with room temperature (random)

''' methods '''

def r(i,j): #returns the distance between 2 spins
    return abs(a[i]-a[j])

def P2(x):  #second order legendre polinomial
    return (3*(x**2)-1)/2

def prob(E,T): #probability of the canonial ensamble
    return math.exp(-(abs(E)/(Kb*T)))

def E(angles):  #returns the current potential energy of the system
    h=0            
    for part_x in xrange(N):
        for part_y in xrange(M):
            if part_x == part[0] and part_y == part[1]:
                h=h+U1(part,angles)
            else:
                h=h+U1((part_x,part_y),-1)
               
    return h
    
def Unear(part,angle=-1): #calcutes the potential of particle part from its nearest neighbours
    u=0
    new_angle=ang[part[0]][part[1]]
    if(angle==-1): new_angle = angle
    
    if (part[0]<N):
        u=u+P2(cos((new_angle-ang[part[0]+1][part[1]])%360))
    if (part[1]<M):
        u=u+P2(cos((new_angle-ang[part[0]][part[1]+1])%360))
    if (part[0]>0):
        u=u+P2(cos((new_angle-ang[part[0]-1][part[1]])%360))
    if (part[1]>0):
        u=u+P2(cos((new_angle-ang[part[0]][part[1]-1])%360))
        
    return u

def U1(part,angles):  #calculates the potential between part and all the othe particles the come after it in their order
    u=0
    new_angle=angles[part[0]][part[1]]
    
    if part[0]<N:
        for i in xrange(part[0]+1,N):
            u=u+P2(cos((new_angle-angles[i][part[1]])%360))
        for part2_x in xrange(part[0]+1,N):
            if part[1]<M:
                for part2_y in xrange(part[1]+1,M):
                    u=u+P2(cos((new_angle-angles[part2_x][part2_y])%360))
    if part[1]<M:
        for i in xrange(part[1]+1,M):
            u=u+P2(cos((new_angle-angles[part[0]][i])%360))
        
    return u
    
def thermo_energy(T):
    return d*0.5*N*M*Kb*T

def is_equilliberated():
    #calculate the total potential energy and return 1 if it is the same as the thermodynamic energy and 0 elsewhere.
    return 1 

def choose_next():

    #foreach particle from the first to the last:
        #if there is a new orientation with a lower potential- changethe particle's angle
        #else - choose an angle with a probabilty exp(-(Enew-Ecurr)/(KbT))
        #multiply the number of times this change apear in the options array by the probablity out of the sum of probabilities (make an int)
        #choose one angle randomly from the options array and change the ang array.
        
    '''
    #foreach slight change in the position calculate the new hemiltonain and its prob.
    #multiply the number of times this change apear in the options array by the probablity out of the sum of probabilities (make an int)
    #choose one change randomly from the options array and change the positions array.
    
    part=(random.random(N),random.random(M))
    
    
    prob_plus=prob(Unear(part,ang[part[0]][part[1]]+1)-Unear(part))
    prob_minus=prob(Unear(part,ang[part[0]][part[1]]-1)-Unear(part))
    
    plus_normalized=int((prob_plus*100)/(prob_plus+prob_minus))
    
    for i in xrange(plus_normalized):
        opts.append(1)
    for i in xrange(100-plus_normalized):
        opts.append(-1)
        
    ang[part[0]][part[1]] = ang[part[0]][part[1]]+opts[random.uniform(0,len(opts))] #changing the angle
    '''
    
    opts=[]   #array with the changing options
    new_angles=ang[:]
    
    
        
    for part_x in xrange(N):
        for part_y in xrange(M):
            for new_angle in xrange(359):
                if new_angle == ang[part_x][part_y]:
                    continue
                
                new_angles[part_x][part_y]=new_angle
                En=E(new_angles)
                Ep=E(ang)
                
                if En < Ep:
                    ang[part_x][part_y] = new_angle #changing the angle
                    break
                else:
                    
                    ang_prob=prob(En-Ep)
                
                for i in xrange(int(ang_prob*100)):
                    opts.append(new_angle)
            
            if new_angle>=359:
                ang[part_x][part_y] = opts[random.uniform(0,len(opts))] #changing the angle 
                new_angles[part_x][part_y]=ang[part_x][part_y]
       
    return 0

def MC(T): #Monte Carlo Step
    if T==0:
        print("end of simulation\n")
        #do something
        return 0
    
    while  not is_equilliberated():
        choose_next()
    
        
    print("cooling\n")
    print str(T)
    return MC(T-delta)  #next step with lower temperature

print ("starting the simulation with "+ str(T0) +"[K] and N = "+str(N)+", M = "+str(M)+"\n")
MC(T0)
    
    
