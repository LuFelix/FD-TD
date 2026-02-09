import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d as conv2
from PIL import Image

def smooth_image(I, n):
    for i in range(n):
        I = conv2(I,np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]])/5.0,'same')
    return I    

def fastInd2RGB(Iidx, M):

    Ny, Nx = Iidx.shape
    
    # Flatten index array
    flat = np.int8( np.clip(Iidx.ravel(),0,255) )

    RGB_flat = M[flat]

    Io = RGB_flat.reshape(Ny, Nx, 3)

    return Io

def addEzToComposite(Ii, Ez, M):
    Ezs = 40 * Ez + 130

    Ezs_uint8 = np.clip(Ezs, 0, 255).astype(np.uint8)

    Ez_rgb = fastInd2RGB(Ezs_uint8, M)

    Io = np.uint8( np.clip(255 * Ez_rgb + Ii.astype(np.float64), 0, 255) )

    return Io

def composeImage(s, wire, er, M2, M3, M4):

    Ss = s / 2 + 128
    Is = fastInd2RGB(np.clip(Ss,0,255).astype(np.uint8), M2)

    Ws = 255 * (1 - wire)
    Iw = fastInd2RGB(np.clip(Ws,0,255).astype(np.uint8), M3)

    Ers = 255 * (er - 1) / 2
    Ier = fastInd2RGB(np.clip(Ers,0,255).astype(np.uint8), M4)

    I = np.uint8( np.clip(255 * (Ier + Is + Iw) / 2, 0, 255) )

    return I

def customColormaps():
    beta = 8.0

    i = np.arange(1, 256).astype(np.float64)

    term_60 = (60 - i) / 255
    term_196 = (i - 196) / 255
    term_128 = (i - 128) / 255

    M1 = np.column_stack([
        (np.pi/2 + np.arctan(beta * term_60)) / np.pi,
        np.zeros_like(i),
        (np.pi / 2 + np.arctan(beta * term_196)) / np.pi
    ])

    M2 = np.column_stack([
        (np.pi/2 + np.arctan(beta * term_196)) / np.pi,
        (np.pi/2 + np.arctan(beta * term_196)) / np.pi,
        (np.pi/2 + np.arctan(beta * term_60)) / np.pi
    ])

    M3 = np.column_stack([
        (np.pi/2 + np.arctan(beta * term_128)) / np.pi,
        (np.pi/2 + np.arctan(beta * term_128)) / np.pi,
        (np.pi/2 + np.arctan(beta * term_128)) / np.pi
    ])

    M4 = np.column_stack([
        np.zeros_like(i),
        (np.pi/2 + np.arctan(beta * term_128)) / np.pi,
        (np.pi/2 + np.arctan(beta * term_128)) / np.pi
    ])

    # Perform MATLAB-style normalization: divide by global max
    M1 /= M1.max()
    M2 /= M2.max()
    M3 /= M3.max()
    M4 /= M4.max()

    return M1, M2, M3, M4

def placeSubImage(Nx, Ny, cx, cy, Ii):

    Hi, Wi = Ii.shape

    Io = np.zeros((Ny, Nx))

    #print(Nx, Ny, cx, cy, Ii.shape)
    
    if (cx<=Wi/2) or ((Nx-cx)<=Wi/2) or (Ny<=(Hi/2)) or ((Ny-cy)<=(Hi/2)):
        print('Image place forbidden');
        Io = np.array([]);
    else:
        Io[int(cy-Hi/2):int(cy+Hi/2), int(cx-Wi/2):int(cx+Wi/2)] = Ii[::-1,:]

    return Io

def leapFrog2D_constants(er, ur, s, dt):

    a = (1.0 - dt*s/(2.0*er))
    b = (1.0 + dt*s/(2.0*er))
    
    c1 = a/b
    c2 = (dt/er)/b
    
    c3 = dt/ur
    c4 = dt/ur

    return c1, c2, c3, c4

def generateConductivity(Nx, Ny, cond_type, parameters):

    x, y = np.meshgrid(np.linspace(0,Nx/Ny,Nx), np.linspace(0,1,Ny))

    s = np.array([])
    
    if cond_type == 'boundary':
        
        sx = np.ones((Ny,Nx))
        sy = np.ones((Ny,Nx))

        L = parameters['L']
        MaxS = parameters['maxS']
        value = parameters['value']
        
        
        slx = value*np.cos(2*np.pi*x/(L*MaxS))**2
        sly = value*np.cos(2*np.pi*y/L)**2
        
        s1 = (sx*slx + sy*sly) + ((sx+sy)**2); 
        s1 *= np.exp(-(3*x/(L*MaxS))**2)
        
        
        slx = value*np.cos(2*np.pi*x/L)**2
        sly = value*np.cos(2*np.pi*y/(L*MaxS))**2
        
        s2 = (sx*slx + sy*sly) + ((sx+sy)**2); 
        s2 *= np.exp(-(3*y/(L*MaxS))**2)
        
        s = s1 + s2 + s1[:,::-1] + s2[::-1,:]
        
    elif cond_type=='image':
        
        name = parameters['name']
        cx = parameters['cx']
        cy = parameters['cy']
        scale = parameters['scale']
        imScale = parameters['imScale']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        # Ifile = plt.imread(name)
        # Ifile = Ifile[:,:,0]
        # Ifile = Ifile[::-1,:]

        #print(Nx, Ny, Ifile.shape)

        # Ifile = smooth_image(Ifile, smooth)
        
        # s = scale*placeSubImage(Nx, Ny, cx*Nx, cy*Ny, Ifile)/255.0

        Ifile = Image.open(name)
        Ifile = np.array( Ifile.resize( (int(imScale*Ifile.size[0]), int(imScale*Ifile.size[1])) ), dtype=np.float32)
        Ifile = Ifile[:,:,0]
        Ifile = Ifile[::-1,:]

        Ifile = smooth_image(Ifile, smooth)

        s = scale*placeSubImage(Nx, Ny, cx*Nx, cy*Ny, Ifile)/255.0
    
    
    elif cond_type=='box':
        
        ulx = int(Ny*parameters['upper_left_x'])
        uly = int(Ny*parameters['upper_left_y'])
        lrx = int(Ny*parameters['lower_right_x'])
        lry = int(Ny*parameters['lower_right_y'])
        value = parameters['value']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        s = np.zeros((Ny,Nx));
        
        s[uly:lry,ulx:lrx] = value;        

        s = smooth_image(s, smooth)
    
    return s

def generateEpsilon(Nx, Ny, eps_type, parameters):

    x, y = np.meshgrid(np.linspace(0,Nx/Ny,Nx), np.linspace(0,1,Ny))
    

    if eps_type=='lens':
        cx = parameters['cx']
        cy = parameters['cy']
        r2 = parameters['r_left']
        r1 = parameters['r_right']
        R = parameters['R']
        er = parameters['er']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        xx1 = (R**2-r1**2)/(2*r1)
        Cr1 = xx1+r1
        xx2 = (R**2-r2**2)/(2*r2)
        Cr2 = xx2+r2
        
        
        I = er*(  ( (((x-(cx-xx1))**2 + (y-cy)**2) < Cr1**2)  +   (x>cx)*1.0 ) > 1.0    )
        I += er*(  ( (x<cx)*1.0  +   (((x-(cx+xx2))**2+(y-cy)**2) < Cr2**2) ) > 1.0    )

        I = smooth_image(I, smooth)
        
        I += 1.0

    elif eps_type=='image':
        name = parameters['name']
        cx = parameters['cx'] 
        cy = parameters['cy']
        scale = parameters['scale']
        imScale = parameters['imScale']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        Ifile = Image.open(name)
        Ifile = np.array( Ifile.resize( (int(imScale*Ifile.size[0]), int(imScale*Ifile.size[1])) ), dtype=np.float32)
        Ifile = Ifile[:,:,0]
        Ifile = Ifile[::-1,:]

        Ifile = smooth_image(Ifile, smooth)

        I = 1.0 + scale*placeSubImage(Nx, Ny, cx*Nx, cy*Ny, Ifile)/255.0


    
    elif eps_type=='box':
        
        ulx = int(Ny*parameters['upper_left_x'])
        uly = int(Ny*parameters['upper_left_y'])
        lrx = int(Ny*parameters['lower_right_x'])
        lry = int(Ny*parameters['lower_right_y'])
        value = parameters['value']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        I = np.ones((Ny,Nx))
        
        I[uly:lry,ulx:lrx] = value

        I = smooth_image(I, smooth)

    elif eps_type=='interface':
        A = parameters['amplitude']
        a = parameters['angle']
        px = x-parameters['point_x']
        py = y-parameters['point_y']
        smooth = parameters['smooth'] if 'smooth' in parameters else 0
        
        I = (-(px*np.cos(a)-py*np.sin(a))<0)*A
        
        I = smooth_image(I, smooth) + 1
    
    # elif eps_type=='lens2'
        
    #     cx = parameters.cx; 
    #     cy = parameters.cy;
    #     lensTickness = parameters.lensTickness;
    #     angle = parameters.angle;
    #     lensHeight = parameters.lensHeight;
    #     er = parameters.er;

    #     R = (lensTickness^2+lensHeight^2)/(2*lensTickness);
        
    #     c1x = cx + (R-lensTickness)*cos(angle);
    #     c1y = cy + (R-lensTickness)*sin(angle);
    #     c2x = cx - (R-lensTickness)*cos(angle);
    #     c2y = cy - (R-lensTickness)*sin(angle);
        
    #     I = er*(  ( ((x-c1x).^2+(y-c1y).^2)<R^2 )&( ((x-c2x).^2+(y-c2y).^2)<R^2 )    );
    #     I = conv2(I,[0 1 0; 1 1 1; 0 1 0]/5,'same');
    #     I = conv2(I,[0 1 0; 1 1 1; 0 1 0]/5,'same');
    #     I = conv2(I,[0 1 0; 1 1 1; 0 1 0]/5,'same');
    #     I = conv2(I,[0 1 0; 1 1 1; 0 1 0]/5,'same');
        
        
    # elif eps_type=='plane_x'
    #     cx = parameters.cx; 
    #     er = parameters.er;
    #     width = parameters.width;
        
    #     I = ones(Ny,Nx);
        
    #     I(:,round((Ny*cx):(Ny*(cx+width)))) = er;

    # elif eps_type=='percolation'
    #     ulx = 1+fix(Ny*parameters.upper_left_x);
    #     uly = 1+fix(Ny*parameters.upper_left_y);
    #     lrx = 1+fix(Ny*parameters.lower_right_x*.999);
    #     lry = 1+fix(Ny*parameters.lower_right_y*.999);
    #     p = parameters.percent;
    #     a = parameters.amplitude;
    #     s = parameters.scale;
        
    #     I = ones(Ny,Nx);
        
    #     B = zeros(size(I(uly:lry,ulx:lrx)));
        
    #     C = imresize(B,s);
        
    #     C = fix(rand(size(C))<p);
        
    #     B = imresize(C,size(B))>0.5;
        
    #     I(uly:lry,ulx:lrx) = 1+a*B;
   
    # elif eps_type=='interface'
    #     A = parameters.amplitude;
    #     a = parameters.angle;
    #     px = x-parameters.point_x;
    #     py = y-parameters.point_y;
        
    #     I = 1+(-(px*cos(a)-py*sin(a))<0)*A;

    # elif eps_type=='box'
    #     ulx = 1+fix(Ny*parameters.upper_left_x);
    #     uly = 1+fix(Ny*parameters.upper_left_y);
    #     lrx = 1+fix(Ny*parameters.lower_right_x);
    #     lry = 1+fix(Ny*parameters.lower_right_y);
    #     value = parameters.value;
        
    #     I = ones(Ny,Nx);
        
    #     I(uly:lry,ulx:lrx) = 1+value;            


    return I

def generateSource(Nx, Ny, source_type, parameters):



    
    if source_type == 'pulse':
        cx = parameters['cx']
        cy = parameters['cy']
        A = parameters['amplitude']
        t0 = parameters['t0']
        s2 = parameters['width']**2
        t = parameters['time']
        
        I = np.zeros((Ny, Nx))
        
        I[int(Ny*cy), int(Ny*cx)] = A*np.exp(-(t-t0)**2/(2*s2))

    elif source_type == 'burst':
        cx = parameters['cx'] 
        cy = parameters['cy']
        A = parameters['amplitude']
        t0 = parameters['t0']
        s2 = parameters['width']**2
        t = parameters['time']
        f = parameters['frequency']
        
        I = np.zeros((Ny, Nx))
        
        I[int(Ny*cy), int(Ny*cx)] = A*np.sin(2*np.pi*f*t)*np.exp(-(t-t0)**2/(2*s2))

    
    elif source_type ==  'sine':
        cx = parameters['cx']
        cy = parameters['cy']
        A = parameters['amplitude']
        f = parameters['frequency']
        t = parameters['time']
        
        I = np.zeros((Ny, Nx))
        
        I[int(Ny*cy), int(Ny*cx)] = A*np.sin(2.0*np.pi*f*t)


    elif source_type == 'plain_square_x':
        cx = parameters['cx']
        A = parameters['amplitude']
        f = parameters['frequency']
        t = parameters['time']
        off = parameters['offset']
        
        I = np.zeros((Ny, Nx))
        
        I[off:-off, int(Ny*cx)] = A*np.arctan(10*np.sin(2*np.pi*f*t))/np.pi

        
    elif source_type == 'plain_sine_x':
        cx = parameters['cx']
        A = parameters['amplitude']
        f = parameters['frequency']
        t = parameters['time']
        off = parameters['offset']
        
        I = np.zeros((Ny, Nx))
        
        I[off:-off, int(Ny*cx)] = A*np.sin(2*np.pi*f*t)

        
#     case 'sweep'
#         cx = parameters.cx; 
#         cy = parameters.cy;
#         A = parameters.amplitude;
#         f = parameters.frequency;
#         df = parameters.deltaFrequency;
#         t = parameters.time;
        
#         I = zeros(Ny, Nx);
        
#         I(round(Ny*cy), round(Ny*cx)) = A*sin(2*pi*(f+t*df)*t);
        

        
#     case 'rotating_sin'
#         cx = parameters.cx; 
#         cy = parameters.cy;
#         A = parameters.amplitude;
#         f = parameters.frequency;
#         w = parameters.angularVelocity;
#         r = parameters.rotationRadius;
#         t = parameters.time;
        
#         I = zeros(Ny, Nx);
        
#         I(round(Ny*(cy+r*cos(w*t))), round(Ny*(cx+r*sin(w*t)))) = A*sin(2*pi*f*t);

#         for i=1:10
#             I = conv2(I,[0 1 1 0; 1 1 1 1; 1 1 1 1; 0 1 1 0]/12,'same');
#         end
        
#     case 'burst'
#         cx = parameters.cx; 
#         cy = parameters.cy;
#         A = parameters.amplitude;
#         t0 = parameters.t0;
#         s2 = parameters.width^2;
#         t = parameters.time;
#         f = parameters.frequency;
        
#         I = zeros(Ny, Nx);
        
#         I(round(Ny*cy), round(Ny*cx)) = A*sin(2*pi*f*t)*exp(-(t-t0).^2/(2*s2));

#     case 'periodic_burst'
#         cx = parameters.cx; 
#         cy = parameters.cy;
#         A = parameters.amplitude;
#         t = parameters.time;
#         f1 = parameters.wave_frequency;
#         d = parameters.displace_percentage;
#         f2 = parameters.burst_frequency;
#         s = parameters.sharpness;
        
#         I = zeros(Ny, Nx);
        
#         I(round(Ny*cy), round(Ny*cx)) = A*sin(2*pi*f1*t).*(0.5+(atan(s*(sin(2*pi*f2*t)+d))/pi)) ;

# end    

# end

    return I