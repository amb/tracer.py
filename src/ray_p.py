import profile
import pstats

import operator
import random
import math
from time import time

def vec3(x,y,z): return (float(x),float(y),float(z))
def vc_add(a,b): return (a[0]+b[0],a[1]+b[1],a[2]+b[2])
def vc_sub(a,b): return (a[0]-b[0],a[1]-b[1],a[2]-b[2])
def vc_mul(a,b): return (a[0]*b[0],a[1]*b[1],a[2]*b[2])
def vc_neg(a): return (-a[0],-a[1],-a[2])
def vc_scl(a,b): return (a[0]*b,a[1]*b,a[2]*b)
def vc_len2(a): return a[0]*a[0] + a[1]*a[1] + a[2]*a[2]
def vc_len(a): return math.sqrt(vc_len2(a))
def vc_dot(a,b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def vc_crs(a, b): return (a[1]*b[2] - a[2]*b[1],         
                          a[2]*b[0] - a[0]*b[2],
                          a[0]*b[1] - a[1]*b[0])
def vc_nrm(a): return (lambda x: (0,0,0) if x == 0 else vc_scl(a, 1/x))(vc_len(a))
def vc_cl1(a): (map(lambda x: 1.0 if x>1.0 else x, a))

class Material(object):
    def __init__(self, absorb, emit, transparency):
        self.absorbtion = absorb
        self.emission = emit
        self.transparency = transparency

class Ray(object):
    def __init__(self, origin, direction, caster=None):
        self.origin = origin
        self.direction = direction
        self.caster = caster

class Primitive3D(object):
    index = 0
    def __init__(self,material):
        self.material = material
        self.index = Primitive3D.index
        Primitive3D.index += 1
    
    def test(self, ray):
        raise "Primitive 3D object undefined."

class Triangle(Primitive3D):
    def __init__(self,a,b,c,mat): 
        Primitive3D.__init__(self, mat)
        
        self.a = a
        self.b = b
        self.c = c 
        
        self.edge1 = vc_sub(self.b, self.a)
        self.edge2 = vc_sub(self.c, self.a)
        
        self.tangent = vc_nrm(self.edge1)
        self.normal = vc_nrm(vc_crs(self.tangent, self.edge2))
        
    def get_normal(self, loc):
        return self.normal # triangles are easy
        
    def test(self, ray): 
        pvec = vc_crs(ray.direction, self.edge2)
        det = vc_dot(self.edge1, pvec)
        if -0.000001 < det < 0.000001: return None
        
        inv_det = 1.0/det
        tvec = vc_sub(ray.origin, self.a)
        u = vc_dot(tvec, pvec) * inv_det
        if u < 0.0 or u > 1.0: return None

        qvec = vc_crs(tvec, self.edge1)
        v = vc_dot(ray.direction, qvec) * inv_det
        if v < 0.0 or (u + v) > 1.0: return None

        t = vc_dot(self.edge2, qvec) * inv_det
        return (vc_scl(ray.direction,t))

class Scene(object):
    def __init__(self):
        self.objects = []
        self.obj_amount = 0
        
    def add(self, obj):
        obj.index = self.obj_amount
        self.objects.append(obj)
        self.obj_amount += 1
       
def create_world():
    c_white = vec3(1.0, 1.0, 1.0)
    c_blue  = vec3(0.5, 0.5, 1.0)
    c_red   = vec3(1.0, 0.5, 0.5)
    c_black = vec3(0.0, 0.0, 0.0)
    c_green = vec3(0.5, 1.0, 0.5)
    
    mb_basic = Material(c_white, c_black, 0.0)
    mb_light = Material(c_white, c_white, 0.0)
    mb_blue  = Material(c_blue , c_black, 0.0)
    mb_red   = Material(c_red  , c_black, 0.0)
    mb_green = Material(c_green, c_black, 0.0)

    world = Scene()

    #-- bottom
    world.add(Triangle(vec3(-50,50,100),vec3(-50,50,0),vec3(50,50,100),mb_blue))
    world.add(Triangle(vec3(50,50,0),vec3(50,50,100),vec3(-50,50,0),mb_blue))
    
    #-- top
    world.add(Triangle(vec3(-50,-50,0),vec3(-50,-50,100),vec3(50,-50,100),mb_basic))
    world.add(Triangle(vec3(50,-50,100),vec3(50,-50,0),vec3(-50,-50,0),mb_basic))
    
    #-- top light
    world.add(Triangle(vec3(-25,-49,25),vec3(-25,-49,75),vec3(25,-49,75),mb_light))
    world.add(Triangle(vec3(25,-49,75),vec3(25,-49,25),vec3(-25,-49,25),mb_light))
    
    #-- back
    world.add(Triangle(vec3(-50,-50,100),vec3(50,50,100),(50,-50,100),mb_basic))
    world.add(Triangle(vec3(-50,-50,100),vec3(-50,50,100),(50,50,100),mb_basic))
    
    #-- left
    world.add(Triangle(vec3(-50,-50,100),vec3(-50,-50,0),vec3(-50,50,100), mb_red))
    world.add(Triangle(vec3(-50,50,100),vec3(-50,-50,0),vec3(-50,50,0), mb_red))
    
    #-- right
    world.add(Triangle(vec3(50,-50,0),vec3(50,-50,100),vec3(50,50,100), mb_green))
    world.add(Triangle(vec3(50,-50,0),vec3(50,50,100),vec3(50,50,0), mb_green))
    
    return world

rays = 0

def raycast(w,ray):
    global rays
    rays += 1
    vec, obj = vc_scl(ray.direction, 100000), None
    vecl = vc_len2(vec)
    for o in w.objects:
        if o.index == ray.caster: continue
        t = o.test(ray)
        if t:
            if vc_len2(t) < vecl:
                vec,obj = t,o  
                vecl = vc_len2(vec)             
    return (vec,obj)

def trace(w,ray,depth):
    collision_vec, collision_obj = raycast(w,ray)
    if collision_obj:
        its = vc_add(collision_vec, ray.origin) # intersection location
        amount = 4*depth
        o = collision_obj
        
        # random ray
        refc = vec3(0,0,0)
        if depth > 0:
            for _ in xrange(amount):
                
                pr1 = math.pi * 2.0 * random.random()
                sr2 = math.sqrt(random.random())
                x = (math.cos(pr1) * sr2)
                y = (math.sin(pr1) * sr2)
                z = math.sqrt(1.0 - (sr2 * sr2))
                if vc_dot(o.normal, its) < 0.0:
                    o.normal = vc_neg(o.normal)
                """
                out_direction = (o.tangent.scale(x)) + 
                                (o.normal.cross(o.tangent).scale(y)) + 
                                (o.normal.scale(z))
                """             
                out_direction = vc_add(vc_scl(o.tangent,x),
                       vc_add(vc_scl(vc_crs(o.normal,o.tangent),y),
                       vc_scl(o.normal,z)))
                
                """
                x = random.random()*2-1
                y = random.random()*2-1
                z = random.random()*2-1
                out_direction = vc_nrm((x,y,z))
                """
                
                refc = vc_add(refc, trace(w,Ray(its,out_direction,o.index),depth-1)) 

        if depth > 0: vc_scl(refc, 1.0/amount)
        l=vc_len2(collision_vec)
        if l>0: vc_scl(refc, 1000.0/l)
        return vc_add(o.material.emission, vc_mul(refc, o.material.absorbtion))

    return vec3(0,0,0) # no collision found

def render_world(wrd, w, h, skip): 
    global rays
    
    sw,sh=w/skip,h/skip

    # color 
    pic = [vec3(0,0,0)]*sw*sh
    
    stime = time()          
    for i in xrange(sw):
        if i%10 == 0: print (i*skip)*100/w
        for j in xrange(sh):
            x,y = i*skip/2-w/4-0.01, j*skip/2-h/4
            eyeray = Ray(vec3(0,0,-110), vc_nrm(vec3(x,y,300)))
            pic[i+j*sw] = trace(world,eyeray,2) 
    etime = time()

    print "done."
    print "rays:",rays, "in", etime-stime, "=", int(float(rays)/(etime-stime)), "rays per second."
    
    return (w,h,sw,sh,skip,pic)
    
def show_image(dt):
    import pygame
    w,h,sw,sh,skip,pic = dt
    pygame.init()
    screen = pygame.display.set_mode((w, h))
    for i in xrange(sw):
        for j in xrange(sh):
            c = pic[i+j*sw]
            c.clamp1()
            screen.fill((c.x*255,c.y*255,c.z*255), pygame.Rect(i*skip,j*skip,skip,skip))

    pygame.display.flip()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or \
             (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit(); 
                running = False
        pygame.time.delay(100)

world = create_world()
image = render_world(world, 512, 512, 4)
#show_image(image)
#profile.run('render_world(world, 512, 512, 8)')


