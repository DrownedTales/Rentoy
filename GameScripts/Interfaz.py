from asyncio import events
from time import sleep
import tkinter
from PIL import ImageTk, Image
import os

from GameScripts.CartaScripts.Carta import Carta
from events import Events

WINDOW_SIZE = (1080, 720)
CARD_SIZE = 150
MY_CARD_SIZE = 200
HAND_FRAME_HEIGHT = 100
BACK_CARD_URL = "Images/test3.png"
BUTTON_IMG = "Images/buttontest1.png"
CARD_OFFSET = 30
MY_CARD_OFFSET = 100
BUTTON_FONT = ("Alice in Wonderland", 40)
TITLE_FONT = ("Alice in Wonderland", 40)
BASIC_FONT = ("Alice in Wonderland", 40)

#prevents images being garbage collected
#ya podria hacerlo el puto tkinter, llevo tres horas para averiguar por que no funcionaba esta mierda
images = dict()
main_canvas = None
_root = None
player_pos = dict()
events = Events()
popup = None

button_guard = False
index_eleccion = None

def clear_window():
    images.clear()
    for i in _root.winfo_children():
        if i != popup:
            i.destroy()

def make_button(base, _text, text_color, img_path, id, anim_func):
    if img_path != None:
        img = ImageTk.PhotoImage(file=img_path)
        images[id] = img
    else:
        img = None
    return tkinter.Button(base, fg=text_color, text=_text, image=img, command=anim_func, compound=tkinter.CENTER, \
        highlightthickness=0, bd=0, relief=tkinter.SUNKEN, activeforeground=text_color, font=BUTTON_FONT, cursor="hand2")

def __on_popup_close(func):
    global popup
    popup.destroy()
    if func != None:
        func()

def make_error_popup(parametro, func):
    global popup
    popup = tkinter.Toplevel()
    l = tkinter.Label(popup, text=parametro, font=BASIC_FONT)
    l.pack(pady=20)
    popup.protocol("WM_DELETE_WINDOW", lambda: __on_popup_close(func))
    button = make_button(popup, "Aceptar", "#FFFFFF", None, None, lambda: __on_popup_close(func))
    button.config(bg="blue")
    button.pack()


def draw_image(img_url, size, pos, rot, id):
    img= (Image.open(img_url))
    resized_image= img.resize((size, size), Image.ANTIALIAS)
    rotated_image= resized_image.rotate(rot)
    one = ImageTk.PhotoImage(rotated_image)
    images[id] = one
    main_canvas.create_image(pos[0], pos[1], image=one, tag=id)    

def draw_hand_card(card: Carta, player_name):
    n = len([i for i in images.keys() if player_name in i])
    draw_image("Images/" + card.to_string() + ".png", MY_CARD_SIZE,\
        ((WINDOW_SIZE[0]/2) - CARD_OFFSET + (CARD_OFFSET*n), WINDOW_SIZE[1] - (HAND_FRAME_HEIGHT/2)),\
            0, player_name + " " + card.to_string())

def draw_hidden_card(player_name):
    n = len([i for i in images.keys() if player_name in i])
    if player_pos[player_name][1] == 90:
        pos = (player_pos[player_name][0][0], player_pos[player_name][0][1] + CARD_OFFSET*n)
    elif player_pos[player_name][1] == 180:
        pos = (player_pos[player_name][0][0]  + CARD_OFFSET*n, player_pos[player_name][0][1])
    elif player_pos[player_name][1] == 270:
        pos = (player_pos[player_name][0][0], player_pos[player_name][0][1] - CARD_OFFSET*n)

    draw_image(BACK_CARD_URL, CARD_SIZE, pos, player_pos[player_name][1], player_name + " " + str(n))

def mostrarMensaje(parametro):
    l = tkinter.Label(_root, text=parametro, font=("Alice in Wonderland", 40))
    l.pack(pady=20)

def button_call(index = None): #si, ya se que esto es una chapuza. son las 3 y tengo sueño dejame
    global index_eleccion
    index_eleccion = index
    global button_guard
    button_guard = True
    sleep(0.1)
    button_guard = False

def espera_eleccion(parametros, funciones):
    buttons = []
    for i in range(len(parametros)):
        button = make_button(_root, parametros[i], "#FFFFFF", BUTTON_IMG, "eleccion" + str(i), lambda i=i: button_call(i))
        button.config(width=(WINDOW_SIZE[0]/len(parametros)-30))
        button.pack(side=tkinter.LEFT, padx=20, expand=1, fill=tkinter.X, anchor=tkinter.N)
        buttons.append(button)

    while button_guard == False:
        sleep(0.05)

    return funciones[index_eleccion]

def recibe_respuesta():
    input_box = tkinter.Entry(_root, font=("Alice in Wonderland", 40))
    input_box.pack(pady=20)

    button = make_button(_root, "aceptar", "#FFFFFF", BUTTON_IMG, "accept", button_call)
    button.pack(pady=20)

    id = _root.bind('<Return>', button_call)
    
    while button_guard == False:
        sleep(0.05)
    var = input_box.get()

    _root.unbind('<Return>', id)
    return var


def main_loop():
    root = tkinter.Tk()
    #window
    root.title("Rentoy")
    root.iconbitmap(os.path.join("Images", "icon.ico"))
    global _root
    _root = root
    _root.geometry(str(WINDOW_SIZE[0])+"x"+str(WINDOW_SIZE[1]))

    _root.protocol("WM_DELETE_WINDOW", events.on_close)

    #cosas de menus

    root.mainloop()

def start_game(players, player_name):
    clear_window()
    print("iniciando pantalla de juego")
    #canvas
    canvas = tkinter.Canvas(_root, height=WINDOW_SIZE[1], width=WINDOW_SIZE[0])
    canvas.pack()
    global main_canvas
    main_canvas = canvas

    main_canvas.delete("all")
    images.clear()
    #placeholder de la pila
    draw_image("Images/test1.png", CARD_SIZE, (WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2), 0, "pila")
    #placeholder del mazo
    draw_image("Images/test2.png", CARD_SIZE, (WINDOW_SIZE[0]*0.7, WINDOW_SIZE[1]/2), 0, "mazo")

    order = []
    index: int = None
    for i in range(len(players)):
        if players[i] == player_name:
            index = i
    for i in players[index + 1:]:
        order.append(i)
    for i in players[:index]:
        order.append(i)

    max_n = int(len(order)/3)
    rest = len(order) % 3
    for i in range(len(order)):
        if i < max_n*2:
            if i < max_n:
                player_pos[order[i]] = ((30, (WINDOW_SIZE[1] - HAND_FRAME_HEIGHT)/max_n), 270)
            else:
                player_pos[order[i]] = (((WINDOW_SIZE[0])/max_n, 30), 180)
        else:
            break
    for i in range(rest):
        player_pos[order[i]] = ((WINDOW_SIZE[0] - 30, (WINDOW_SIZE[1] - HAND_FRAME_HEIGHT)/max_n), 90)

def connection_screen():
    clear_window()
    button1 = make_button(_root, "CONECTAR", "#FFFFFF", BUTTON_IMG, "connect button", events.on_connect)
    button2 = make_button(_root, "CREAR SALA", "#FFFFFF", BUTTON_IMG, "crear button", events.on_create)
    button1.place(rely=0.25, relx=0.5, relheight=0.2, relwidth=0.75, anchor=tkinter.CENTER)
    button2.place(rely=0.75, relx=0.5, relheight=0.2, relwidth=0.75, anchor=tkinter.CENTER)

def waiting_players(jugadores, total_jugadores):
    clear_window()
    mostrarMensaje("Esperando jugadores: " + str(len(jugadores)) + " / " + str(total_jugadores))
    for i in jugadores:
        mostrarMensaje(i)

def waiting_teams(equipos):
    clear_window()
    mostrarMensaje("Esperando equipos:")
    for i in equipos.keys():
        frame = tkinter.Frame(_root, width=(WINDOW_SIZE[0]/len(equipos.keys())-30))
        frame.pack(side=tkinter.LEFT, padx=20, anchor=tkinter.N, fill=tkinter.X, expand=1)
        l = tkinter.Label(frame, text=i, font=TITLE_FONT)
        l.pack()
        for e in equipos[i]:
            a = tkinter.Label(frame, text=e, font=BASIC_FONT)
            a.pack()
