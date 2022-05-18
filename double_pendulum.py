from pygame import *
from math import *

init()
screen_width = 600
screen_height = 600
screen = display.set_mode((screen_width,screen_height))
trail = Surface(screen.get_size())
trail.set_colorkey((0,0,0))
trail.fill((0,0,0))

# Initial acceleration, velocity, and position values 
a1a = 0
a2a = 0
a1v = 0
a2v = 0
a1 = pi/2
a2 = 0

l1 = 125 # Length of first arm
l2 = 125 # Length of second arm
m1 = 10 # Mass of first 'weight'
m2 = 10 # Mass of second 'weight'
g = -0.98 # Gravity
x2p = -1
y2p = -1

startx = screen_width//2
starty = 200
clock = time.Clock()
while True:
    clock.tick(60)
    screen.fill((0,0,0))
    # Angle derivatives with repsect to time^2. (Angular acceleration)
    a1a = ( -g*(2*m1+m2)*sin(a1)-m2*g*sin(a1-2*a2)-2*sin(a1-a2)*m2*(a2v*a2v*l2+a1v*a1v*l1*cos(a1-a2)) ) / ( l1*(2*m1+m2-m2*cos(2*a1-2*a2)) )
    a2a = ( 2*sin(a1-a2)*(a1v*a1v*l1*(m1+m2)+g*(m1+m2)*cos(a1)+a2v*a2v*l2*m2*cos(a1-a2)) ) / ( l2*(2*m1+m2-m2*cos(2*a1-2*a2)) )
    
    a1v += a1a
    a2v += a2a
    a1 += a1v
    a2 += a2v

    x = int(startx+l1*sin(a1))
    y = int(starty-l1*cos(a1))
    x2 = int(x+l2*sin(a2))
    y2 = int(y-l2*cos(a2))

    if x2p != -1: # Don't draw the first non-assigned point
        draw.line(trail, (100,100,100), (x2,y2), (x2p,y2p))
    screen.blit(trail, (0,0)) # Trail
    
    # Draw arms
    draw.line(screen, (255,255,255), (startx,starty), (x,y))
    draw.line(screen, (255,255,255), (x,y), (x2,y2))
    # Draw 'weights'
    draw.circle(screen, (255,255,255), (x,y), m1)
    draw.circle(screen, (255,255,255), (x2,y2), m2)

    # Previous points, used for trail
    x2p = x2
    y2p = y2

    display.update() 
quit()
