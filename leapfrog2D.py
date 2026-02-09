import numpy as np
import time
import threading



import threading

def task_multiply(A, B):
    C = A*B



def leapFrog2D(Ezi, Hxi, Hyi, parameters):

    # tic =  time.time()   
    c1 = parameters['c1']
    c2 = parameters['c2']
    c3 = parameters['c3']
    c4 = parameters['c4']
    dx = parameters['dx']
    dy = parameters['dy']
    wire = parameters['wire']
    
   
    Nx = Ezi.shape[0]
    Ny = Ezi.shape[1]
    
    i0 = range(Nx-1)
    j0 = range(Ny-1)

    i1 = range(1,Nx)
    j1 = range(1,Ny)
    
    i0_j0 = np.ix_(i0, j0)
    i1_j1 = np.ix_(i1, j1)
    i1_j0 = np.ix_(i1, j0)
    i0_j1 = np.ix_(i0, j1)


    # - mu, epsilon, and s are already mixed into the constants to save computation... This is done once outside this function
    # - wire is 0 or 1, and it "zeroes" the fields in certain parts of the grid to emulate perfect conductors in certain regions
    # - There is no explicit "t" index because, since we do batch update in all the grid, the "o" and "i" in the name of the references
    #   for E and H (Ezi, Ezo, Hxi, etc) takes care of implicitly making "new E" equals "old E" etc.
    #
    # a = (1.0 - dt*s/(2.0*er))
    # b = (1.0 + dt*s/(2.0*er))
    # c1 = a/b
    # c2 = (dt/er)/b
    # c3 = dt/ur
    # c4 = dt/ur
    
    # Ez[i+1, j+1, t+1] = c1[i+1, j+1,   t]*Ezi[i+1, j+1,   t] + c2[i+1, j+1, t+1]*(  ( Hy[i+1, j+1,   t] - Hy[  i, j+1,   t] )/dx - ( Hx[i+1, j+1, t] - Hx[i+1, j, t] )/dy   )
    # Hx[  i,   j,   t] =                   Hxi[  i,   j,   t] + c3[  i,   j,   t]*(  ( Ez[  i,   j,   t] - Ez[  i, j+1,   t] )/dy   )
    # Hy[  i,   j,   t] =                   Hyi[  i,   j,   t] + c4[  i,   j,   t]*(  ( Ez[i+1,   j,   t] - Ez[  i,   j,   t] )/dx   )

    G1 = c1[i1_j1]*Ezi[i1_j1]
    G2 = wire[i1_j1]*Hyi[i1_j1]
    G3 = wire[i0_j1]*Hyi[i0_j1]
    G4 = wire[i1_j1]*Hxi[i1_j1]
    G5 = wire[i1_j0]*Hxi[i1_j0]

    Ezi[i1_j1] = G1 + c2[i1_j1]*(  ( G2 - G3 )/dx - ( G4 - G5 )/dy   )

    K1 = wire[i0_j0]*Ezi[i0_j0]
    K2 = wire[i0_j1]*Ezi[i0_j1]
    K3 = wire[i1_j0]*Ezi[i1_j0]
    K4 = wire[i0_j0]*Ezi[i0_j0]

    Hxi[i0_j0] = Hxi[i0_j0] + c3[i0_j0]*(   ( K1 - K2 )/dy   )
    Hyi[i0_j0] = Hyi[i0_j0] + c4[i0_j0]*(   ( K3 - K4 )/dx   )

    
    # return Ezo, Hxo, Hyo
