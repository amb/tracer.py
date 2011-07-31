import pygame
import random
import math
from time import time

EPSILON = 0.0000001
rr = random.random

class vec3():
    def __init__(self, x, y, z): self.x, self.y, self.z = float(x), float(y), float(z)
    def __add__(self, b): return vec3(self.x+b.x,self.y+b.y,self.z+b.z)
    def __sub__(self, b): return vec3(self.x-b.x,self.y-b.y,self.z-b.z)    
    def __mul__(self, b): return vec3(self.x*b.x,self.y*b.y,self.z*b.z)
    def __neg__(self): return vec3(-self.x, -self.y, -self.z)
    def __str__(self): return "("+repr(self.x)+","+repr(self.y)+","+repr(self.z)+")"
    def vec(self): return vec3(self.x, self.y, self.z)
    def vect(self): return (self.x, self.y, self.z)
    def scale(self, a): return vec3(self.x*a,self.y*a,self.z*a)
    def len(self): return math.sqrt(self.len2())
    def len2(self): return self.x*self.x + self.y*self.y + self.z*self.z
    def dot(self, b): return self.x*b.x+self.y*b.y+self.z*b.z
    def cross(self, b): return vec3(self.y*b.z - self.z*b.y, 
                                    self.z*b.x - self.x*b.z,
                                    self.x*b.y - self.y*b.x)
    def normalize(self): return (lambda x: vec3(0,0,0) if x == 0 else self.scale(1/x))(self.len())
    def clamp1(self): self.x,self.y,self.z = map(lambda x: 1.0 if x>1.0 else x, self.vect())

class Material():
    def __init__(self, absorb, emit, reflect, transparency):
        self.absorbtion = absorb
        self.emission = emit
        self.reflection = reflect
        self.transparency = transparency

class Ray():
    def __init__(self, origin, direction, caster=None):
        self.origin = origin
        self.direction = direction
        self.caster = caster

class Primitive3D():
    index = 0
    def __init__(self,material):
        self.material = material
        self.index = Primitive3D.index
        Primitive3D.index += 1
    
    def test(self, ray):
        raise "Primitive 3D object undefined."
        
class Sphere(Primitive3D):
    def __init__(self,c,r,mat): 
        Primitive3D.__init__(self, mat)
        
        self.center = c     
        self.radius = r
        
    def get_normal(self, loc):
        return (loc-self.center).normalize()
        
    def test(self, ray): 
        ro = self.center-ray.origin
        tm = ro.dot(ray.direction)
        if tm < 0: return None
        tp = ray.direction.scale(tm)
        d2 = ro.len2()-tp.len2()
        r2 = self.radius * self.radius
        if d2 < r2: # and ro.len() > self.radius: 
            #origin outside
            t2 = math.sqrt(r2 - d2)
            pv = tp - ray.direction.scale(t2)
            return pv
        return None

class Triangle(Primitive3D):
    def __init__(self,a,b,c,mat): 
        Primitive3D.__init__(self, mat)
        
        self.a = vec3(a.x,a.y,a.z)
        self.b = vec3(b.x,b.y,b.z)
        self.c = vec3(c.x,c.y,c.z)     
        
        self.edge1 = self.b - self.a
        self.edge2 = self.c - self.a
        
        self.tangent = self.edge1.normalize()
        self.normal = self.tangent.cross(self.edge2).normalize()
        
    def get_normal(self, loc):
        return self.normal # triangles are easy
        
    def test(self, ray): 
        pvec = ray.direction.cross(self.edge2)
        det = self.edge1.dot(pvec)
        if -0.000001 < det < 0.000001: return None
        
        inv_det = 1.0/det
        tvec = ray.origin - self.a
        u = tvec.dot(pvec) * inv_det
        if u < 0.0 or u > 1.0: return None
        
        qvec = tvec.cross(self.edge1)
        v = ray.direction.dot(qvec) * inv_det
        if v < 0.0 or (u + v) > 1.0: return None
        
        t = self.edge2.dot(qvec) * inv_det
        return (ray.direction.scale(t))

class Scene():
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
    
    mb_basic = Material(c_white, c_black, 1.0, 0.0)
    mb_light = Material(c_white, c_white, 0.0, 0.0)
    mb_blue  = Material(c_blue , c_black, 1.0, 0.0)
    mb_red   = Material(c_red  , c_black, 1.0, 0.0)
    mb_green = Material(c_green, c_black, 1.0, 0.0)
    mb_black = Material(c_black, c_black, 1.0, 0.0)

    """
    mb_basic = Material(c_white, c_white, 1.0, 0.0)
    mb_light = Material(c_white, c_white, 0.0, 0.0)
    mb_blue  = Material(c_blue , c_blue, 1.0, 0.0)
    mb_red   = Material(c_red  , c_red, 1.0, 0.0)
    mb_green = Material(c_green, c_green, 1.0, 0.0)
    mb_black = Material(c_black, c_black, 1.0, 0.0)
    """
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
    world.add(Triangle(vec3(-50,-50,100),vec3(50,50,100),vec3(50,-50,100),mb_basic))
    world.add(Triangle(vec3(-50,-50,100),vec3(-50,50,100),vec3(50,50,100),mb_basic))
    
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
    res = (ray.direction.scale(100000), None)
    for o in w.objects:
        if o == ray.caster: continue
        t = o.test(ray)
        if t != None:
            if t.len2() < res[0].len2():
                res = (t, o)                
    return res

    """    
        # calculate reflection
        norm = o.get_normal(its)
        vpar = norm.scale(norm.dot(res[0])*2) 
        reflection = res[0] - vpar
        reflection = reflection.normalize()
"""
def trace(w,ray,depth):
    res = raycast(w,ray)

    # collision with ray and object
    if res[1] != None:
        its,o = res[0]+ray.origin, res[1] # intersection location
        
        amount = 100*depth
        # random ray
        refc = vec3(0,0,0)
        if depth > 0:
            for i in xrange(amount):
                
                pr1 = math.pi * 2.0 * random.random()
                sr2 = math.sqrt(random.random())
                x = (math.cos(pr1) * sr2)
                y = (math.sin(pr1) * sr2)
                z = math.sqrt(1.0 - (sr2 * sr2))
                
                normal = o.normal
                tangent = o.tangent
                #if normal.dot(its) < 0.0:
                #    normal = -normal
                out_direction = (tangent.scale(x)) + (normal.cross(tangent).scale(y)) + (normal.scale(z))
                
                """
                x = random.random()*2-1
                y = random.random()*2-1
                z = random.random()*2-1
                
                out_direction = vec3(x,y,z).normalize()
                """
                
                refc = refc + trace(w,Ray(its,out_direction,o),depth-1)  

        if depth > 0: refc = refc.scale(1.0/amount)
        l=res[0].len2()
        if l>0: refc.scale(1000.0/l)
        return o.material.emission + refc * o.material.absorbtion

    # default for no object collision
    return vec3(0,0,0)

def render_world(wrd, w, h, skip): 
    global rays
    
    sw,sh=w/skip,h/skip

    # color 
    pic = [vec3(0.0,0.0,0.0)]*sw*sh
    
    stime = time()
                  
    for i in xrange(sw):
        if i%10 == 0: print (i*skip)*100/w
        for j in xrange(sh):
            x,y = i*skip/2-w/4-0.01, j*skip/2-h/4
            eyeray = Ray(vec3(0,0,-110), vec3(x,y,300).normalize())
            pic[i+j*sw] = trace(world,eyeray,1)
            
    etime = time()

    pygame.init()
    screen = pygame.display.set_mode((w, h))
    
    print "done."
    print "rays:",rays, "in", etime-stime, "=", int(float(rays)/(etime-stime)), "rays per second."
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
render_world(world, 512, 512, 8)
