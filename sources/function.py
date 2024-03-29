import pyxel as px
import numpy as np
import json
import shutil
import os

def scale_blt(u, v, img, sprite_x, sprite_y, width, height, colkey, rotate):
    abs_height = abs(height)
    abs_width = abs(width)
    sprite = []

    if rotate == 1 or rotate == 2:
        px.blt(9,210 - abs_height, img, sprite_x, sprite_y, width, height, colkey) #on affiche le sprite de base dans un coin de la fenêtre
    else:
        px.blt(9,210 - abs_height, img, sprite_x, sprite_y, -width, height, colkey) #si c'est rotate = 3 ou 4 on inverse le sens du sprite

    '''on récupère les pixels du sprite et ont en fait un tableau qui représente le sprite'''
    for y in range(210 - abs_height, 210):
        x_row = []

        for x in range(9,9 + abs_width):
            x_row.append(px.pget(x, y))

        sprite.append(x_row)

    px.rect(9, 210 - abs_height, abs_width, abs_height, 14) #on recouvre le sprite de base pour pouvoir upscale d'autres sprite ensuite
    if rotate % 2 == 0: #si c'est pair on rotate de 90°
        sprite = np.rot90(sprite, axes=(1,0))

    '''on affiche le sprite aux positions u et v en remplaçant les pixels par des rectangles en 2x2 de même couleur'''
    for index_y, row in enumerate(sprite):
        for index_x, color in enumerate(row):

            if color != colkey:
                px.rect(index_x*2  + u, index_y*2  + v, 2, 2, color)


def dist(A,B):
    distance = px.sqrt((B[1] - A[1]) ** 2 + (B[0] - A[0]) ** 2)
    return distance if distance < 1000 else 0

def offset(A,B,C):
    return C + (B - A)


def anchoring(self):
    self.anchored_position = (px.mouse_x, px.mouse_y, None)
     
    for index, points in enumerate(self.anchor_point):
        if not self.grid:
            for dipoles in self.dipoles_dict.values():
                '''si un noeud de dipole est assez proche d'un point d'ancrage, la position ancrée de la souris se met sur le noeud du dipole'''
                if dist(dipoles["start"], points) <= 4+4:
                    self.anchored_position = (offset(points[0], dipoles["start"][0], px.mouse_x), offset(points[1], dipoles["start"][1], px.mouse_y), index)  

                elif dist(dipoles["end"], points) <= 4+4:
                    self.anchored_position = (offset(points[0], dipoles["end"][0], px.mouse_x), offset(points[1], dipoles["end"][1], px.mouse_y), index) 
        else:
            a = points[0] // 13
            b = points[1] // 13
            resulta = nearest_value(a*13,points[0],(a+1)*13)
            resultb = nearest_value(b*13,points[1],(b+1)*13)
            self.anchored_position = (offset(points[0],resulta, px.mouse_x), offset(points[1],resultb, px.mouse_y), None)
            for dipoles in self.dipoles_dict.values():
                if self.anchored_position in (dipoles["start"],dipoles["end"]):
                    self.anchored_position = (self.anchored_position[0],self.anchored_position[1],0)
    

def nearest_value(min_value,value,max_value):
    if value < min_value:
        return min_value
    elif value > max_value:
        return max_value
    elif value - min_value < max_value - value:
        return min_value
    else:
        return max_value
            

def dipole_hitbox(dipole):
    I = dipole["start"] #les points I et J
    J = dipole["end"]
    IJ_angle = px.atan2(J[1] - I[1], J[0] - I[0]) #et l'angle qu'ils forment

    if dipole["type"] == "cable":
        size = 4

    else:
        size = 15

    A = (size * px.cos(IJ_angle - 90) + I[0], size * px.sin(IJ_angle - 90) + I[1]) #calcule les coordonées des points A et B au niveau de point I
    B = (size * px.cos(IJ_angle + 90) + I[0], size * px.sin(IJ_angle + 90) + I[1])

    C = (size * px.cos(IJ_angle + 90) + J[0], size * px.sin(IJ_angle + 90) + J[1]) #calcule les coordonées des points C et D au niveau de point J
    D = (size * px.cos(IJ_angle - 90) + J[0], size * px.sin(IJ_angle - 90) + J[1])

    return (A,B,C,D)   


def colisions(position,hitbox):
    '''coordonées des sommets de la hitbox ainsi que de z, la position de la sourie'''
    A = hitbox[0]
    B = hitbox[1]
    C = hitbox[2]
    D = hitbox[3]
    Z = (position[0], position[1])

    '''les coordonnées des vecteur de chaques cotés de la hitbox'''
    AB = (B[0]-A[0],B[1]-A[1])
    BC = (C[0]-B[0],C[1]-B[1])
    CD = (D[0]-C[0],D[1]-C[1])
    DA = (A[0]-D[0],A[1]-D[1])

    '''les coordonées des vecteurs de chaque sommet avec z'''
    AZ = (Z[0]-A[0],Z[1]-A[1])
    BZ = (Z[0]-B[0],Z[1]-B[1])
    CZ = (Z[0]-C[0],Z[1]-C[1])
    DZ = (Z[0]-D[0],Z[1]-D[1])

    '''calculs des déterminants'''
    AB_AZ = AB[0]*AZ[1]-(AB[1]*AZ[0])
    BC_BZ = BC[0]*BZ[1]-(BC[1]*BZ[0])
    CD_CZ = CD[0]*CZ[1]-(CD[1]*CZ[0])
    DA_DZ = DA[0]*DZ[1]-(DA[1]*DZ[0])

    '''si tous les déterminants sont négatif ou égal à 0, le point Z est à l'intérieur de la hitbox ou sur un de ses cotés'''
    if AB_AZ <= 0 and BC_BZ <= 0 and CD_CZ <= 0 and DA_DZ <= 0:
        return True
    
    return False

def switch (rotation, anchored_pos):
    if rotation == 1:
        return ((anchored_pos[0]-20, anchored_pos[1]), (anchored_pos[0]+19, anchored_pos[1]))
    
    elif rotation == 2:
        return ((anchored_pos[0], anchored_pos[1]-20), (anchored_pos[0], anchored_pos[1]+19))

    elif rotation == 3:
        return ((anchored_pos[0]+19, anchored_pos[1]), (anchored_pos[0]-20, anchored_pos[1]))
    
    elif rotation == 4:
        return ((anchored_pos[0], anchored_pos[1]+19), (anchored_pos[0], anchored_pos[1]-20))
    
def offset2(start, end):
    a = end - start
    if a > 0:
        return start + 5
    
    elif a < 0:
        return a + start + 5
    
    else:
        return start - 15


def key_input(text, lim, onlyNumbers):
    if not onlyNumbers:
        keyboard = {px.KEY_0:"0",px.KEY_1:"1",px.KEY_2:"2",px.KEY_3:"3",px.KEY_4:"4",px.KEY_5:"5",px.KEY_6:"6",px.KEY_7:"7",px.KEY_8:"8",px.KEY_9:"9",
                    px.KEY_A:"a",px.KEY_B:"b",px.KEY_C:"c",px.KEY_D:"d",px.KEY_E:"e",px.KEY_F:"f",px.KEY_G:"g",px.KEY_H:"h",px.KEY_I:"i",px.KEY_J:"j", px.KEY_K:"k",
                    px.KEY_L:"l",px.KEY_M:"m",px.KEY_N:"n",px.KEY_O:"o",px.KEY_P:"p",px.KEY_Q:"q",px.KEY_R:"r",px.KEY_S:"s",px.KEY_T:"t", px.KEY_U:"u",px.KEY_V:"v",
                    px.KEY_W:"w",px.KEY_X:"x",px.KEY_Y:"y",px.KEY_Z:"z",px.KEY_SPACE:" ",px.KEY_ASTERISK:"*",px.KEY_PLUS:"+",px.KEY_MINUS:"-",px.KEY_SLASH:"/"}
    
    else:
        keyboard = {px.KEY_0:"0",px.KEY_1:"1",px.KEY_2:"2",px.KEY_3:"3",px.KEY_4:"4",px.KEY_5:"5",px.KEY_6:"6",px.KEY_7:"7",px.KEY_8:"8",px.KEY_9:"9"}
    key_input = text

    if len(key_input) < lim:
        for keys in keyboard:
            if px.btnp(keys):
                letter = keyboard[keys]

                if px.btn(px.KEY_SHIFT):
                    letter = letter.upper()
                key_input += letter

    if px.btnp(px.KEY_BACKSPACE):
        if not(onlyNumbers and len(key_input) == 1):
            key_input = key_input[:-1]

        else:
            key_input = "0"

    if onlyNumbers:
        key_input = int(key_input)
        key_input = str(key_input) #pour transformer les 012 en 12 etc

    return key_input


def add_message(self, message, time, color):
    found = False
    for index, list_ in enumerate(self.message_list):
        if color == 10 and message in list_:

            self.message_list[index] = [message, time, color]
            found = True
            break

    if not found:
        if self.tips or (not self.tips and color != 10): #si les astuces sont désactivés, on ajoute pas les messages jaunes
            self.message_list.append([message, time, color])


def branches(self):
    for num in self.dipoles_dict.keys():
        self.dipoles_dict[num]["U"] = 0 if self.dipoles_dict[num]["type"] != 0 else self.tension
        self.dipoles_dict[num]["I"] = 0

    self.tension = 0
    self.relate_list = []
    self.nod_foundlist = []
    ending_point = first_branch(self)

    for nod_group in self.nod_foundlist:
        compare_list = []

        for nod in nod_group:
            compare_list.append([nod])
            compare_list = explore(self,compare_list,ending_point)

        compare(self, compare_list)
    for index,branch in enumerate(self.relate_list):
        I = intensity(self,branch,index)
        for dip in branch:
           self.dipoles_dict[dip[1]]["U"] = self.tension
           self.dipoles_dict[dip[1]]["I"] = I
        self.relate_list[index].insert(0,I)

    for num in self.dipoles_dict.keys():
        self.dipoles_dict[num]["visited"] = False

    print(self.relate_list, "relate_list")
    print(self.dipoles_dict)



def first_branch(self):
    for num, dipoles in self.dipoles_dict.items():
        if dipoles["type"] == 0:

            dipoles["visited"] = True
            self.tension = dipoles["U"]
            self.relate_list.append([("start",num)])
        break

    verified = 0
    while verified < len(self.relate_list[0]):

        dip = self.relate_list[-1][verified]
        found = []
        dip_anchor = self.dipoles_dict[dip[1]][("end" if dip[0] == "start" else "start") if verified > 0 else dip[0]]

        for num, dipoles in self.dipoles_dict.items():
            if not dipoles["visited"]:

                if dipoles["start"] == dip_anchor:
                    if verified > 0:
                        found.append((len(self.relate_list[0]),"start", num))
                    else:
                        found.append((0,"end", num))

                elif dipoles["end"] == dip_anchor:
                    if verified > 0:
                        found.append((len(self.relate_list[0]),"end", num))
                    else:
                        found.append((0,"start", num))

        verified += 1

        if len(found) == 1: #on ajoute que si c'est pas un noeud
            self.dipoles_dict[found[0][2]]["visited"] = True
            self.relate_list[0].insert(found[0][0], (found[0][1], found[0][2]))

            if found[0][0] == 0: #si on l'insère en début de liste
                verified = 0 #on remet vérified à 0 pour qu'il soit quand même vérifié
        
        else: #un noeud est trouvé
            for dip in found:
                if dip[0] > 0: #on veut que le noeud après la pile, pas celui avant
                    self.dipoles_dict[dip[2]]["visited"] = True
                    self.nod_foundlist.append([(dip[1], dip[2])])

    ending_dip = self.relate_list[0][0]
    return self.dipoles_dict[ending_dip[1]][ending_dip[0]]


def explore(self,compare_list,ending_point):
    repeat = True
    while repeat == True:
        found = []
        prev = previous_dip(self,compare_list)
        if prev != ending_point:
            for num, dipoles in self.dipoles_dict.items():
                if not dipoles["visited"]:
                
                    if dipoles["start"] == prev:
                        found.append(("start",num))

                    elif dipoles["end"] == prev:  
                        found.append(("end",num)) 

        else:
            repeat = False

        if len(found) == 1:
            self.dipoles_dict[found[0][1]]["visited"] = True
            compare_list[-1].append(found[0])

        else: #on a trouvé un noeud
            self.nod_foundlist.append([])
            for dip in found:
                self.nod_foundlist[-1].append(dip)
            repeat = False

    return compare_list

def compare(self, compare_list):
    add_list = []
    for branch in compare_list:
        found_dip = False
        current_breaker = False

        for dip in branch:
            dipole = self.dipoles_dict[dip[1]]

            if dipole["type"] != "cable":
                found_dip = True #on a trouvé un dipole (pas un cable)

            if dipole["type"] == 0:
                found_battery = True #on a trouvé la pile

            if(dipole["type"] == 6 and dip[0] == "end") or (dipole["type"] == 3 and dipole["broken"] == True) or (dipole["type"] == 4 and dipole["closed"] == True):
                current_breaker = True
        
        if not current_breaker:
            if not found_dip:
                self.relate_list.append(branch) #on continue au cas où une autre branche sans dipole existe
                add_list.append("NoDipBranchFound")

            elif found_dip:
                add_list.append(branch) #on l'ajoute à une liste provisoire au cas où on trouve une branche sans dipoles après

    if "NoDipBranchFound" not in (add_list): #si aucune branche sans dipole a été trouvée
        for selected_branch in add_list:
            self.relate_list.append(selected_branch)

    else:
        for branch in compare_list:
            if branch not in add_list:
                for dip in selected_branch:
                    print(dip)
                    self.dipoles_dict[dip[1]]["visited"] = False


def previous_dip(self, list_):
    dip = list_[-1][-1]
    return self.dipoles_dict[dip[1]]["end" if dip[0] == "start" else "start"] #renvoie les coo de l'ancre opposée du dipole précédent


def check_files(self):
    for mod in range(2):
        for index, name in enumerate(self.file_list[mod]):

            with open(self.directory+ ("\\sauvegardes\\" if mod == 0 else "\\exercices\\") + name, "r") as file_:
                data = json.load(file_)

                if data["type"] != mod: #si le fichier de sauvegarde n'est pas dans le bon dossier
                    self.file_list[1-mod].append(self.file_list[mod][index]) #on le switch de liste
                    self.file_list[mod].pop(index)
                    file_.close() #on ferme le fichier
                    shutil.move(self.directory+ ("\\sauvegardes\\" if mod == 0 else "\\exercices\\") + name,
                                self.directory+ ("\\sauvegardes\\" if mod == 1 else "\\exercices\\") + name) #on le déplace dans le bon dossier
                    

def list_dir(path):
    """permet de récupérer les fichiers de sauvegarde et de recréer les dossiers inexistant"""
    try:
        return os.listdir(path)
    
    except FileNotFoundError:
        os.mkdir(path)
        return [] #il est forcément vide

def save(self,path):
    with open(self.directory+ ("\\sauvegardes\\" if self.mod == 0 else "\\exercices\\") + path, "w") as newfile:

        file_ = json.dumps({"type": self.mod, "count": self.global_count, "vision": self.vision, "dipoles": self.dipoles_dict, "notes": self.annotation_list}, indent=4)
        newfile.write(file_)

def load(self,path):
    with open(self.directory+ ("\\sauvegardes\\" if self.mod == 0 else "\\exercices\\") + path, "r") as file_:
        data = json.load(file_)

    self.global_count = data["count"]
    self.vision = data["vision"]
    self.dipoles_dict = data["dipoles"]
    self.annotation_list = data["notes"]


def dipole_key(self,dipole):
    if dipole["type"] == 6:
        return ((self.dipoles[dipole["type"]]["key"],0),("color",self.del_color))
    
    elif dipole["type"] == 3:
        return ((self.dipoles[dipole["type"]]["key"],0),("ceiling",4))
    
    else:
        return ((self.dipoles[dipole["type"]]["key"],0),)
    

def variant(self,dipole):
    if dipole["type"] in (0,1,2):
        return self.vision
    
    if dipole["type"] == 3:
        return dipole["broken"] + self.vision * self.dipoles[3]["variant"]
    
    if dipole["type"] == 4:
        return dipole["closed"] + self.vision * self.dipoles[4]["variant"]
    
    if dipole["type"] == 5:
        return (dipole["alight"] if self.vision == 0 else 0) + self.vision * self.dipoles[5]["variant"]
    
    if dipole["type"] == 6:
        return ((dipole["alight"] if self.vision == 0 else 0) + self.vision * self.dipoles[6]["variant"]) + 3 * dipole["color"]


def swap(self, num):
    temp = self.dipoles_dict[num]["start"]
    self.dipoles_dict[num]["start"] = self.dipoles_dict[num]["end"]
    self.dipoles_dict[num]["end"] = temp


def zones(self,position):
    if (0 <= position[0] <= 104 and 189 <= position[1] <= 209) or (self.color_selection[0] and 29 < position[0] < 54 and 124 < position[1] < 190):
        return 1 #la barre en bas

    if 347 <= position[0] <= 372 and 0 <= position[1] <= 209:
        return 2 #la barre à droite

    if 125 <= position[0] <= 283 and 0 <= position[1] <= 20:
        return 3 #la barre en haut

    if 105 <= position[0] <= 225 and 195 <= position[1] <= 210:
        return 4 #les cases à cocher

    if self.call_position[2] == "modify" and 260 <= position[0] <= 345 and 178 <= position[1] <= 209:
        return 5 #le menu de modify
    
    if not (0 <= position[0] <= 373 and 0 <= position[1] <= 210):
        return 6 #hors de l'écran

    return 0

def detect(self):
    for dipoles in self.dipoles_dict.values():
        if dipoles["type"] in (5,6) and dipoles["U"] > 0:
            dipoles["alight"] =  1

        if dipoles["type"] == 3 and dipoles["I"] > dipoles["ceiling"]:
            dipoles["broken"] = 1

def reset(self):
    """permet d'actualiser le global count pour pas qu'il séloigne trop du nombre réel de dipoles à l'écran"""
    temp_dict = {}
    self.global_count = 0
    for num in self.dipoles_dict.keys():
        temp_dict[str(self.global_count)] = self.dipoles_dict[num]
        self.global_count += 1

    self.dipoles_dict = temp_dict
    if self.global_count >= self.count_reset / 2: #si après avoir réaranger le global count il est plus grand que 50% de la limite
        self.count_reset += self.count_reset / 2 #on augmente la limite de 50%

    add_message(self,"les numeros ont ete mis a jour", 5, 10)


def intensity(self,branch,index):
    R_sum = 0
    for dip in branch:
        if self.dipoles_dict[dip[1]]["type"] not in("cable",0):
            R_sum += self.dipoles_dict[dip[1]]["R"]

    return (self.tension/R_sum) if R_sum != 0 else self.relate_list[index-1][0]

