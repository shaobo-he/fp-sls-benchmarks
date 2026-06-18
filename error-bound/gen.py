#!/usr/bin/env python3
"""Generate QF_FP error-bound benchmarks from the classic FPTaylor functions.

Each benchmark asks: is there an input (in the FPTaylor range) for which the
SAME expression computed in Float32 differs from its Float64 evaluation by more
than epsilon?  i.e.  exists x in [lo,hi] . |f32(x) - f64(x)| > eps
SAT  = a witness input whose single-precision round-off error exceeds eps.
The error is measured in Float64 (the float result is widened, then compared to
the double result). Inputs are Float32, range-constrained; constants are decimal
to_fp literals (accepted by z3/cvc5, and by fp-sls via z3-simplify preprocessing).
"""
import struct
RNE = "roundNearestTiesToEven"

class FP:
    def __init__(self, eb, sb): self.eb, self.sb = eb, sb
    def c(self, x):
        # Emit a constant as a *pure FP bit pattern* (to_fp from a bitvector of
        # the IEEE bits) -- NOT to_fp-from-real, which pulls in the Real sort
        # (not native QF_FP: fp-sls only handles it via z3 preprocessing, and
        # cvc5 rejects it). Matches the SMT-COMP griggio style.
        v = float(x)
        if (self.eb, self.sb) == (8, 24):
            bits = struct.unpack('<I', struct.pack('<f', v))[0]   # IEEE single
            return f"((_ to_fp 8 24) (_ bv{bits} 32))"
        if (self.eb, self.sb) == (11, 53):
            bits = struct.unpack('<Q', struct.pack('<d', v))[0]   # IEEE double
            return f"((_ to_fp 11 53) (_ bv{bits} 64))"
        raise ValueError(f"unsupported precision {self.eb},{self.sb}")
    def add(self,a,b): return f"(fp.add {RNE} {a} {b})"
    def sub(self,a,b): return f"(fp.sub {RNE} {a} {b})"
    def mul(self,a,b): return f"(fp.mul {RNE} {a} {b})"
    def div(self,a,b): return f"(fp.div {RNE} {a} {b})"
    def neg(self,a):   return f"(fp.neg {a})"

# --- FPTaylor expressions (transcribed verbatim from FPTaylor/benchmarks) ---
def rigidBody1(F,v):
    x1,x2,x3=v['x1'],v['x2'],v['x3']
    return F.sub(F.sub(F.sub(F.neg(F.mul(x1,x2)), F.mul(F.c("2.0"),F.mul(x2,x3))), x1), x3)
def rigidBody2(F,v):
    x1,x2,x3=v['x1'],v['x2'],v['x3']
    a=F.mul(F.c("2.0"),F.mul(x1,F.mul(x2,x3))); b=F.mul(F.c("3.0"),F.mul(x3,x3))
    cc=F.mul(x2,F.mul(x1,F.mul(x2,x3)));        d=F.mul(F.c("3.0"),F.mul(x3,x3))
    return F.sub(F.add(F.sub(F.add(a,b),cc),d), x2)
def doppler1(F,v):
    u,vv,T=v['u'],v['v'],v['T']
    t1=F.add(F.c("331.4"),F.mul(F.c("0.6"),T))
    return F.div(F.mul(F.neg(t1),vv), F.mul(F.add(t1,u),F.add(t1,u)))
def verhulst(F,v):
    x=v['x']; return F.div(F.mul(F.c("4.0"),x), F.add(F.c("1.0"),F.div(x,F.c("1.11"))))
def predatorPrey(F,v):
    x=v['x']; xk=F.div(x,F.c("1.11"))
    return F.div(F.mul(F.c("4.0"),F.mul(x,x)), F.add(F.c("1.0"),F.mul(xk,xk)))
def turbine1(F,v):
    vv,w,r=v['v'],v['w'],v['r']; wr2=F.mul(F.mul(w,w),F.mul(r,r))
    term=F.div(F.mul(F.mul(F.c("0.125"),F.sub(F.c("3.0"),F.mul(F.c("2.0"),vv))),wr2),F.sub(F.c("1.0"),vv))
    return F.sub(F.sub(F.add(F.c("3.0"),F.div(F.c("2.0"),F.mul(r,r))),term),F.c("4.5"))
def sine(F,v):
    x=v['x']; x2=F.mul(x,x); x3=F.mul(x2,x); x5=F.mul(x3,x2); x7=F.mul(x5,x2)
    return F.sub(F.add(F.sub(x,F.div(x3,F.c("6.0"))),F.div(x5,F.c("120.0"))),F.div(x7,F.c("5040.0")))
def sqroot(F,v):
    y=v['y']; y2=F.mul(y,y); y3=F.mul(y2,y); y4=F.mul(y3,y)
    return F.sub(F.add(F.sub(F.add(F.c("1.0"),F.mul(F.c("0.5"),y)),F.mul(F.c("0.125"),y2)),
                       F.mul(F.c("0.0625"),y3)), F.mul(F.c("0.0390625"),y4))
def sineOrder3(F,v):
    z=v['z']; z3=F.mul(F.mul(z,z),z)
    return F.sub(F.mul(F.c("0.954929658551372"),z), F.mul(F.c("0.12900613773279798"),z3))

# name -> (expr, {var:(lo,hi)}, default-epsilon)
BENCH = {
 # epsilon levels (probe.py, 20M samples): easy ~ median; hard ~ p99; vhard ~ 0.99*max
 # (vhard's witness is a near-worst-case input -- a needle, esp. for the 3-variable kernels).
 "rigidBody1":  (rigidBody1, {"x1":("-15","15"),"x2":("-15","15"),"x3":("-15","15")}, {"easy":"1e-6","hard":"3e-5","vhard":"1e-4"}),
 "rigidBody2":  (rigidBody2, {"x1":("-15","15"),"x2":("-15","15"),"x3":("-15","15")}, {"easy":"1e-5","hard":"2e-3","vhard":"9e-3"}),
 "doppler1":    (doppler1,   {"u":("-100","100"),"v":("20","20000"),"T":("-30","50")}, {"easy":"1e-6","hard":"1e-5","vhard":"3.8e-5"}),
 "verhulst":    (verhulst,   {"x":("0.1","0.3")}, {"easy":"1e-8","hard":"6e-8","vhard":"8.5e-8"}),
 "predatorPrey":(predatorPrey,{"x":("0.1","0.3")}, {"easy":"2e-9","hard":"3e-8","vhard":"4.8e-8"}),
 "turbine1":    (turbine1,   {"v":("-4.5","-0.3"),"w":("0.4","0.9"),"r":("3.8","7.8")}, {"easy":"1e-7","hard":"1e-6","vhard":"3.5e-6"}),
 "sine":        (sine,       {"x":("-1.57079632679","1.57079632679")}, {"easy":"1e-8","hard":"8e-8","vhard":"1.5e-7"}),
 "sqroot":      (sqroot,     {"y":("0","1")}, {"easy":"2e-8","hard":"1.5e-7","vhard":"2.3e-7"}),
 "sineOrder3":  (sineOrder3, {"z":("-2","2")}, {"easy":"1e-8","hard":"9e-8","vhard":"1.85e-7"}),
}

F32, F64 = FP(8,24), FP(11,53)
def widen(name): return f"((_ to_fp 11 53) {RNE} {name})"

def emit(name, eps):
    expr, ranges, _ = BENCH[name]
    L=[f"(set-info :smt-lib-version 2.6)", f"(set-logic QF_FP)",
       f"(set-info :source |Float32-vs-Float64 round-off error bound for the FPTaylor",
       f"  '{name}' kernel. SAT = an input in range whose single-precision error",
       f"  abs(f32 - f64) exceeds {eps} (measured in double). Generated; not hand-tuned.|)",
       f"(set-info :category \"crafted\")", f"(set-info :status sat)"]
    fvars={}; dvars={}
    for vn,(lo,hi) in ranges.items():
        L.append(f"(declare-const {vn} (_ FloatingPoint 8 24))")
        fvars[vn]=vn; dvars[vn]=f"{vn}d"
    for vn,(lo,hi) in ranges.items():
        L.append(f"(define-fun {vn}d () (_ FloatingPoint 11 53) {widen(vn)})")
    for vn,(lo,hi) in ranges.items():
        L.append(f"(assert (fp.geq {vn} {F32.c(lo)}))")
        L.append(f"(assert (fp.leq {vn} {F32.c(hi)}))")
    f32=expr(F32,fvars); f64=expr(F64,dvars)
    L.append(f"(define-fun f32 () (_ FloatingPoint 8 24) {f32})")
    L.append(f"(define-fun f64 () (_ FloatingPoint 11 53) {f64})")
    L.append(f"(define-fun err () (_ FloatingPoint 11 53) (fp.abs (fp.sub {RNE} {widen('f32')} f64)))")
    L.append(f"(assert (fp.gt err {F64.c(eps)}))")
    L.append("(check-sat)")
    return "\n".join(L)+"\n"

if __name__=="__main__":
    import sys, os
    out=sys.argv[1] if len(sys.argv)>1 else "."
    os.makedirs(out, exist_ok=True)
    for name,(_,_,eps) in BENCH.items():
        for level, e in eps.items():
            p=os.path.join(out, f"{name}_{level}.smt2")
            open(p,"w").write(emit(name, e))
            print("wrote", p)
