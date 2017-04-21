# pj.py
import os,utils,g,pygame,random

NR=3; NC=4

class Piece:
    def __init__(self,ind):
        self.ind=ind
        self.img=None
        self.mates=[] # list of pieces
        self.group=0
        self.cx0=0; self.cy0=0; self.cx=0; self.cy=0

class Jigsaw:
    def __init__(self):
        # next 3 lines layout dependent
        self.rect=pygame.Rect(g.sx(8),g.sy(4.6),g.sy(23),g.sy(12.6))
        d=g.sy(.48); x1,y1,w,h=self.rect
        self.frame_rect=pygame.Rect(x1-d,y1-d,w+2*d,h+2*d)
        self.total=NC*NR; self.margin=g.sy(.8); self.next_group=0
        self.pieces=[]; self.final=None
        for ind in range(self.total):
            pce=Piece(ind); self.pieces.append(pce)
        self.carry=None; self.dx=0; self.dy=0
        n=0
        for r in range(1,NR+1):
            for c in range(1,NC+1):
                mates=[]
                if r>1: mates.append(self.pieces[n-NC])
                if r<NR: mates.append(self.pieces[n+NC])
                if c>1: mates.append(self.pieces[n-1])
                if c<NC: mates.append(self.pieces[n+1])
                self.pieces[n].mates=mates
                n+=1
        s='1'; self.bcx=g.sx(25.1); self.bcy=g.sy(10.1)
        if g.journal: s=''; self.bcx=g.sx(22); self.bcy=g.sy(7.5)

    def setup(self,pj_n):
        self.pj_n=pj_n
        random.shuffle(self.pieces)
        self.carry=None; self.next_group=0
        fname=os.path.join('data',str(pj_n),'pieces.txt')
        try:
            f=open(fname, 'r')
        except:
            print 'Peter says unable to load '+fname
            return False
        for i in range(4): ignore=int(f.readline())
        n=0; factor=32.0/1200.0
        for ind in range(self.total):
            n+=1
            pce=self.pce_from_index(ind)
            pce.cx0=g.sx(factor*int(f.readline()))
            pce.cy0=g.sy(factor*int(f.readline()))
            img=utils.load_image(str(n)+'.png',True,str(pj_n))
            if img==None: return False
            if img==None:
                print 'Peter says unable to load data/'+str(pj_n)+'/'+str(n)+'.png'
                return False
            pce.img=img
            pce.group=0
        try:
            g.red=int(f.readline())
            g.green=int(f.readline())
            g.blue=int(f.readline())
        except:
            pass
        f.close
        self.layout()
        self.final=None
        return True

    def draw(self):
        if self.complete():
            g.screen.blit(self.final,self.rect)
            g.screen.blit(g.frame,self.frame_rect)
        else:
            grey=100
            pygame.draw.rect(g.screen,(grey,grey,grey),self.rect,2)
            if self.carry!=None:
                self.carry.cx=g.mx+self.dx; self.carry.cy=g.my+self.dy
                if self.carry.group>0: self.align(self.carry)
            for pce in self.pieces:
                img=pce.img
                utils.centre_blit(g.screen,img,(pce.cx,pce.cy))

    def pce_from_index(self,ind):
        for pce in self.pieces:
            if pce.ind==ind: return pce
        
    def solve(self):
        for pce in self.pieces:
            pce.cx=pce.cx0+self.rect[0]+1
            pce.cy=pce.cy0+self.rect[1]+1
            pce.group=1

    def top(self,pce):
        self.pieces.remove(pce)
        self.pieces.append(pce)

    def top_gp(self,gp):
        lst=utils.copy_list(self.pieces)
        for pce in lst:
            if pce.group==gp: self.top(pce)

    def which(self):
        l=utils.copy_list(self.pieces)
        for i in range(self.total):
            pce=l.pop()
            img=pce.img
            if utils.mouse_on_img(img,(pce.cx,pce.cy)):
                if pce.group>0:
                    lst=utils.copy_list(self.pieces)
                    for pce1 in lst:
                        if pce1.group==pce.group: self.top(pce1)
                else:
                    self.top(pce)
                return pce
        return None

    def click(self):
        if self.complete(): return False #****
        if self.carry:
            pce=self.carry
            self.carry=None # put down
            if pce.group==0:
                self.check(pce)
            else: # check all members of group
                self.check(pce)
                looking=True
                for i in range(100): # no infinite loop possibility
                    looking=False
                    for pce1 in self.pieces:
                        if pce1.group==pce.group:
                            if self.check(pce1): looking=True
                    if not looking:break
                if looking: print '>>>> avoided loop'
            if pce.group>0: self.top_gp(pce.group)
            self.align(pce)
            return True
        pce=self.which()
        if pce==None: return False
        # pick up
        self.carry=pce; self.dx=pce.cx-g.mx; self.dy=pce.cy-g.my
        return True

    def check(self,pce0):
        tf=False
        for pce in pce0.mates:
            if (pce0.group==pce.group) and pce.group>0: # already in same group
                pass
            else:
                dx0=abs(pce.cx0-pce0.cx0); dy0=abs(pce.cy0-pce0.cy0)
                dx=abs(pce.cx-pce0.cx); dy=abs(pce.cy-pce0.cy)
                if abs(dx-dx0)<self.margin:
                    if abs(dy-dy0)<self.margin:
                        ok=True
                        # close enough - check if right place
                        dind=utils.sign(pce.ind-pce0.ind)
                        dx=utils.sign(pce.cx-pce0.cx)
                        dy=utils.sign(pce.cy-pce0.cy)
                        if abs(pce.ind-pce0.ind)==1: # same row
                            if dx<>dind: ok=False
                        else: # same column
                            if dy<>dind: ok=False
                        if ok:
                            tf=True
                            if pce.group==0:
                                if pce0.group==0:
                                    self.next_group+=1
                                    pce.group=self.next_group
                                    pce0.group=self.next_group
                                else:
                                    pce.group=pce0.group
                            else:
                                if pce0.group==0:
                                    pce0.group=pce.group
                                else: # two separate groups
                                    for pce1 in self.pieces:
                                        if pce1.group==pce0.group:
                                            pce1.group=pce.group
        return tf

    def align(self,pce0):
        gp0=pce0.group
        if gp0>0:
            dddx=pce0.cx-pce0.cx0; dddy=pce0.cy-pce0.cy0
            for pce in self.pieces:
                if pce.group==gp0 and (pce<>pce0):
                    ddx=pce.cx0-pce0.cx0; ddy=pce.cy0-pce0.cy0
                    dx=ddx; dy=ddy
                    pce.cx=pce0.cx0+dx+dddx
                    pce.cy=pce0.cy0+dy+dddy

    def complete(self):
        gp=0
        for pce in self.pieces:
            if pce.group==0: return False
            if gp==0:
                gp=pce.group
            else:
                if pce.group<>gp:return False
        if self.final==None:
            self.final=utils.load_image('final.jpg',False,str(self.pj_n))
            g.success+=1
            self.solve()
        return True

# hard coded for 12 piece PJ
    def layout(self):
        ind=0
        y=g.sy(2.2); x0=g.sx(3.2); dx=g.sy(6.4); dy=g.sy(4.4)
        for r in range(5):
            x=x0
            for c in range(5):
                if r==0 and c==0:
                    pass
                elif r>0 and r<4 and c>0:
                    pass
                else:
                    pce=self.pieces[ind]; pce.cx=x; pce.cy=y
                    ind+=1
                x+=dx
            y+=dy

    def debug(self):
        print '****'
        for p in self.pieces:
            print str(p.ind)+'-'+str(p.group),
        print

                    
                
            
        
        

            
            
        
