import pyxel as px
import function as func
import anim_menu as anim
import edit as edit
import random 

def update(self):
    func.detect(self)
    if px.btnp(px.MOUSE_BUTTON_LEFT) and self.state == "mouse":
        """print(px.mouse_x, px.mouse_y)"""
        for dipoles in self.dipoles_dict.values():
            if dipoles["type"] != "cable":
                if func.colisions(self.anchored_position, dipoles["hitbox"]):
                    a = dipoles[self.dipoles[dipoles["type"]]["key"]]
                    dipoles[self.dipoles[dipoles["type"]]["key"]] = (a + 1) if (self.dipoles[dipoles["type"]]["variant"]-1) > a else 0

    if px.btnp(px.KEY_J):
        self.br = True

    if self.br:
        func.branches(self)

    if self.state in ("move","cut","modify") and self.move_list == [] or self.move_list == [None]:
        for dipoles in self.dipoles_dict.values():

            if func.colisions(self.anchored_position, dipoles["hitbox"]):
                self.hitbox_show = dipoles["hitbox"]

    if self.state in ("annotate","cut"):
        for notes in self.annotation_list:

            if func.colisions(self.anchored_position, notes[3]):
                self.hitbox_show = notes[3]

    if px.btnp(px.MOUSE_BUTTON_LEFT) and 35 < px.mouse_x < 50 and 187 < px.mouse_y < 195 and not self.color_selection[0]:
        self.color_selection[0] = True
            
    elif px.btnp(px.MOUSE_BUTTON_LEFT) and 35 < px.mouse_x < 50 and 123 < px.mouse_y < 133 and self.color_selection[0]:
        self.color_selection[0] = False

    elif px.btnp(px.MOUSE_BUTTON_LEFT) and 344 < px.mouse_x < 349 and 178 < px.mouse_y < 192 and not self.color_selection[1]:
        self.color_selection[1] = True
            
    elif px.btnp(px.MOUSE_BUTTON_LEFT) and 292 < px.mouse_x < 296 and 178 < px.mouse_y < 192 and self.color_selection[1]:
        self.color_selection[1] = False
        
    '''on définie les zones permettant de changer l'état de la souris et d'autres fonctionalités hors de la zone 0'''
    if px.btnp(px.MOUSE_BUTTON_LEFT) and self.mouse_zone != 0:
        if 29 < px.mouse_x < 55 and 194 < px.mouse_y < 210 and not self.color_selection[0]:
            self.state = "trace"
            
        elif 54 < px.mouse_x < 76 and 191 < px.mouse_y < 210:
            self.state = "cut"

        elif 75 < px.mouse_x < 97 and 191 < px.mouse_y < 210:
            self.state = "move"

        elif 348 < px.mouse_x < 373 and ((7 < px.mouse_y < 204) if not self.battery else (35 < px.mouse_y < 204)):
            self.state = "drag"
        
        elif 133 < px.mouse_x < 169 and 0 < px.mouse_y < 17:
            self.vision = 1 - self.vision

        elif 174 < px.mouse_x < 195 and 0 < px.mouse_y < 17:
            self.state = "modify"

        elif 190 < px.mouse_x < 211 and 0 < px.mouse_y < 17:
            self.state = "annotate"

        elif 211 < px.mouse_x < 232 and 0 < px.mouse_y < 17:
            self.launcher = "save"

        elif 232 < px.mouse_x < 253 and 0 < px.mouse_y < 17:
            self.launcher = "title"

        elif 253 < px.mouse_x < 274 and 0 < px.mouse_y < 17:
            self.dipoles_dict = {}
            self.annotation_list = []
            self.state = "mouse"
            self.global_count = 0
            self.tension = 9

        elif 139 <= px.mouse_x <= 147 and 197 <= px.mouse_y <= 205:
            self.anchor = not self.anchor

        elif 180 <= px.mouse_x <= 188 and 197 <= px.mouse_y <= 205:
            self.tips = not self.tips

        elif 217 <= px.mouse_x <= 225 and 197 <= px.mouse_y <= 205:
            self.grid = not self.grid
            
    if px.btnp(px.MOUSE_BUTTON_RIGHT):
        self.state = "mouse"

    '''on vérifie dans quelle zone se situe la souris'''
    self.mouse_zone = func.zones(self,(px.mouse_x,px.mouse_y))
        
    '''si on clique dans la zone 0, on active la fonction qui va avec le state actuel'''
    if px.btnp(px.MOUSE_BUTTON_LEFT):
        if self.mouse_zone == 0 :
            if self.state not in ("modify","annotate") or (self.state == "annotate" and self.call_position == (0,0,None)):
                self.call_position = (self.anchored_position[0], self.anchored_position[1], self.state) #nous donne les coordonnées du début du clic et les conserves

            elif self.state == "modify" and not(260 <= px.mouse_x <= 330 and 178 <= px.mouse_y <= 194):
                self.call_position = (0,0,None)
                for dipoles in self.dipoles_dict.values():
                    if func.colisions(self.anchored_position, dipoles["hitbox"]):
                        self.call_position = (self.anchored_position[0], self.anchored_position[1], self.state)

            

            if self.state == "annotate":
                msg_list = ("faire un clic droit ou entrer \npour valider", "cliquer a nouveau sur une \nnote pour la modifier", "vous pouvez couper une note !")
                func.add_message(self,random.choice(msg_list), 5, 10)

                for index,notes in enumerate(self.annotation_list):
                    if func.colisions(self.anchored_position, notes[3]):

                        self.call_position = (notes[0], notes[1], "annotate") #on récupère la position de la note à modifier
                        self.actual_text = notes[2] #on récupère le texte de cette note
                        self.annotation_list.pop(index) #et on la supprime pour pouvoir la remplacer après

        elif self.mouse_zone == 2 and self.state == "drag":
            self.call_position = (self.anchored_position[0], self.anchored_position[1], self.state) #nous donne les coordonnées du début du clic et les conserves
            func.add_message(self,"utiliser R pour pivoter", 5, 10)

    if self.state != "drag":
        self.anchor_point = [(px.mouse_x, px.mouse_y)]

    elif self.state == "drag":
        if self.rotate % 2 == 1:
            self.anchor_point = [(px.mouse_x-20, px.mouse_y), (px.mouse_x+19, px.mouse_y)]
        else:
            self.anchor_point = [(px.mouse_x, px.mouse_y-20), (px.mouse_x, px.mouse_y+19)]

    if self.anchor and not self.state == "modify":
        func.anchoring(self)
    
    else:
        self.anchored_position = (px.mouse_x, px.mouse_y, None)

    self.battery = False
    for dipoles in self.dipoles_dict.values():
        if dipoles["type"] == 0:
            self.battery = True

    if self.global_count >= self.count_reset:
        func.reset(self)

def draw(self):
    '''affiche les dipoles'''
    for dipoles in self.dipoles_dict.values():
        if dipoles["type"] == "cable":

            px.line(dipoles["start"][0],dipoles["start"][1],dipoles["end"][0],dipoles["end"][1],dipoles["variant/color"])
            px.circb(dipoles["start"][0],dipoles["start"][1],4,7)
            px.circb(dipoles["end"][0],dipoles["end"][1],4,7)

        elif dipoles["type"] != "cable":
            variant = func.variant(self,dipoles)

            func.scale_blt(func.offset2(dipoles["start"][0],dipoles["end"][0]),func.offset2(dipoles["start"][1],dipoles["end"][1]),0,variant*16,dipoles["type"]*16,15,15,14,dipoles["rotate"])
            px.circb(dipoles["start"][0],dipoles["start"][1],4,7)
            px.circb(dipoles["end"][0],dipoles["end"][1],4,7)

    '''selon l'état de call_position, on continue d'executer une fonction'''
    if self.call_position[2] == "trace":
        edit.trace(self, self.call_position[0], self.call_position[1])

    elif self.call_position[2] == "cut":
        edit.cut(self, self.call_position[0], self.call_position[1])  

    elif self.call_position[2] == "move":
        edit.move_(self, self.call_position[0], self.call_position[1])
        
    elif self.call_position[2] == "drag":
        edit.drag(self, self.call_position[0], self.call_position[1])

    elif self.call_position[2] == "annotate":
        edit.annotate(self, self.call_position[0], self.call_position[1])

    elif self.call_position[2] == "modify":
        anim.modify(self, self.call_position[0], self.call_position[1])

    if self.hitbox_show != (None):
        px.line(self.hitbox_show[0][0],self.hitbox_show[0][1],self.hitbox_show[1][0],self.hitbox_show[1][1],10)
        px.line(self.hitbox_show[1][0],self.hitbox_show[1][1],self.hitbox_show[2][0],self.hitbox_show[2][1],10)
        px.line(self.hitbox_show[2][0],self.hitbox_show[2][1],self.hitbox_show[3][0],self.hitbox_show[3][1],10)
        px.line(self.hitbox_show[3][0],self.hitbox_show[3][1],self.hitbox_show[0][0],self.hitbox_show[0][1],10)
        self.hitbox_show = (None)

    for text in self.annotation_list:
        px.text(text[0],text[1],text[2],7)

    '''la barre à droite'''
    px.blt(348, 1, 0, 0, 120, 25, 16, 14)
    px.blt(348, 193, 0, 0, 120, 25, -16, 14)
    px.line(348, 17, 348, 193, 7)
    px.rect(349, 17, 24, 177, 2)

    '''la liste des dipoles'''
    for i in range(7):
        if i < 6:
            px.blt(354, 9 + (28 * i), 0, 0, 0 + (16 * i), 15, 15, 14) #les dipoles
        else:
            px.blt(354, 9 + (28 * i), 0, 0 +(48*(self.del_color)) , 0 + (16 * i), 15, 15, 14) #la del selon la couleur sélectionnée

        '''découpe les noms en deux si ils sont trop long'''
        if len(self.dipoles[i]["nom"]) < 7:
            px.text(350,28+(28*i),self.dipoles[i]["nom"],7)

        else:
            px.text(350,24+(28*i),self.dipoles[i]["nom"][:6],7)
            px.text(350,29+(28*i),self.dipoles[i]["nom"][-(len(self.dipoles[i]["nom"])-6):],7)

        if i < 6:
            px.line(349,35+(28*i),373,35+(28*i),7) #les 6 lignes blanches

    '''la barre en bas à gauche'''
    px.blt(1, 191, 0, 0, 120, 16, 20, 14)
    px.blt(89, 191, 0, 0, 120, -16, 20, 14)
    px.line(16, 191, 88, 191, 7)
    px.rect(16, 192, 73, 19, 2)

    '''les icones'''
    px.blt(12,193,0,32,16,15,15,14) #le multimètre
    px.text(33,198,"cable",self.cable_color)
    
    if not self.color_selection[0]:
        px.blt(38,189,0,32,11,10,5,14) #la flèche

    else:
        px.rect(30,126,25,65,7) #le cadre blanc autour
        for i in range(5):
            px.rect(31,179-(i*13),23,12,self.color_list[i]) #les couleurs

        px.blt(38,124,0,32,11,10,-5,14) #la flèche plus haut

        if px.btnp(px.MOUSE_BUTTON_LEFT) and 29 < px.mouse_x < 54 and 124 < px.mouse_y < 189:
            color = px.pget(px.mouse_x,px.mouse_y)

            if color != 7:
                self.cable_color = color
                self.color_selection[0] = False #on referme la fenêtre de sélection
                self.state = "trace" #et on active le mode traçage

    if not self.color_selection[1]:
        px.blt(346,180,0,107,22,5,10,14) #la flèche

    else:
        px.rect(296,175,53,20,7) #le cadre blanc autour
        for i in range(4):
            px.rect(336-(i*13),176,12,18,self.color_list[1:][i]) #les couleurs

        px.blt(294,180,0,107,22,-5,10,14) #la flèche moins loin

        if px.btnp(px.MOUSE_BUTTON_LEFT) and 296 < px.mouse_x < 346 and 175 < px.mouse_y < 195:
            color = px.pget(px.mouse_x,px.mouse_y)

            if color != 7:
                self.del_color = self.color_list[1:][::-1].index(color)
                self.color_selection[1] = False #on referme la fenêtre de sélection

    px.blt(58,193,0,56,0,15,15,14) #le sciseau
    px.blt(79,193,0,72,0,15,15,14) #les flèches de déplacement

    anim.selection(self)
    if len(self.message_list) > 0: #si il y à au moins un message
        anim.message(self)
        
    '''la barre en haut '''
    px.blt(126,0,0,0,120,16,-19,14)
    px.blt(267,0,0,0,120,-16,-19,14)
    px.line(142, 18, 266, 18, 7)
    px.rect(142, 0, 125, 18, 2)

    '''les icones'''
    px.blt(137, 1, 0, 80, 32 if self.vision == 0 else 48, 30, 15, 14)
    px.blt(173, 1, 0, 64, 64, 15, 15, 14)
    px.blt(194, 1, 0, 80, 16, 15, 15, 14)
    px.blt(215, 1, 0, 96, 80, 15, 15, 14)
    px.blt(236, 1, 0, 80, 64, 15, 15, 14)
    px.blt(257, 1, 0, 96, 64, 15, 15, 14)

    '''les cases à cocher'''
    anim.check_box(self)

    '''on dessine le curseur selon la zone de la souris et selon le mode actuel'''
    x = self.anchored_position[0]
    y = self.anchored_position[1]

    if self.mouse_zone == 0:
        if self.state != "mouse": 
            px.mouse(False) #on retire le curseur de base si un autre est actif

            if self.state == "trace":
                px.circb(x, y,4,1)
                px.pset(x, y,7)
            
            elif self.state == "drag":
                px.blt(x-4, y-4,0,88,0,9,9,14) #la main

            elif self.state == "cut":
                px.blt(x-4, y-4,0,47,0,9,9,14) #le petit sciseau

            elif self.state == "move":
                px.blt(x-4, y-4,0,32,0,9,9,14) #les petites flèches de déplacmeent

            elif self.state == "annotate":
                px.blt(x-4, y-4,0,103,0,9,9,14) #le curseur conventionel

            elif self.state == "modify":
                px.blt(x-4,y-4,0,112,0,9,9,14)

        else:
            px.mouse(True) #sinon on continue d'afficher le curseur de base

    elif self.mouse_zone != 0:  
        if self.state == "drag" and self.mouse_zone == 2: #on veux pouvoir afficher le curseur drag dans la barre à droite
            px.mouse(False)
            px.blt(x-4, y-4,0,88,0,9,9,14)

        elif self.mouse_zone == 5 and 295 <= px.mouse_x<= 339 and 189 <= px.mouse_y <= 195:
            px.mouse(False)
            px.blt(px.mouse_x-1,px.mouse_y-1,0,107,16,4,4,14)

        else: #sinon on affiche le curseur de base
            px.mouse(True)     

    if self.battery:
        px.blt(353,8,0,144,0,16,16,0)