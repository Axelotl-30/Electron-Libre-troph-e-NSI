import pyxel as px
import game
import os
import sys
import function as func
import anim_menu as anim

class App:
    def __init__(self):
        px.init(373, 210,title="électron libre")
        px.load("circuit2.pyxres")
        px.colors[14] = 0x9193C4 #on change deux couleurs pour les utiliser comme couleur d'UI
        px.colors[2] = 0x6f7296
        px.colors[0] = 0x0f0f0f #on atténue le noir

        self.directory = os.path.dirname(os.path.abspath(sys.argv[0]))#
        self.mod = 0 #0 ou 1, ça définie mode exo ou mode save
        self.file_list = [[file_ for file_ in func.list_dir(self.directory+"\\sauvegardes\\") if file_.endswith(".json")],
                        [file_ for file_ in func.list_dir(self.directory+"\\exercices\\") if file_.endswith(".json")]]
        func.check_files(self)

        self.launcher = "title"
        self.del_color = 0
        self.cable_color = 0
        self.global_count = 0 #attribu un numéro à un dipole
        self.count_reset = 50 #pour pas avoir des valeurs trop grandes à long terme
        self.state = "mouse" #états existants: "mouse","cut","move","trace" et "drag"
        self.mouse_zone = 0 #enregistre la zone où se situe la souris
        self.rotate = 1
        self.color_selection = [False,False] #le premier c'est pour la couleur des cables et l'autre pour la couleur des del
        self.vision = 0 #défini l'apparence des sprites
        self.actual_text = ""
        self.tips = True #active ou désactives les astuces (messages en jaune)
        self.anchor = True #la possibilité d'ancrer sa sourie
        self.grid = False #affiche une grille
        self.selection = 0 #quelle sauvegarde on choisi dans le menu save
        self.new_file = "finished"
        self.modify_dip = None
        self.battery = False #on ne peux mettre qu'une pile

        self.dipoles = [{"nom": "pile", "variant": 1,"key": "broken"}, {"nom": "moteur", "variant": 1,"key":"On"}, {"nom": "resistance","variant":1,"key":"None"}, 
                         {"nom": "fusible", "variant": 2,"key": "broken"}, {"nom": "interupteur", "variant": 2, "key": "closed"}, 
                         {"nom": "ampoule", "variant": 2, "key": "alight"}, {"nom": "del", "variant": 2, "key": "alight"}]
        
        self.dipoles_dict = {} #la "liste" des dipoles avec pour key leur numéro
        self.relate_list = [] #la liste des mailles
        self.nod_foundlist = [] #la liste des noeuds trouvés
        self.message_list = [] #la liste des messages à afficher
        self.move_list = [] #la liste des dipoles à déplacer
        self.cut_list = [] #la liste des dipoles à supp
        self.annotation_list = [] #la liste des notes

        self.call_position = (px.mouse_x, px.mouse_y, None) #permet l'appel de certaines fonctions avec la position x, y de départ
        self.anchor_point = [(px.mouse_x, px.mouse_y)] #représentes le ou les points d'ancrage de la souris
        self.anchored_position = (px.mouse_x, px.mouse_y, None) #permet d'utiliser la position ancrée de la souris
        self.color_list = (0,3,5,10,8)
        self.hitbox_show = (None)


        self.br = False
        px.run(self.update,self.draw)


    def update(self):
        if self.launcher == "game":
            game.update(self)

        elif self.launcher == "title":
            if px.btnp(px.MOUSE_BUTTON_LEFT) and 111<= px.mouse_x <= 260 and 126 <= px.mouse_y <= 149: 
                self.launcher = "game"
            px.mouse(True)

        elif self.launcher == "save":

            if px.btnp(px.MOUSE_BUTTON_LEFT) and 137 <= px.mouse_x <= 227 and 45 <= px.mouse_y <= 165:
                self.selection = (px.mouse_y - 45) // 10
    
            if px.btnp(px.KEY_DOWN) and self.selection < 11:
                self.selection += 1

            elif px.btnp(px.KEY_UP) and self.selection > 0:
                self.selection -= 1

            if px.btnp(px.MOUSE_BUTTON_LEFT) and 235 <= px.mouse_x <= 267 and 145 <= px.mouse_y <= 161 and self.selection <= len(self.file_list[self.mod])-1: 
                os.remove(self.directory+ ("\\sauvegardes\\" if self.mod == 0 else "\\exercices\\") +self.file_list[self.mod][self.selection])
                self.file_list[self.mod].pop(self.selection)
                
            elif px.btnp(px.MOUSE_BUTTON_LEFT) and 235 <= px.mouse_x <= 267 and 85 <= px.mouse_y <= 101 and len(self.file_list[self.mod]) < 12: 
                self.new_file = "new"

            elif px.btnp(px.MOUSE_BUTTON_LEFT) and 235 <= px.mouse_x <= 267 and 105 <= px.mouse_y <= 117 and self.selection <= len(self.file_list[self.mod])-1: 
                func.save(self, self.file_list[self.mod][self.selection])

            elif px.btnp(px.MOUSE_BUTTON_LEFT) and 235 <= px.mouse_x <= 267 and 125 <= px.mouse_y <= 137 and self.selection <= len(self.file_list[self.mod])-1: 
                func.load(self, self.file_list[self.mod][self.selection])

            elif px.btnp(px.MOUSE_BUTTON_LEFT) and 252 <= px.mouse_x <= 266 and 45 <= px.mouse_y <= 59: 
                self.launcher = "game"  


    def draw(self):
        px.cls(14) 
        if self.grid:
            for i in range(29):
                for j in range(17):
                    px.blt(0+(i if not (j > 14 and i < 2) else 2)*13,0+j*13,0,128,0,13,13,14)
                    #la condition c'est pour pas que la grille gène l'upscale des dipoles

        if self.launcher == "game" or self.launcher == "save": #on continue d'afficher le jeu en arrière plan si c'est save
            game.draw(self)

        elif self.launcher == "title":
            px.blt(62,5,1,1,0,248,86,0) #fond titre
            px.blt(79,4,1,0,175,212,81,0) #titre
            px.blt(167,100,1,0,88,39,9,0) #modes
            px.blt(111,126,1,0,112,150,24,0) #creation
            px.blt(111,160,1,0,136,150,24,0) #exercice
        
        if self.launcher == "save":
            anim.saving(self)
            if self.new_file == "new":
                anim.new_file(self)

App()