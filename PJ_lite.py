#!/usr/bin/python
# PJ_lite.py
"""
    Copyright (C) 2010  Peter Hewitt

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

"""
import g,utils,pygame,gtk,sys,jigsaw,buttons

class PJ_lite:
    
    def __init__(self):
        self.success=0
        self.journal=True # set to False if we come in via main()
        self.jigsaw_n=0

    def display(self,wait=False):
        if g.state==1:
            self.menu_display()
            #utils.display_number(g.success,(g.sx(.2),g.sy(.15)),g.font2,utils.ORANGE)
        else:
            if self.pj.complete():
                g.screen.blit(g.bgd,(g.sx(0),0))
                
            else:
#                g.screen.fill((g.red,g.green,g.blue))
                g.screen.fill(utils.CYAN)
            self.pj.draw()
            buttons.draw()
            utils.display_number(g.success,(g.sx(.2),g.sy(.3)),g.font1,utils.ORANGE)

    def menu_display(self):
        g.screen.fill(utils.CYAN)
        w=g.menu[0].get_width(); h=g.menu[0].get_height()
        dx=g.sy(.22); dy=g.sy(.1); y0=dy
        y=y0; ind=0
        for r in range(5):
            x=dx
            for c in range(4):
                g.screen.blit(g.menu[ind],(x,y))
                ind+=1
                if ind==len(g.menu): return
                x+=w+dx
            y+=h+dy
                                 
    def menu_click(self):
        w=g.menu[0].get_width(); h=g.menu[0].get_height()
        dx=g.sy(.22); dy=g.sy(.1); y0=dy
        y=y0; n=0
        for r in range(5):
            x=dx
            for c in range(4):
                n+=1
                if utils.mouse_in(x,y,x+w,y+h):
                    self.jigsaw_n=n; g.state=2
                    g.screen.fill(utils.CYAN)
                    utils.centre_blit(g.screen,g.wait,(g.sx(16),g.sy(11)))
                    pygame.display.flip()
                    return
                x+=w+dx
            y+=h+dy
        
    def setup(self):
        self.menu_bu.on()
        return self.pj.setup(self.jigsaw_n)

    def run(self):
        g.init()
        g.journal=self.journal
        if not self.journal:
            utils.load(); self.success=g.success
        else:
            g.success=self.success
        x=g.sx(3); y=g.sy(1.8)
        self.menu_bu=buttons.Button("menu",(x,y)); self.menu_bu.off()
        self.pj=jigsaw.Jigsaw()
        going=True
        while going:
            ms=pygame.time.get_ticks()
            g.mx,g.my=pygame.mouse.get_pos()
            # Pump GTK messages.
            while gtk.events_pending():
                gtk.main_iteration()

            # Pump PyGame messages.
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    if not self.journal: utils.save()
                    going=False
                elif event.type == pygame.MOUSEMOTION:
                    g.redraw=True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    g.redraw=True
                    if event.button==2: # centre button
                        g.version_display=not g.version_display; break
                    elif event.button==1: # left button
                        if g.state==3:
                            bu=buttons.check() 
                            if bu!='': g.state=1; break
                    if g.state==1:
                        self.menu_click()
                        if g.state==2:
                            if not self.setup(): going=False; break
                            g.state=3
                    elif g.state==3:
                        self.pj.click()
            if not going: break
            if g.redraw:
                self.display()
                if g.version_display: utils.version_display()
                if self.pj.carry:
                    g.screen.blit(g.negative,(g.mx,g.my))
                else:
                    g.screen.blit(g.pointer,(g.mx,g.my))
                pygame.display.flip()
                g.redraw=False
            self.success=g.success
            g.clock.tick(40)
            d=pygame.time.get_ticks()-ms; g.frame_rate=int(1000/d)

if __name__=="__main__":
    pygame.init()
    pygame.display.set_mode((800,600))
    game=PJ_lite()
    game.journal=False
    game.run()
    pygame.display.quit()
    pygame.quit()
    sys.exit(0)
