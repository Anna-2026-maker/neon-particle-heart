"""Reference Python implementation: assemble, rotate, explode and return."""
import math, random, pygame
from dataclasses import dataclass

WIDTH, HEIGHT, FPS = 1100, 760, 60
pygame.init(); screen=pygame.display.set_mode((WIDTH,HEIGHT)); clock=pygame.time.Clock()

@dataclass
class Particle:
    x:float; y:float; z:float; vx:float; vy:float; size:float

def heart_point(t,r):
    return 16*math.sin(t)**3*r, -(13*math.cos(t)-5*math.cos(2*t)-2*math.cos(3*t)-math.cos(4*t))*r

particles=[]
for _ in range(1100):
    t=random.random()*math.tau; r=math.sqrt(random.random()); x,y=heart_point(t,r); a=random.random()*math.tau
    particles.append(Particle(x,y,(random.random()-.5)*7,math.cos(a)*random.uniform(.7,3.7),math.sin(a)*random.uniform(.7,3.7)-1,random.uniform(.7,2.8)))

running=True
while running:
    for event in pygame.event.get():
        if event.type==pygame.QUIT: running=False
    screen.fill((3,2,4)); phase=(pygame.time.get_ticks()/1000)%8
    for p in particles:
        angle=(phase-1)*1.2 if 1<phase<3.2 else 0
        x=p.x*math.cos(angle)+p.z*math.sin(angle); y=p.y
        if 3.6<phase<5.2:
            e=(phase-3.6)/1.6; x+=p.vx*e*42; y+=p.vy*e*42+e*e*26
        pygame.draw.circle(screen,(255,30,175),(int(WIDTH/2+x*12),int(HEIGHT/2+y*12)),max(1,int(p.size)))
    pygame.display.flip(); clock.tick(FPS)
pygame.quit()
