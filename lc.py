import __future__
import random
import math

#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#'                     Natural Constants                          '
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

Kb=1.3806488*(10**(-16)) #Boltzman constant in [cm^2][g]/([s^2][K])


#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#'                     System Properties                          '
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

N=2 #num of columns
M=2  #num of rows
delta=1 #cahnge of temperature in each step in [K]

d = 2   #dimentions of the system

T0=298  #initial temperature in [K]

ang=[[random.uniform(0,2*math.pi) for i in xrange(N)] for j in xrange(M)]  #initial angles of the spins with room temperature (random)

MIN_TEMPERATURE = 0
NUM_METROPOLIS_STEPS = 1000
MAX_NON_IMPROVING_STEPS = 3

#pos=[[j*2 for j in xrange(N)] for i in xrange(M)]   #location of the spins


#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#'                        Methods                                 '
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def print_angs(angs):                                           #prints the spins
    st=""
    for i in xrange(N):
        for j in xrange(M):
            st+= " "+str(angs[i][j])
        print st
        print "\n"
        st=""
    return 0





def r(i,j): #returns the distance between 2 spins
    return abs(pos[i]-pos[j])






def P2(x):                                                    #second order legendre polinomial
    return (3*(x**2)-1)/2




def prob(E,T):                                              #probability of the canonial ensamble
    return math.exp(-(abs(E)/(Kb*T)))





def is_equilliberated(T):                                   #calculate the total potential energy
                                                            #return 1 if so, 0 else
    e=E(ang)
    t=thermo_energy(T)
    print float(e+t-E0)
    return (float(e+t-E0))                                  #TODO:!!!!!!!!!!







def E(angles):                                              #returns the current potential energy of the system
    h=0
    
    for part_x in xrange(N):
        for part_y in xrange(M):
            h=h+Unear((part_x,part_y),angles)
               
    return (10**(-16))*h





def thermo_energy(T):                                   #returns the current thermic energy of the system
    return d*0.5*N*M*Kb*T





    
def Unear(part,angles):                                 #calcutes the potential of particle part from its nearest neighbours
    u=0
    new_angle=angles[part[0]][part[1]]
    
    if (part[0]<N-1):
        u=u+P2(math.cos((new_angle-angles[part[0]+1][part[1]])%360))
    if (part[1]<M-1):
        u=u+P2(math.cos((new_angle-angles[part[0]][part[1]+1])%360))
#    if (part[0]>0):
#        u=u+P2(cos((new_angle-angles[part[0]-1][part[1]])%360))
#    if (part[1]>0):
#        u=u+P2(cos((new_angle-angles[part[0]][part[1]-1])%360))
    return u

#def U1(part,angles):  #calculates the potential between part and all the othe particles the come after it in their order
#    u=0
#    new_angle=angles[part[0]][part[1]]
#    
#    if part[0]<N:
#        for i in xrange(part[0]+1,N):
#            u=u+P2(cos((new_angle-angles[i][part[1]])%360))
#        for part2_x in xrange(part[0]+1,N):
#            if part[1]<M:
#                for part2_y in xrange(part[1]+1,M):
#                    u=u+P2(cos((new_angle-angles[part2_x][part2_y])%360))
#    if part[1]<M:
#        for i in xrange(part[1]+1,M):
#            u=u+P2(cos((new_angle-angles[part[0]][i])%360))
#        
#    return u


def choose_next(angles, T): #foreach particle from the first to the last:
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
    # Go over all of the particles, and change the angles for each one.
    for part_x in xrange(N):
        for part_y in xrange(M):
            # TODO: Select the initial angle.
            # Perform NUM_METROPOLIS_STEPS steps and each time select a new
            # angle from a distribution that should become more and more as the
            # boltzman energy distribution.
            for step in xrange(NUM_METROPOLIS_STEPS):
                # Select a new angle based on the current one using a Gaussian
                # distribution.
                curr_angle = angles[part_x][part_y]
                new_angle = random.gauss(curr_angle, 1)

                # Calculate the coefficient that is proportional to the density
                # of the boltzman distibution.
                Ep=E(angles)
                angles[part_x][part_y] = new_angle
                En=E(angles)
                alpha = prob(En,T)/prob(Ep,T)

                alpha = min(1.0, alpha)
                p = random.random()
                if p > alpha:
                    angles[part_x][part_y] = curr_angle


def MC(T):                                                                                  #Monte Carlo Step
    global ang
    while T > MIN_TEMPERATURE:
        print "--------------------(T = %s[K])--------------------" % str(T)
        print_angs(ang)
        print "Energy: %s" % E(ang)
    
        # Continue choosing angles using the Metropolis algorithm until we reach
        # equlibrium.
        ebest = E(ang)
        k = 0
        while k < MAX_NON_IMPROVING_STEPS:
            print "Performing Metropolis step... ",
            new_angles = [row[:] for row in ang]
            choose_next(new_angles, T)
            e = E(new_angles)

            if e < ebest:
                ebest = e
                ang = new_angles
                k = 0
                print "Got better energy."
            else:
                k += 1
                print "Didn't get better energy (k=%s)" % k
            
#        while not is_equilliberated(T):
#            choose_next(T)
        
        # Next step with lower temperature.
        print "Cooling... (T=%s[K]->%s[K])" % (T, T-delta)
        T -= delta

    print("End of Simulation.\n")
    #TODO:do something





#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#'                         Main                                   '
#''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

E0=E(ang)+thermo_energy(T0) # initial energy of the system
print "*"*70
print "*"*70
print "Starting the Simulation with T=%s[K] and N=%s, M=%s" % (str(T0), str(N), str(M))
print "*"*70
print "*"*70
MC(T0)
