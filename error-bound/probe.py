#!/usr/bin/env python3
"""Estimate the achievable Float32-vs-Float64 error per kernel via numpy sampling,
so we can pick a reachable epsilon. float32 ops stay float32 (numpy); float64 via
Python float. err = |float(f32) - f64|. Reports median and max over random inputs."""
import numpy as np, random, statistics as st
f32 = np.float32

def rigidBody1(F,v):
    x1,x2,x3=v; return -F(x1)*F(x2) - F(2.0)*F(x2)*F(x3) - F(x1) - F(x3)
def rigidBody2(F,v):
    x1,x2,x3=(F(t) for t in v)
    return F(2.0)*x1*x2*x3 + F(3.0)*x3*x3 - x2*x1*x2*x3 + F(3.0)*x3*x3 - x2
def doppler1(F,v):
    u,vv,T=(F(t) for t in v); t1=F(331.4)+F(0.6)*T
    return (-t1*vv)/((t1+u)*(t1+u))
def verhulst(F,v):
    x=F(v[0]); return (F(4.0)*x)/(F(1.0)+x/F(1.11))
def predatorPrey(F,v):
    x=F(v[0]); xk=x/F(1.11); return (F(4.0)*x*x)/(F(1.0)+xk*xk)
def turbine1(F,v):
    vv,w,r=(F(t) for t in v); wr2=w*w*r*r
    return F(3.0)+F(2.0)/(r*r) - F(0.125)*(F(3.0)-F(2.0)*vv)*wr2/(F(1.0)-vv) - F(4.5)
def sine(F,v):
    x=F(v[0]); return x - (x*x*x)/F(6.0) + (x*x*x*x*x)/F(120.0) - (x*x*x*x*x*x*x)/F(5040.0)
def sqroot(F,v):
    y=F(v[0]); return F(1.0)+F(0.5)*y-F(0.125)*y*y+F(0.0625)*y*y*y-F(0.0390625)*y*y*y*y
def sineOrder3(F,v):
    z=F(v[0]); return F(0.954929658551372)*z - F(0.12900613773279798)*(z*z*z)

B = {
 "rigidBody1":(rigidBody1,[(-15,15)]*3),"rigidBody2":(rigidBody2,[(-15,15)]*3),
 "doppler1":(doppler1,[(-100,100),(20,20000),(-30,50)]),
 "verhulst":(verhulst,[(0.1,0.3)]),"predatorPrey":(predatorPrey,[(0.1,0.3)]),
 "turbine1":(turbine1,[(-4.5,-0.3),(0.4,0.9),(3.8,7.8)]),
 "sine":(sine,[(-1.57079632679,1.57079632679)]),"sqroot":(sqroot,[(0,1)]),
 "sineOrder3":(sineOrder3,[(-2,2)]),
}
random.seed(1)
for name,(fn,rng) in B.items():
    errs=[]
    for _ in range(200000):
        ins=[f32(random.uniform(lo,hi)) for lo,hi in rng]   # float32 inputs
        e=abs(float(fn(f32,ins)) - fn(float,[float(i) for i in ins]))
        errs.append(e)
    errs.sort()
    print(f"  {name:13s} median={st.median(errs):.3e}  p99={errs[int(len(errs)*0.99)]:.3e}  max={errs[-1]:.3e}")
