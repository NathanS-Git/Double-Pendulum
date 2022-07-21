import pygame as pg
import sympy as sp
import numpy as np

# -------------------
#  Pendulum values
# -------------------
masses = [2,2,2] # in kilograms
lengths = [1,1,1] # in meters
# -------------------

assert len(masses) == len(lengths), "Mass and rod counts do not match"
assert len(masses) >= 1, "Too few values"
assert all((mass > 0 for mass in masses)), "One or more masses are non-positive"
assert all((length > 0 for length in lengths)), "One or more lengths are non-positive"

n = len(lengths)

print("Obtaining Lagrangian equations...")

t, g = sp.symbols('t g')
m = [sp.symbols('m_{}'.format(i)) for i in range(n)]
l = [sp.symbols('l_{}'.format(i)) for i in range(n)]

# Obtain symbols for angle, angular velocity, and angular acceleration for sympy
theta = [sp.symbols(r'\theta_{}'.format(i), cls=sp.Function)(t) for i in range(n)]
theta_d = [sp.diff(angle, t) for angle in theta]
theta_dd = [sp.diff(velocity, t) for velocity in theta_d]

# Convert angles to cartesian coordinates for sympy energy calculation
x = [l[0]*sp.sin(theta[0])]
y = [-l[0]*sp.cos(theta[0])]
for i in range(1,n):
    x.append( x[i-1] + l[i]*sp.sin(theta[i]) )
    y.append( y[i-1] - l[i]*sp.cos(theta[i]) )

# Kinetic energy (T = 1/2(mv^2))
T = sum([sp.Rational(1,2)*m[i]*(sp.diff(x[i], t)**2 + sp.diff(y[i], t)**2) for i in range(n)])

# Potential energy (V = mgh)
V = sum([m[i]*g*y[i] for i in range(n)])

# Lagrangian
L = T-V

# Compute Euler-Lagrangian equations
LE = [sp.diff(L, theta[i]) - sp.diff(sp.diff(L, theta_d[i]), t).simplify() for i in range(n)]

# Solve for angular acceleration
print("Solving Lagrangian...")
sols = sp.solve([LE[i] for i in range(n)], [theta_dd[i] for i in range(n)], simplify=False, rational=False)

# Convert sympy function to python function
print("Converting to a python function...")
arguments = [t,g]+m+l+theta+theta_d
acceleration = [sp.lambdify([arguments], sols[theta_dd[i]]) for i in range(n)]

# Initialize renderer
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
time_step = 1/60
framerate = 120

start_x = screen_width//2
start_y = 200
x2p, y2p = -1, -1
ppm = 100 # Pixels per meter (Used for drawing)
mass_radius = 8

clock = pg.time.Clock()
time = 0

while True:
    clock.tick(framerate)
    screen.fill((0,0,0))

    args = [time, g]+masses+lengths+angles+angular_velocities
    angular_accelerations = [acceleration[i](args) for i in range(n)]
    
    angular_velocities = [angular_velocities[i] + angular_accelerations[i] * time_step for i in range(n)]
    angles = [angles[i] + angular_velocities[i] * time_step for i in range(n)]

    # Convert angles to screen coordinates
    draw_x = [int(start_x+lengths[0]*ppm*np.sin(angles[0]))]
    draw_y = [int(start_y-lengths[0]*ppm*np.cos(angles[0]))]
    for i in range(1,n):
        draw_x.append(int(draw_x[i-1]+lengths[i]*ppm*np.sin(angles[i])))
        draw_y.append(int(draw_y[i-1]-lengths[i]*ppm*np.cos(angles[i])))

    # Draw trail
    if x2p != -1: # Wait until 1 iteration has passed
        pg.draw.line(trail, (255,255,255), (draw_x[-1],draw_y[-1]), (x2p,y2p))
    trail.fill((245,230,230,255), special_flags=pg.BLEND_RGBA_MULT)
    screen.blit(trail, (0,0))
    
    # Draw pendulum
    ot = (start_x,start_y) # from
    for to in zip(draw_x,draw_y):
        pg.draw.line(screen, (255,255,255), ot, to)
        pg.draw.circle(screen, (255,255,255), to, mass_radius)
        ot = to

    # Previous points (used for trail)
    x2p = draw_x[-1]
    y2p = draw_y[-1]

    time += time_step
    pg.display.update() 