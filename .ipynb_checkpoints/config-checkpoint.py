import numpy as np
# from scipy.signal import convolve2d
# from skimage.transform import resize
# from scipy.signal import convolve2d
from util import *

# Config dictoinary 
#
#
# Config parameters:
#
#
# Resolution parameters
# Nx : Grid X resolution
# Ny : Gryd Y resolution
# Nt : Time resolution
#
# stepsize parameters
# dy : Grid Y stepsize
# dx : Grid X stepsize
# dt : Timestep

# Electric medium parameters (must all be Ny x Nx arrays)
# s      : Condutivity 
# wire   : Perfect wire
# er     : Dielectric permitivity
# ur     : Magnectix permissitivy  
#
# Sources parameters (parameters must be a list of sources disctionary, see format bellow)
# sources_names        : List with the source name (each one have specific parameters)
# sources_parameters   : Parameters for the source name
#

#
# OBS: Smooth on epsilon is dangerous because the "empty" space is filled with 1 so, smooth messes up with the bordes
#


def configSimulation(name, anecroic=True):

    S = config_default(anecroic=anecroic)

    # -----------------------------
    # SWITCH-CASE implementation
    # -----------------------------

    if name == 'single lens':
        S = config_single_lens(S)

    if name == 'single lens plane':
        S = config_single_lens_plane(S)

    elif name == 'laser pulse':
        S = config_laser_pulse(S)

    elif name == 'yagi_antenna':
        S = config_yagi_antenna(S)

    elif name == 'antireflex':
        S = config_antireflex(S)

    elif name == 'opticalfiber':
        S = config_optical_fiber(S)

    elif name == 'optical ckt':
        S = config_optical_ckt(S)

    elif name == 'dual optcal fiber':
        S = config_dual_optical_fiber(S)

    elif name == 'refraction':
        S = config_refraction(S)
    
    else:    
        print(f"[configSimulation] Unknown configuration name: {name}")

    return S





def config_default(anecroic=True):
    S = {}

    # ---------------------------
    # Default values
    # ---------------------------

    S['Nx'] = 800
    S['Ny'] = 416
    S['Nt'] = 1500

    S['dy'] = 1.0 / max(S['Ny'], S['Nx'])
    S['dx'] = S['dy']

    CLF = np.sqrt(1/S['dx']**2 + 1/S['dy']**2)
    S['dt'] = 1.0 / CLF

    # absorbing boundaries
    p = {}
    p['L'] = 0.15
    p['maxS'] = 1.4
    if anecroic:
        p['value'] = 100.0
    else:
        p['value'] = 0.0
    
    S['s']  = generateConductivity(S['Nx'], S['Ny'], 'boundary', p)

    S['wire'] = np.ones((S['Ny'], S['Nx']))
    S['er']   = np.ones((S['Ny'], S['Nx']))
    S['ur']   = np.ones((S['Ny'], S['Nx']))

    # sources
    S['sources_names'] = []
    S['sources_parameters'] = []

    return S


def config_refraction(S):
  
    aperture = 0.45
    pos = 0.1
    x = 0.5

    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 0.01
    p['lower_right_x'] = x+0.07
    p['lower_right_y'] = aperture+pos
    p['value'] = 550
    p['smooth'] = 10
    S['s'] += generateConductivity(S['Nx'], S['Ny'], 'box', p)

    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 1-aperture+pos
    p['lower_right_x'] = x+0.07
    p['lower_right_y'] = 1-0.01
    p['value'] = 550
    p['smooth'] = 10
    S['s'] += generateConductivity(S['Nx'], S['Ny'], 'box', p)
    
    p = {}
    p['cx'] = x
    p['cy'] = 0.5+pos
    p['r_left'] = 0.06
    p['r_right'] = 0.01
    p['R'] = 0.2
    p['er'] = 2
    p['smooth'] = 10
    S['er'] = generateEpsilon(S['Nx'], S['Ny'], 'lens', p)
    
    
    
    p = {}
    px = 0.8;
    er = 1;
    p['point_x'] = px
    p['point_y'] = 0.5
    p['angle'] = np.pi/4
    p['amplitude'] = er
    p['smooth'] = 20
    S['er'] *= generateEpsilon(S['Nx'], S['Ny'], 'interface',p)

    p = {}
    p['point_x'] = px+0.6
    p['point_y'] = 0.5
    p['angle'] = np.pi/4
    p['amplitude'] = -1+1/(er+1)
    p['smooth'] = 20
    S['er'] *= generateEpsilon(S['Nx'], S['Ny'], 'interface',p)
        


    sources_parameter1 = {}
    sources_parameter1['cx'] = 0.2;
    sources_parameter1['cy'] = 0.5+pos+0.01
    sources_parameter1['amplitude'] = 1200
    sources_parameter1['frequency'] = 0
    sources_parameter1['time'] = 0;        

    sources_parameter2 = {}
    sources_parameter2['cx'] = 0.21;
    sources_parameter2['cy'] = 0.5+pos+0.01
    sources_parameter2['amplitude'] = 1200
    sources_parameter2['frequency'] = 60
    sources_parameter2['time'] = 0;   


    S['sources_names'].append('sine')
    S['sources_names'].append('sine')
    S['sources_parameters'].append(sources_parameter1)
    S['sources_parameters'].append(sources_parameter2)

    return S


def config_single_lens_plane(S):

    # lens
    p = {}
    p['cx'] = 0.6
    p['cy'] = 0.5
    p['r_left'] = 0.15
    p['r_right'] = 0.15
    p['R'] = 0.5
    p['er'] = 2
    p['smooth'] = 200
    S['er'] = generateEpsilon(S['Nx'], S['Ny'], 'lens', p)
    
    
    # sources config
    sources_parameter = {}
    sources_parameter['cx'] = 0.1
    sources_parameter['amplitude'] = 100
    sources_parameter['frequency'] = 30
    sources_parameter['offset'] = int(S['Ny']*0.1)
    sources_parameter['time'] = 0
        
    S['sources_names'].append('plain_sine_x')
    S['sources_parameters'].append(sources_parameter)


    
    return S


def config_single_lens(S):

    # lens
    p = {}
    p['cx'] = 0.6
    p['cy'] = 0.5
    p['r_left'] = 0.15
    p['r_right'] = 0.15
    p['R'] = 0.5
    p['er'] = 2
    p['smooth'] = 200
    S['er'] = generateEpsilon(S['Nx'], S['Ny'], 'lens', p)
    
    
    # sources config
    
    # sine source
    S['sources_names'].append('sine')
    sources_parameter = {}
    sources_parameter['cx'] = 0.25
    sources_parameter['cy'] = 0.5
    sources_parameter['amplitude'] = 800
    sources_parameter['width'] = 0.03
    sources_parameter['t0'] =  sources_parameter['width']*6 + 0.03
    sources_parameter['time'] = 0
    sources_parameter['s2'] = 0.03
    sources_parameter['frequency'] = 40
    S['sources_parameters'].append(sources_parameter)



    return S

def config_laser_pulse_line(S):
    
    sources_parameter1 = {}
    sources_parameter1['cx'] = 0.2;
    sources_parameter1['amplitude'] = 10;
    sources_parameter1['frequency'] = 25;
    sources_parameter1['offset'] = int(S['Ny']*0.3);
    sources_parameter1['time'] = 0;        

    sources_parameter2 = {}
    sources_parameter2['cx'] = 0.21;
    sources_parameter2['amplitude'] = 10;
    sources_parameter2['frequency'] = 25;
    sources_parameter2['offset'] = int(S['Ny']*0.3);
    sources_parameter2['time'] = 0;   


    S['sources_names'].append('plain_sine_x')
    S['sources_names'].append('plain_sine_x')
    S['sources_parameters'].append(sources_parameter1)
    S['sources_parameters'].append(sources_parameter2)


    return S

def config_laser_pulse(S):
    
    # sine source
    S['sources_names'].append('burst')
    sources_parameter = {}
    sources_parameter['cx'] = 0.25
    sources_parameter['cy'] = 0.5
    sources_parameter['amplitude'] = 1800
    sources_parameter['width'] = 0.03
    sources_parameter['t0'] =  sources_parameter['width']*3 + 0.03
    sources_parameter['time'] = 0
    sources_parameter['frequency'] = 40
    S['sources_parameters'].append(sources_parameter)


    return S


def config_yagi_antenna(S):
        
    sources_parameter1 = {}
    sources_parameter1['cx'] = 0.8
    sources_parameter1['amplitude'] = 10
    sources_parameter1['frequency'] = 14.5
    sources_parameter1['offset'] = int(S['Ny']*0.3)
    sources_parameter1['time'] = 0

    sources_parameter2 = {}
    sources_parameter2['cx'] = 0.7
    sources_parameter2['amplitude'] = 10
    sources_parameter2['frequency'] = 14.5
    sources_parameter2['offset'] = int(S['Ny']*0.2)
    sources_parameter2['time'] = 0

    sources_parameter3 = {}
    sources_parameter3['cx'] = 0.6
    sources_parameter3['amplitude'] = 10
    sources_parameter3['frequency'] = 14.5
    sources_parameter3['offset'] = int(S['Ny']*0.1)
    sources_parameter3['time'] = 0
        
    S['sources_names'].append('plain_sine_x')
    S['sources_names'].append('plain_sine_x')
    S['sources_names'].append('plain_sine_x')
    S['sources_parameters'].append(sources_parameter1)
    S['sources_parameters'].append(sources_parameter2)
    S['sources_parameters'].append(sources_parameter3)

    return S



def config_antireflex(S):
    
# +--------------------------
# | division
    p = {}
    p['name'] = 'images/antireflex_s.png'
    p['cx'] = 0.5
    p['cy'] = 0.5
    p['scale'] = 150
    p['imScale'] = 1
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'image', p)
    
    
    p = {}
    p['upper_left_x'] = 0.725
    p['upper_left_y'] = 0.001
    p['lower_right_x'] = 0.775
    p['lower_right_y'] = 0.15
    p['value'] = 150
    p['smooth'] = 2
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    p = {}
    p['upper_left_x'] = 0.725
    p['upper_left_y'] = 0.35
    p['lower_right_x'] = 0.775
    p['lower_right_y'] = 0.5
    p['value'] = 150
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    
    p = {}
    p['cx'] = 0.75
    p['cy'] = 0.25
    p['r_left'] = 0.06
    p['r_right'] = 0.05
    p['R'] = 0.11
    p['er'] = 1.1
    p['smooth'] = 4
    S['er'] = S['er'] + generateEpsilon(S['Nx'], S['Ny'], 'lens', p) - 1

    
    p = {}
    p['upper_left_x'] = 0.725
    p['upper_left_y'] = 0.5
    p['lower_right_x'] = 0.775
    p['lower_right_y'] = 0.65
    p['value'] = 150
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    p = {}
    p['upper_left_x'] = 0.725
    p['upper_left_y'] = 0.85
    p['lower_right_x'] = 0.775
    p['lower_right_y'] = 0.999
    p['value'] = 150
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    
    p = {}
    p['cx'] = 0.75
    p['cy'] = 0.75
    p['r_left'] = 0.06
    p['r_right'] = 0.05
    p['R'] = 0.11
    p['er'] = 1.1
    p['smooth'] = 4
    S['er'] = S['er'] + generateEpsilon(S['Nx'], S['Ny'], 'lens', p) - 1

        
        
        
# +--------------------------
# | cristal
# 
    p = {}
    p['name'] = 'images/antireflex_er2.png'
    p['cx'] = 0.5
    p['cy'] = 0.5
    p['scale'] = 1.47
    p['imScale'] = 1
    p['smooth'] = 1
    S['er'] = S['er'] + generateEpsilon(S['Nx'], S['Ny'], 'image', p) - 1
    
    
    # % sources config

    # % sine
    sources_parameter1 = {}
    sources_parameter1['cx'] = 0.25
    sources_parameter1['cy'] = 0.25
    sources_parameter1['amplitude'] = 1200
    sources_parameter1['frequency'] = 40
    sources_parameter1['time'] = 0

    sources_parameter2 = {}
    sources_parameter2['cx'] = 0.25
    sources_parameter2['cy'] = 0.75
    sources_parameter2['amplitude'] = 1200
    sources_parameter2['frequency'] = 40
    sources_parameter2['time'] = 0

    S['sources_names'].append('sine')
    S['sources_names'].append('sine')
    S['sources_parameters'].append(sources_parameter1)
    S['sources_parameters'].append(sources_parameter2)

    return S


def config_optical_fiber(S):

    aperture = 0.37
    pos = 0.1
    x = 0.4
    
    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 0.01
    p['lower_right_x'] = x+0.17
    p['lower_right_y'] = aperture+pos
    p['value'] = 550
    p['smooth'] = 10
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 1-aperture+pos
    p['lower_right_x'] = x+0.17
    p['lower_right_y'] = 1-0.01
    p['value'] = 550
    p['smooth'] = 10
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)
    
    p = {}
    p['cx'] = x*S['Ny']/S['Nx']+0.01
    p['cy'] = 0.5+pos
    p['name'] = 'images/lens.png'
    p['imScale'] = 1
    p['scale'] = 4       
    p['smooth'] = 4
    p['value'] = 3
    S['er'] = generateEpsilon(S['Nx'], S['Ny'], 'image',p)
    
    # %fiber
    p = {}
    p['upper_left_x'] = x+0.06
    p['upper_left_y'] = aperture+pos
    p['lower_right_x'] = 1.9
    p['lower_right_y'] = 1-aperture+pos
    p['value'] = 2
    S['er'] = S['er']*generateEpsilon(S['Nx'], S['Ny'], 'box', p)
    
    
    # % first burst
    sources_parameter1 = {}
    sources_parameter1['cx'] = 0.15
    sources_parameter1['cx'] = 0.15
    sources_parameter1['cy'] = 0.5+pos-0.1
    sources_parameter1['amplitude'] = 600
    sources_parameter1['frequency'] = 50
    sources_parameter1['time'] = 0

    S['sources_names'].append('sine')
    S['sources_parameters'].append(sources_parameter1)

    return S



def config_optical_ckt(S):

    S['Nx'] = 1802
    S['Ny'] = 802
    
    
    S['dy'] = 1.0/max([S['Ny'], S['Nx']])
    S['dx'] = S['dy']

    CLF = np.sqrt(1.0/(S['dx']**2)+1.0/(S['dy']**2))
    
    S['dt'] = 1.0/CLF

    S['wire'] = np.ones((S['Ny'],S['Nx']))
    S['er'] = np.ones((S['Ny'],S['Nx']))
    S['ur'] = np.ones((S['Ny'],S['Nx']))


    # absorbing boundaries
    p = {}
    p['L'] = 0.15
    p['maxS'] = 1.4
    p['value'] = 100.0
    S['s'] = generateConductivity(S['Nx'], S['Ny'], 'boundary', p)
    
   
    aperture = 0.46
    pos = 0.192
    x = 0.3
    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 0.01
    p['lower_right_x'] = x+0.05
    p['lower_right_y'] = aperture+pos
    p['value'] = 550
    S['s'] += generateConductivity(S['Nx'], S['Ny'], 'box', p)
    
    p = {}
    p['upper_left_x'] = x;
    p['upper_left_y'] = 1-aperture+pos;
    p['lower_right_x'] = x+0.05;
    p['lower_right_y'] = 1-0.01;
    p['value'] = 550;
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    
    p = {}
    p['cx'] = 1400.0/1800.0
    p['cy'] = 0.5
    p['name'] = 'images/waveguide.png'
    p['imScale'] = 1
    p['scale'] = 17
    S['er'] = generateEpsilon(S['Nx'], S['Ny'], 'image',p)

    p = {}
    p['cx'] = (1000.0-380.0)/1800.0+0.01
    p['cy'] = 0.5
    p['imScale'] = 1
    p['name'] = 'images/fiber_curve.png'
    p['scale'] = 6
    S['er'] = S['er']*generateEpsilon(S['Nx'], S['Ny'], 'image',p)
    
    
    # % second burst
    source_parameter1 = {}
    source_parameter1['cx'] = 0.15;
    source_parameter1['cy'] = 0.5+pos;
    source_parameter1['amplitude'] = 3000;
    source_parameter1['frequency'] = 2.2*10;
    source_parameter1['width'] = 0.3;
    source_parameter1['t0'] =  0.01;
    source_parameter1['time'] = 0;
    
    S['sources_names'].append('burst')
    S['sources_parameters'].append(source_parameter1)

    return S




def config_dual_optical_fiber(S):

    aperture = 0.37
    pos = 0.1
    x = 0.4
    p = {}
    p['upper_left_x'] = x
    p['upper_left_y'] = 0.01
    p['lower_right_x'] = x+0.12
    p['lower_right_y'] = 0.285
    p['value'] = 550
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

    p = {}                                     
    p['upper_left_x'] = x
    p['upper_left_y'] = 0.313
    p['lower_right_x'] = x+0.12
    p['lower_right_y'] = 0.47
    p['value'] = 550
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)
        
    p = {}        
    p['upper_left_x'] = x
    p['upper_left_y'] = 1-aperture+pos
    p['lower_right_x'] = x+0.12
    p['lower_right_y'] = 1-0.01
    p['value'] = 550
    S['s'] = S['s'] + generateConductivity(S['Nx'], S['Ny'], 'box', p)

        

    # lens
    p = {}
    p['cx'] = x
    p['cy'] = 0.6
    p['R'] = 0.15
    p['r_left'] = 0.15*p['R']
    p['r_right'] = 0.15*p['R']
    p['er'] = 4
    p['smooth'] = 20
    S['er'] = S['er']*generateEpsilon(S['Nx'], S['Ny'], 'lens', p)

    
        
    # %fiber
    aperture = 0.37
    pos = 0.1
    x = 0.4
    p = {}
    p['upper_left_x'] = x+0.09
    p['upper_left_y'] = aperture+pos
    p['lower_right_x'] = 1.9
    p['lower_right_y'] = 1-aperture+pos
    p['value'] = 2.2
    S['er'] = S['er']*generateEpsilon(S['Nx'], S['Ny'], 'box', p)

        
        
    # %fiber
    aperture = 0.485
    pos = -0.2
    x = 0.4
    p = {}
    p['upper_left_x'] = x+0.0
    p['upper_left_y'] = aperture+pos
    p['lower_right_x'] = 1.9
    p['lower_right_y'] = 1-aperture+pos
    p['value'] = 2.2
    S['er'] = S['er']*generateEpsilon(S['Nx'], S['Ny'], 'box', p)
        
 
    # % second burst
    source_parameter1 = {}
    source_parameter1['cx'] = 0.15
    source_parameter1['cy'] = 0.72-0.20
    source_parameter1['amplitude'] = 3000
    source_parameter1['frequency'] = 50
    source_parameter1['width'] = 0.3
    source_parameter1['t0'] =  0.01
    source_parameter1['time'] = 0
    
    S['sources_names'].append('burst')
    S['sources_parameters'].append(source_parameter1)
    

    return S




