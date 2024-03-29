import pyxel as px
import function as func

def selection(self):
    '''si la souris survole une case on affiche une barre en gris'''
    if 29 < px.mouse_x < 55 and 194 < px.mouse_y < 210:
        px.line(35,209,50,209,14)

    elif 54 < px.mouse_x < 76 and 191 < px.mouse_y < 210:
        px.line(58,209,73,209,14)

    elif 75 < px.mouse_x < 97 and 191 < px.mouse_y < 210:
        px.line(79,209,94,209,14)

    '''on affiche une barre en blanc en dessous de l'icone sélectionné'''
    if self.state == "trace":
        px.line(35,209,50,209,7)

    elif self.state == "cut":
        px.line(58,209,73,209,7)

    elif self.state == "move":
        px.line(79,209,94,209,7)


def message(self):
    for total, messages in enumerate(self.message_list):
        px.text(1, 1+(14 * total), messages[0], messages[2]) #affiche le méssage le plus récent

    if px.frame_count%30 == 0: #toutes les 30 frames (plus ou moins 1 seconde)
        index = 0
        while index < len(self.message_list):
            if self.message_list[index][1] == 0:
                self.message_list.pop(index)
                index -= 1

            else:
                self.message_list[index][1] -= 1 #on retire 1 au temps d'affichage
            index += 1


def saving(self):
    px.blt(129,37,0,0,120,8,8,14) #les quatres coins
    px.blt(267,37,0,0,120,-8,8,14)
    px.blt(267,170,0,0,120,-8,-8,14)
    px.blt(129,170,0,0,120,8,-8,14)

    px.rect(130,45,144,125,2) #le fond
    px.rect(137,37,130,8,2)
    px.rect(137,165,130,13,2)

    px.line(129,45,129,169,7) #les bordures
    px.line(274,45,274,169,7)
    px.line(137,37,266,37,7)
    px.line(137,177,266,177,7)

    px.blt(235, 85, 0, 32, 112, 32, 16, 0) #nouveau
    px.blt(235, 105, 0, 128, 112, 32, 16, 0) #sauvegarder
    px.blt(235, 125, 0, 64, 112, 32, 16, 0) #charger
    px.blt(235, 145, 0, 96, 112, 32, 16, 0) #effacer

    px.text(139, 166, str(len(self.file_list[self.mod]))+"/12 sauvegardes", 7)
    px.blt(252,45,0,32,128,15,15,14) #la croix rouge

    for y in range(12): #les 12 barres
        px.blt(137,45+(y*10),0,0,112,8,8,0)
        px.blt(219,45+(y*10),0,0,112,-8,8,0)
        px.rect(145,45+(y*10),74,8,14)
    
    for index,name in enumerate(self.file_list[self.mod]): #les noms des saves
        name = name[:-5] #on retire le .json
        px.text(141, 47+(index*10), name if len(name) <= 20 else name[:20], 7) #on affiche les noms des saves en blanc sauf la sélectionnée

    px.blt(136,44+(self.selection*10),0,0,147,8,10,0) #l'outline jaune de sélection
    px.blt(220,44+(self.selection*10),0,0,147,-8,10,0)
    for i in range(19):
        px.blt(144+(i*4),44+(self.selection*10),0,8,147,4,10,0)



def new_file(self):
    self.actual_text = func.key_input(self.actual_text,20,False)
    px.text(141,47+(len(self.file_list[self.mod])*10),self.actual_text,7)
    size = len(self.actual_text)

    if (px.frame_count // 20) % 2 == 0: #le quotient est pair une fois sur deux donc toutes les 1.33 sec car 20 frame = 0.66 sec
        px.rect(size * 4 + 141 + 1, 47+(len(self.file_list[self.mod])*10), 2, 5, 7)

    if px.btnp(px.MOUSE_BUTTON_RIGHT) or px.btnp(px.KEY_RETURN):

        func.save(self,  self.actual_text + ".json")
        self.file_list[self.mod].append(self.actual_text + ".json")
        self.new_file = "finished"
        self.actual_text = ""


def modify(self,x1,y1):
    modify_dip = None
    for num,dipoles in self.dipoles_dict.items():
        if func.colisions((x1,y1), dipoles["hitbox"]):
            modify_dip = num
    if modify_dip == None:
        return None

    parameter = "R" if self.dipoles_dict[modify_dip]["type"] != 0 else "U"

    px.blt(260,178,0,0,120,16,16,14)
    px.blt(330,178,0,0,120,-16,16,14)
    px.blt(330,194,0,0,120,-16,-16,14)
    px.blt(260,194,0,0,120,16,-16,14)

    px.rect(276,179,54,31,2)
    px.line(276,178,330,178,7)
    px.line(276,209,330,209,7)

    px.text(296,181,"resistance" if self.dipoles_dict[modify_dip]["type"] != 0 else "tension",7)
    px.text(296,190,str(self.dipoles_dict[modify_dip][parameter])+" ohm",7)
    if self.dipoles_dict[modify_dip]["type"] != "cable":
        show_poles(self,modify_dip)
        px.blt(271,198,0,20,150,12,10,0)

    px.text(296,201,"numero "+modify_dip,7)

    if px.btn(px.MOUSE_BUTTON_LEFT) and 295 <= px.mouse_x<= 335 and 189 <= px.mouse_y <= 195:
        self.actual_text = str(self.dipoles_dict[modify_dip][parameter])

    if px.btnp(px.MOUSE_BUTTON_LEFT) and 270 <= px.mouse_x <= 283 and 197 <= px.mouse_y <= 208:
        func.swap(self, modify_dip)

    if self.actual_text != "":

        if (px.frame_count // 20) % 2 == 0: 
            px.rect(len(self.actual_text) * 4 + 296 + 1, 190, 2, 5, 7)

        self.actual_text = func.key_input(self.actual_text, 3, True)
        self.dipoles_dict[modify_dip][parameter] = int(self.actual_text)

        if px.btnp(px.MOUSE_BUTTON_LEFT) or px.btnp(px.MOUSE_BUTTON_RIGHT) or px.btnp(px.KEY_RETURN):
            self.actual_text = ""


def show_poles(self,num):
    rotate = 1 - (self.dipoles_dict[num]["rotate"] % 2)
    start = self.dipoles_dict[num]["start"][rotate]
    end = self.dipoles_dict[num]["end"][rotate]
    switch = 1 if (end - start) < 0 else -1

    px.blt(270 + (4*rotate),185 - (4*rotate),0,0,160,(16 - (8 * rotate))*switch,(8 + (8 * rotate))*switch,0)
        

def check_box(self):
    px.text(109,195,"ancrage\nauto",7)
    px.blt(139,197,0,17,112,8,8,14)
    if self.anchor:
        px.blt(139,197,0,8,112,9,8,14)

    px.text(151,198,"astuces",7)
    px.blt(180,197,0,17,112,8,8,14)
    if self.tips:
        px.blt(180,197,0,8,112,9,8,14)

    px.text(192,198,"grille",7)
    px.blt(217,197,0,17,112,8,8,14)
    if self.grid:
        px.blt(217,197,0,8,112,9,8,14)
