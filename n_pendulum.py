from mmap import ALLOCATIONGRANULARITY
import pygame as pg
import sympy as sp
import numpy as np


# User defined values
masses = [2,2]
lengths = [1,1]


assert len(masses) == len(lengths), "Mass and rod counts do not match"
assert len(masses) >= 1, "Too few values"

n = len(lengths)

t, g = sp.symbols('t g')
m = [sp.symbols('m{}'.format(i)) for i in range(n)]
l = [sp.symbols('l{}'.format(i)) for i in range(n)]
#m1, m2 = sp.symbols('m1 m2')
#L1, L2 = sp.symbols('L1 L2')

theta = [sp.symbols('\theta_{}'.format(i), cls=sp.Function)(t) for i in range(n)]

#the1, the2 = sp.symbols(r'\theta_1, \theta_2', cls=sp.Function)

#the1 = the1(t)
#the2 = the2(t)

theta_d = [sp.diff(angle, t) for angle in theta]
theta_dd = [sp.diff(velocity, t) for velocity in theta_d]

#the1_d = sp.diff(the1, t)
#the2_d = sp.diff(the2, t)
#the1_dd = sp.diff(the1_d, t)
#the2_dd = sp.diff(the2_d, t)

x = [l[0]*sp.sin(theta[0])]
y = [-l[0]*sp.cos(theta[0])]
for i in range(1,n):
    x.append( x[i-1] + l[i]*sp.sin(theta[i]) )
    y.append( y[i-1] - l[i]*sp.cos(theta[i]) )

#x1 = L1*sp.sin(the1)
#y1 = -L1*sp.cos(the1)

#x2 = L1*sp.sin(the1)+L2*sp.sin(the2)
#y2 = -L1*sp.cos(the1)-L2*sp.cos(the2)

# Use these to define the kinetic and potential energy for each mass. Obtain the Lagrangian
# Kinetic (K = 1/2(mv^2))
T = sum([(1/2)*m[i]*(sp.diff(x[i], t)**2 + sp.diff(y[i], t)**2) for i in range(n)])

#T1 = 1/2 * m1 * (sp.diff(x1, t)**2 + sp.diff(y1, t)**2)
#T2 = 1/2 * m2 * (sp.diff(x2, t)**2 + sp.diff(y2, t)**2)
#T = T1 + T2
# Potential (V = mgh)
V = sum([m[i]*g*y[i] for i in range(n)])

#V1 = m1*g*y1
#V2 = m2*g*y2
#V = V1 + V2
# Lagrangian
L = T-V

LE = [sp.diff(L, theta[i]) - sp.diff(sp.diff(L, theta_d[i]), t).simplify() for i in range(n)]

#LE1 = sp.diff(L, the1) - sp.diff(sp.diff(L, the1_d), t).simplify()
#LE2 = sp.diff(L, the2) - sp.diff(sp.diff(L, the2_d), t).simplify()

print("Solving Lagrangian...")
#sols = sp.solve([LE1, LE2], (the1_dd, the2_dd), simplify=False, rational=False)
sols = sp.solve([LE[i] for i in range(n)], [theta_dd[i] for i in range(n)], simplify=False, rational=False)

# Convert two second order ode's to four first order
args = [t,g]+m+l+theta+theta_d
acceleration = [sp.lambdify([args], sols[theta_dd[i]]) for i in range(n)]
#dz1dt_f = sp.lambdify(args, sols[theta_dd[0]])
#dz2dt_f = sp.lambdify(args, sols[theta_dd[1]])
#dz1dt_f = sp.lambdify((t,g,m1,m2,L1,L2,the1,the2,the1_d,the2_d), sols[the1_dd])
#dz2dt_f = sp.lambdify((t,g,m1,m2,L1,L2,the1,the2,the1_d,the2_d), sols[the2_dd])

print("Beginning Simulation.")

pg.init()
screen_width = 600
screen_height = 600
screen = pg.display.set_mode((screen_width,screen_height))
trail = pg.Surface(screen.get_size())
trail.set_colorkey((0,0,0))
trail.fill((0,0,0))

angles = [np.pi/2] + [0]*(n-1)
angular_velocities = [0]*n
angular_accelerations = [0]*n

g = -9.8 # Gravity
x2p = -1
y2p = -1
time_step = 1/60
framerate = 120

start_x = screen_width//2
start_y = 200
ppm = 100 # Pixels per meter (Used for drawing)

clock = pg.time.Clock()
time = 0

while True:
    clock.tick(framerate)
    screen.fill((0,0,0))

    #a1a = dz1dt_f(time, g, m1, m2, l1, l2, a1, a2, a1v, a2v)
    #a2a = dz2dt_f(time, g, m1, m2, l1, l2, a1, a2, a1v, a2v)
    args = [time, g]+masses+lengths+angles+angular_velocities
    angular_accelerations = [acceleration[i](args) for i in range(n)]
    
    angular_velocities = [angular_velocities[i] + angular_accelerations[i] * time_step for i in range(n)]
    angles = [angles[i] + angular_velocities[i] * time_step for i in range(n)]
    #angular_velocities[0] += angular_accelerations[0] * time_step
    #angular_velocities[1] += angular_accelerations[1] * time_step
    #angles[0] += angular_velocities[0] * time_step
    #angles[1] += angular_velocities[1] * time_step    
    #a1v += a1a * time_step
    #a2v += a2a * time_step
    #a1 += a1v * time_step
    #a2 += a2v * time_step

    # Convert angles to screen coordinates
    draw_x = [int(start_x+lengths[0]*ppm*np.sin(angles[0]))]
    draw_y = [int(start_y-lengths[0]*ppm*np.cos(angles[0]))]
    for i in range(1,n):
        draw_x.append(int(draw_x[i-1]+lengths[i]*ppm*np.sin(angles[i])))
        draw_y.append(int(draw_y[i-1]-lengths[i]*ppm*np.cos(angles[i])))
    #x = int(startx+l1*ppm*np.sin(a1))
    #y = int(starty-l1*ppm*np.cos(a1))
    #x2 = int(x+l2*ppm*np.sin(a2))
    #y2 = int(y-l2*ppm*np.cos(a2))

    # Draw trail
    if x2p != -1: # Do not draw first unassigned point
        pg.draw.line(trail, (255,255,255), (draw_x[-1],draw_y[-1]), (x2p,y2p))
    trail.fill((255,254,254,254), special_flags=pg.BLEND_RGBA_MULT)
    screen.blit(trail, (0,0))
    
    # Draw calls
    
    ot = (start_x,start_y)

    for to in zip(draw_x,draw_y):
        pg.draw.line(screen, (255,255,255), ot, to)
        pg.draw.circle(screen, (255,255,255), to, 8)
        ot = to

    # Previous points (used for trail)
    x2p = draw_x[-1]
    y2p = draw_y[-1]

    time += time_step
    pg.display.update() 