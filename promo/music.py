"""Soft, clean promo bed: plucked arpeggios over a warm pad, light tick. Original composition, generated with numpy."""
import numpy as np, sys, wave
SR=44100
def note(f,dur,vel=1,bright=1.0):
    t=np.arange(int(SR*dur))/SR
    env=np.exp(-t*3.2)*(1-np.exp(-t*400))
    w=np.sin(2*np.pi*f*t)+.35*bright*np.sin(2*np.pi*2*f*t)*np.exp(-t*6)+.12*np.sin(2*np.pi*3*f*t)*np.exp(-t*9)
    return (w*env*vel).astype(np.float32)
def pad(freqs,dur):
    t=np.arange(int(SR*dur))/SR
    out=np.zeros_like(t)
    for f in freqs:
        for d in (-0.4,0.4): out+=np.sin(2*np.pi*(f+d)*t)*.5+.15*np.sin(2*np.pi*(f*2+d)*t)
    a=np.minimum(1,t/1.2)*np.minimum(1,(dur-t)/1.5)
    return out/len(freqs)*a*.14
def mk(total,seed=1,bpm=96):
    rng=np.random.default_rng(seed)
    N=int(SR*total); mix=np.zeros(N,np.float32)
    beat=60/bpm
    # progression (Hz): Cmaj7 - Am7 - Fmaj7 - G
    prog=[[261.63,329.63,392.0,493.88],[220.0,261.63,329.63,392.0],[174.61,220.0,261.63,329.63],[196.0,246.94,293.66,392.0]]
    bar=beat*4; t=0; k=0
    while t<total:
        ch=prog[k%4]; p=pad([f/2 for f in ch[:3]],bar+.5); i0=int(t*SR); seg=p[:max(0,N-i0)]; mix[i0:i0+len(seg)]+=seg
        # 8 eighth-note plucks per bar, arpeggio with gentle variation
        order=[0,2,1,3,2,0,3,1]
        for j in range(8):
            tt=t+j*beat/2
            if tt>=total: break
            f=ch[order[j]]*(2 if rng.random()<.25 else 1)
            v=.55 if j%2==0 else .38
            n=note(f,1.4,v,bright=.9); i=int(tt*SR); s=n[:max(0,N-i)]; mix[i:i+len(s)]+=s
        # soft tick on 2 and 4
        for j in (1,3):
            tt=t+j*beat
            if tt>=total: break
            i=int(tt*SR); L=int(SR*.06); x=rng.standard_normal(L)*np.exp(-np.arange(L)/SR*180)*.08
            s=x[:max(0,N-i)]; mix[i:i+len(s)]+=s.astype(np.float32)
        t+=bar; k+=1
    # simple echo
    d=int(SR*beat*.75); e=np.zeros_like(mix); e[d:]=mix[:-d]*.22; mix+=e
    # fade in/out
    tt=np.arange(N)/SR; mix*=np.minimum(1,tt/.6)*np.minimum(1,np.maximum(0,(total-tt)/2.0))
    mix/=max(1e-6,np.abs(mix).max()); mix*=.7
    return mix
if __name__=='__main__':
    total=float(sys.argv[1]); out=sys.argv[2]; seed=int(sys.argv[3]) if len(sys.argv)>3 else 1
    m=mk(total,seed)
    with wave.open(out,'w') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m*32767).astype(np.int16).tobytes())
