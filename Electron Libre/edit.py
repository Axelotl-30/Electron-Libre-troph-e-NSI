import pyxel as px
import function as func

def trace(self,x1,y1):
    px.line(x1, y1, self.anchored_position[0], self.anchored_position[1],10) #le cable en train d'être tracé
    px.circb(x1,y1,4,10) #le point d'ancrage au début
    px.circb(self.anchored_position[0], self.anchored_position[1] , 4, 10) #le point d'ancrage à la fin

    if not px.btn(px.MOUSE_BUTTON_LEFT): #si on relache le clic
        cable = {"start": (x1,y1), "end": (self.anchored_position[0], self.anchored_position[1]), "type": "cable", "hitbox": (0,0,0,0),
             "variant/color": self.cable_color, "U": 9, "I": None, "R": 0, "visited": False}
        
        if verif(self, cable,self.global_count):
            cable["hitbox"] = func.dipole_hitbox(cable) #on calcule une première fois l'hitbox du câble
            self.dipoles_dict[str(self.global_count)] = cable #puis on l'ajoute au dictionaire avec pour key son numéro
            self.global_count += 1 #on ajoute 1 à la variable qui compte le total des dipôles créés (elle ne représente pas le nombre de dipôles actuel)
        self.call_position = (0,0,None) #on arrête la fonction


def verif(self,dipole,num):
    if dipole["type"] == "cable" and func.dist(dipole["start"],dipole["end"]) <= 4+4: #si le cable est trop court
        func.add_message(self,"cable trop petit !", 5, 8)
        return False    
    
    for other_num,otherdipole in self.dipoles_dict.items():

        if ((otherdipole["start"] == dipole["start"] and otherdipole["end"] == dipole["end"]) or (otherdipole["end"] == dipole["start"] and otherdipole["start"] == dipole["end"])) and other_num != num: #si l'on trouve un cable aux mêmes coordonées 
            func.add_message(self,"un autre dipole est \n deja present !", 5, 8)
            return False
        
    if func.zones(self,(dipole["start"][0],dipole["start"][1])) != 0 or func.zones(self,(dipole["end"][0],dipole["end"][1])) != 0:
        func.add_message(self,"hors des limites de placement !", 5, 8)
        return False   

        
    return True


def cut(self,x1,y1):

    if not px.btn(px.MOUSE_BUTTON_LEFT): #si on relache le clic
        if self.anchored_position[2] == 0: #si la souris est sur un noeud

            for num, dipoles in self.dipoles_dict.items():

                if dipoles["start"] == (self.anchored_position[0],self.anchored_position[1]):
                    self.cut_list.append((num, "start" if dipoles["type"] == "cable" else "both"))
                    dipoles["visited"] = True

                elif dipoles["end"] == (self.anchored_position[0],self.anchored_position[1]):
                    self.cut_list.append((num, "end" if dipoles["type"] == "cable" else "both"))
                    dipoles["visited"] = True

            temp_list = []
            for dip in self.cut_list:
                temp_list.append(dipoles_chain(self,[dip]))

            self.cut_list = temp_list

            for dipoles in self.dipoles_dict.values():
                dipoles["visited"] = False

            if len(self.cut_list) > 1: #si il y a plus qu'un noeud concerné , on sépare les noeuds
                for index,dip_group in enumerate(self.cut_list):
                    offset = -5
                    if index % 2 == 1:
                        offset = 5

                    for dip in dip_group:
                        if dip[1] != "both":

                            nod = self.dipoles_dict[dip[0]][dip[1]] #le noeud du dipoles (start ou end cela dépend de nods[1])
                            self.dipoles_dict[dip[0]][dip[1]] = (nod[0] + offset, nod[1] + (5 * index)) #on modifie sa position
                            self.dipoles_dict[dip[0]]["hitbox"] = func.dipole_hitbox(self.dipoles_dict[dip[0]]) #on re-calcule l'hitbox

                        else:
                            nod = self.dipoles_dict[dip[0]]["start"] #le noeud du dipoles (start ou end cela dépend de nods[1])
                            self.dipoles_dict[dip[0]]["start"] = (nod[0] + offset, nod[1] + (5 * index)) #on modifie sa position

                            nod = self.dipoles_dict[dip[0]]["end"] #le noeud du dipoles (start ou end cela dépend de nods[1])
                            self.dipoles_dict[dip[0]]["end"] = (nod[0] + offset, nod[1] + (5 * index)) #on modifie sa position

                            self.dipoles_dict[dip[0]]["hitbox"] = func.dipole_hitbox(self.dipoles_dict[dip[0]]) #on re-calcule l'hitbox


        elif self.anchored_position[2] == None: #si la souris n'est pas ancrée
            ToDelete = ()
            for num, dipoles in self.dipoles_dict.items():
                if func.colisions(self.anchored_position, dipoles["hitbox"]):
                    ToDelete = (self.dipoles_dict, num)

            for index, notes in enumerate(self.annotation_list):
                if func.colisions(self.anchored_position, notes[3]):
                    ToDelete = (self.annotation_list, index)

            if ToDelete != (): 
                ToDelete[0].pop(ToDelete[1])

        self.cut_list = []
        self.call_position = (0, 0, None)


def dipoles_chain(self,chain):
    repeat = True
    while repeat == True:
        found_smth = False

        for num,dipoles in self.dipoles_dict.items():
            if not dipoles["visited"]:
                start = [self.dipoles_dict[dip[0]]["start"] for dip in chain if dip[1] == "both"]
                end = [self.dipoles_dict[dip[0]]["end"] for dip in chain if dip[1] == "both"]

                if dipoles["start"] in start or dipoles["start"] in end:
                    
                    if dipoles["type"] != "cable":
                        dipoles["visited"] = True
                        found_smth = True
                        chain.append((num,"both"))
                    
                    else:
                        chain.append((num,"start"))

                elif dipoles["end"] in start or dipoles["end"] in end:
                    
                    if dipoles["type"] != "cable":
                        dipoles["visited"] = True
                        found_smth = True
                        chain.append((num,"both"))
                    
                    else:
                        chain.append((num,"end"))          
        if not found_smth:
            repeat = False

    if len(chain) == 0:
        chain.append(None)

    return chain


def chain_dist(self,chain,x1,y1):
    for index,dip in enumerate(chain):
        if dip[1] != "both":

            chain[index] = (dip[0],dip[1],(x1 - self.dipoles_dict[dip[0]][dip[1]][0], y1 - self.dipoles_dict[dip[0]][dip[1]][1])) #on ajoute un tuple des écarts x et y

        else:
            start = self.dipoles_dict[dip[0]]["start"]
            end = self.dipoles_dict[dip[0]]["end"]

            chain[index] = (dip[0],dip[1],(x1 - start[0], y1 - start[1]),(x1 - end[0], y1 - end[1])) #on ajoute les écarts pour le start et le end
    
    return chain


def move_(self, x1, y1):
    if len(self.move_list) == 0:
        if self.anchored_position[2] == 0:

            for num, dipoles in self.dipoles_dict.items():
                if dipoles["start"] == (self.anchored_position[0],self.anchored_position[1]):
                    self.move_list.append((num, "start" if dipoles["type"] == "cable" else "both"))
                    dipoles["visited"] = True

                elif dipoles["end"] == (self.anchored_position[0],self.anchored_position[1]):
                    self.move_list.append((num, "end" if dipoles["type"] == "cable" else "both"))
                    dipoles["visited"] = True

        else:
            for num, dipoles in self.dipoles_dict.items():
                if func.colisions(self.anchored_position, dipoles["hitbox"]):
                    self.move_list.append((num, "both"))
                    dipoles["visited"] = True
                    break
        
        self.move_list = dipoles_chain(self, self.move_list)
        for dipoles in self.dipoles_dict.values():
            dipoles["visited"] = False
        if self.move_list[0] != None:
            self.move_list = chain_dist(self,self.move_list,x1,y1)

    if self.move_list[0] != None:
        self.anchor_point = []
        for dip in self.move_list:

            if dip[1] != "both":
                self.dipoles_dict[dip[0]][dip[1]] = (self.anchored_position[0] - dip[2][0], self.anchored_position[1] - dip[2][1])

            else:
                dipole = self.dipoles_dict[dip[0]]
                    
                self.dipoles_dict[dip[0]]["start"] = (self.anchored_position[0] - dip[2][0], self.anchored_position[1] - dip[2][1])
                self.dipoles_dict[dip[0]]["end"] = (self.anchored_position[0] - dip[3][0], self.anchored_position[1] - dip[3][1])

    if not px.btn(px.MOUSE_BUTTON_LEFT):
        for dip in self.move_list:
            if dip != None:
                dipole = self.dipoles_dict[dip[0]]
                dipole["hitbox"] = func.dipole_hitbox(self.dipoles_dict[dip[0]]) #on réfini les hitbox des dipoles déplacés
                if verif(self,dipole,dip[0]):
                    del self.dipoles_dict[dip[0]]

        self.move_list = []
        self.call_position = (0, 0, None)  


def drag(self, x1, y1):
    if px.btnp(px.KEY_R):
        self.rotate = (self.rotate % 4) + 1 #incrémente rotate de 1 à 4
    
    position = func.switch(self.rotate, self.anchored_position)
    start = position[0]
    end = position[1]

    func.scale_blt(self.anchored_position[0]-15, self.anchored_position[1]-15,0,0,((y1-8)//28)*16,15,15,14, self.rotate)
    px.blt(start[0]-4,start[1]-4,0,96,23,9,9,14)
    px.blt(end[0]-4,end[1]-4,0,96,14,9,9,14)

    if not px.btn(px.MOUSE_BUTTON_LEFT):

        dipole = {"start": (start[0], start[1]), "end": (end[0], end[1]), "type": (y1-8)//28, "hitbox": (0,0,0,0),"rotate": self.rotate, "variant/color": 1, "U": 9, "I": None, "R": 0, "visited": False}
        if verif(self, dipole,self.global_count):

            for group in func.dipole_key(self,dipole):
                dipole[group[0]] = group[1]

            dipole["hitbox"] = func.dipole_hitbox(dipole)
            self.dipoles_dict[str(self.global_count)] = dipole
            self.global_count += 1

        self.call_position = (0, 0, None)
        self.state = "mouse"
        self.rotate = 1


def annotate(self,x1,y1):
    self.actual_text = func.key_input(self.actual_text,30,False)
    px.text(x1,y1,self.actual_text,7)
    size = len(self.actual_text)

    if (px.frame_count // 20) % 2 == 0: #le quotient est pair une fois sur deux donc toutes les 1.33 sec car 20 frame = 0.66 sec
        px.rect(size * 4 + x1 + 1, y1, 2, 5, 7)

    if px.btnp(px.MOUSE_BUTTON_RIGHT) or px.btnp(px.KEY_RETURN):
        if len(self.actual_text) > 0:
            self.annotation_list.append((x1,y1,self.actual_text,((x1-2,y1-2),(x1-2,y1 + 6),(size * 4 + x1,y1 + 6),(size * 4 + x1,y1-2))))

        self.call_position = (0, 0, None)
        self.state = "mouse"
        self.actual_text = ""

