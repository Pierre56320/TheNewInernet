#coding: utf-8
#TM-PG-VG

import huffman
import base64
import tkinter as tk
from tkinter.filedialog import *
from tkinter.messagebox import showwarning, showinfo
import os
from threading import Thread
from time import sleep,time

def compress_fichier(fichier_entree):
    """Prend un fichier en paramètre et le compresse"""
    if fichier_entree[-4:] == ".pvt":
        showwarning("","Le fichier est déjà compressé")
    elif fichier_entree[-4:] == ".txt": #si il s'agit d'un fichier texte on le lit normalement
        with open(fichier_entree, 'r', encoding='utf_8') as fent, open(fichier_entree[:-4] + '.pvt', 'wb') as fsort:
            contenu = fent.read()
            code = huffman.compresser(contenu+".txt") #on encode également l'extension
            fsort.write(code)
            fent.close()
            fsort.close()
    else: # sinon on le lit en tant que fichier binaire
        with open(fichier_entree, 'rb') as fent, open(fichier_entree[:-4]+'.pvt', 'wb') as fsort:
            contenu = base64.b64encode(fent.read()) #transforme les fichiers binaires en chaine de caractère
            code = huffman.compresser(str(contenu)+fichier_entree[-4:])
            fsort.write(code)
            fent.close()
            fsort.close()

def decompress_fichier(fichier_entree):
    """Prend un fichier en paramètre et le décompresse"""
    with open(fichier_entree, 'rb') as fent:
        contenu = fent.read()
        chaine = huffman.decompresser(contenu)
        chaine, extension = chaine[:-4], chaine[-4:]
        if extension == '.txt' :
            with open(fichier_entree[:-4] + '_décompressé.txt', 'w', encoding='utf-8') as fsort:
                fsort.write(chaine)
                fent.close()
        else :
            with open(fichier_entree[:-4]+'_décompressé'+extension, 'wb') as fsort:
                chaine = chaine[2:-1]
                chaine = chaine.encode("ascii")
                fsort.write(base64.b64decode(chaine)) #on retransforme la chaine de caractère en fichier binaire
                fent.close()
                fsort.close()

class Application(object):
    def __init__(self): #on créé une fenêtre tkinter avec ses widgets
        self.fen = tk.Tk()
        self.fen.geometry("600x300")
        self.fen.title('Compression de Huffman')
        self.cadre = tk.Frame(self.fen)
        self.cadre.pack(side = "top", fill=tk.X)
        self.cadre2 = tk.Frame(self.fen)
        self.cadre2.pack(side='bottom',fill=tk.X)
        tk.Button(self.cadre2, text='Quitter', command=self.fen.destroy).pack(side='right', padx=25, pady=15)
        self.bouton1 = tk.Button(self.cadre2, text='Choisir un Fichier', command=self.ChoisirFichier)
        self.bouton1.pack(side='left', padx=25, pady=15)
        self._thread1 = None #on va utiliser deux threads, le premier pour la fonction de compression/décompression
        self._thread2 = None #le deuxième pour l'animation
        self.fen.mainloop()

    def ChoisirFichier(self):
        fichier = askopenfilename(initialdir=".", title="Selection d'un fichier")
        if fichier != '':
            try :
                self.Label1.destroy()
            except:
                pass
            self.cheminFichier = fichier
            self.btnx = tk.Button(self.cadre, text='x', command=self.supFichier)
            self.btnx.pack(side='left', padx=10, pady=15)
            self.Label1 = tk.Label(self.cadre, text=self.cheminFichier, fg='blue')
            self.Label1.pack(side='left', pady=15, padx = 10)
            self.bouton1.configure(text="Compresser", command = self.init_comp)
            self.bouton2 = tk.Button(self.cadre2, text='Décompresser', command=self.init_decomp)
            self.bouton2.pack(side='left', pady=15)

    def supFichier(self):
        """réinitialise la fenêtre"""
        try :
            self.cheminFichier = ''
            self.Label1.configure(text=self.cheminFichier)
            self.btnx.destroy()
            self.bouton1.configure(text="Choisir un Fichier", command=self.ChoisirFichier)
            self.bouton2.destroy()
        except :
            pass

    def tauxDeCompression(self):
        taille_fichier_init = os.path.getsize(self.cheminFichier)
        taille_fichier_comp = os.path.getsize(self.cheminFichier[:-4]+'.pvt')
        self.tdComp = 'Pour "'+str(self.cheminFichier.split('/')[-1])+'" le taux de compression est : '\
                      +str((1 - (taille_fichier_comp /taille_fichier_init))*100)[:5]+'%'\
                      +'\n'+"Temps de compression : "+ str(round(self.fin - self.debut,5))\
                      +' secondes' #on ajoute également le temps de compression
        self.Label1.configure(text=self.tdComp, fg='grey')

    def compress(self):
        self.debut = time()
        compress_fichier(self.cheminFichier)
        self.fin = time()
        if self._thread1 is not None: # arrête l'éxécution du thread
            self._thread1 = None

    def init_comp(self):
        self.btnx.destroy()
        self.bouton1.configure(text="Choisir un Fichier", command=self.ChoisirFichier, state = DISABLED)
        self.bouton2.destroy()
        if self._thread1 is None: # on démarre le 1er thread et on l'associe à la fonction de compression
            self._thread1 = Thread(target=self.compress)
            self._thread1.start()
            self.init_anim_comp()

    def init_anim_comp(self):
        if self._thread2 is None: #on démarre le second thread et on l'associe à la fonction d'animation
            self._thread2 = Thread(target=self.animation_compression)
            self._thread2.start()

    def animation_compression(self):
        while self._thread1 is not None: #tant que le premier thread est en cours on anime
            self.Label1.configure(text="compression en cours.")
            sleep(0.1)
            self.Label1.configure(text="compression en cours..")
            sleep(0.1)
            self.Label1.configure(text="compression en cours...")
            sleep(0.1)
        if self._thread2 is not None: #on arrête le second thread
            self._thread2 = None
        self.tauxDeCompression()
        self.bouton1.configure(state=ACTIVE)
        showinfo("", "Fichier compressé")

    #on gère de la même manière les méthodes pour la décompression
    def decompress(self):
        decompress_fichier(self.cheminFichier)
        if self._thread1 is not None:
            self._thread1 = None

    def init_decomp(self):
        self.btnx.destroy()
        self.bouton1.configure(text="Choisir un Fichier", command=self.ChoisirFichier)
        self.bouton2.destroy()
        if self._thread1 is None:
            self._thread1 = Thread(target=self.decompress)
            self._thread1.start()
            self.init_anim_decomp()

    def init_anim_decomp(self):
        if self._thread2 is None:
            self._thread2 = Thread(target=self.animation_decompression)
            self._thread2.start()

    def animation_decompression(self):
        while self._thread1 is not None:
            self.Label1.configure(text="décompression en cours.")
            sleep(0.1)
            self.Label1.configure(text="décompression en cours..")
            sleep(0.1)
            self.Label1.configure(text="décompression en cours...")
            sleep(0.1)
        if self._thread2 is not None:
            self._thread2 = None
        self.supFichier()
        showinfo("", "Fichier décompressé")

if __name__ == '__main__':
    app = Application()
