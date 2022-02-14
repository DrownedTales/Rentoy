from asyncio import events
from time import sleep
import tkinter
from PIL import ImageTk, Image
import os

from events import Events

#ESTE CODIGO ES FEO DE COJONES Y HAY QUE LIMPIARLO. PERO FUNCIONA Y SOY VAGO

WINDOW_SIZE = (1080, 720)
CARD_SIZE = 150
MY_CARD_SIZE = 250
HAND_FRAME_HEIGHT = 150
BACK_CARD_URL = "Images/test3.png"
BUTTON_IMG = "Images/buttontest1.png"
CARD_OFFSET = 30
MY_CARD_OFFSET = 100
BUTTON_FONT = ("Alice in Wonderland", 40)
TITLE_FONT = ("Alice in Wonderland", 40)
BASIC_FONT = ("Alice in Wonderland", 40)
WINDOW_CARD_MARGIN = 50
ANIMATION_FRAMES = 60
DRAW_CARD_TIME = 0.2

#prevents images being garbage collected
#ya podria hacerlo el puto tkinter, llevo tres horas para averiguar por que no funcionaba esta mierda
images = dict()
main_canvas = None
_root = None
player_pos = dict()
events = Events()
popup = None
action_buttons = []
hand_cards = dict()

vira_pos = None
secvira_pos = None
mazo_pos = None
pila_pos = None

button_guard = False
card_guard = False
index_eleccion = None
carta_eleccion = None

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

def draw_source_image(img, size, pos, rot, id):
    resized_image= img.resize((size, size), Image.ANTIALIAS)
    rotated_image= resized_image.rotate(rot)
    one = ImageTk.PhotoImage(rotated_image)
    images[id] = one
    res = main_canvas.create_image(pos[0], pos[1], image=one, tag=id)
    return res

def draw_image(img_url, size, pos, rot, id):
    img= (Image.open(img_url))
    draw_source_image(img, size, pos, rot, id)

#por ahora la interpolacion es solo lineal, igual luego investigo como hacer curvas o uso otras f(x)
def draw_image_animated(img_url, size1, size2, pos1, pos2, rot1, rot2, id, time):
    img= (Image.open(img_url))

    anim_frames = int(time*ANIMATION_FRAMES)
    for i in range(anim_frames+1):
        size = int(size2 * (i/anim_frames) + size1 * (1 - (i/anim_frames)))
        pos = (int(pos2[0] * (i/anim_frames) + pos1[0] * (1 - (i/anim_frames))),\
            int(pos2[1] * (i/anim_frames) + pos1[1] * (1 - (i/anim_frames))))
        rot = int(rot2 * (i/anim_frames) + rot1 * (1 - (i/anim_frames)))
        res = draw_source_image(img, size, pos, rot, id)

        #print(str(i) + " de " + str(anim_frames))

        sleep(time/ANIMATION_FRAMES)
    return res

def draw_hand_card(card_path):
    n = len([i for i in images.keys() if "this player" in i])
    #print("images keys", images.keys())
    id = "this player" + " " + card_path
    pos = ((WINDOW_SIZE[0]/2) - MY_CARD_OFFSET + (MY_CARD_OFFSET*n), WINDOW_SIZE[1] - (HAND_FRAME_HEIGHT/2))
    item = draw_image_animated("Images/" + card_path + ".png", CARD_SIZE, MY_CARD_SIZE, mazo_pos, pos, 0, 0, id, DRAW_CARD_TIME)
    main_canvas.tag_bind(item, '<ButtonPress-1>', lambda e: card_button_call(id, e))
    global hand_cards
    hand_cards[id] = item, pos

def draw_vira(card_path):
    draw_image_animated("Images/" + card_path + ".png", CARD_SIZE, CARD_SIZE, mazo_pos, vira_pos, 0, 0, "vira", DRAW_CARD_TIME)

def draw_hidden_card(player_name):
    n = len([i for i in images.keys() if player_name in i])
    if player_pos[player_name][1] == 90:
        pos = (player_pos[player_name][0][0], player_pos[player_name][0][1] + CARD_OFFSET*n)
    elif player_pos[player_name][1] == 180:
        pos = (player_pos[player_name][0][0]  + CARD_OFFSET*n, player_pos[player_name][0][1])
    elif player_pos[player_name][1] == 270:
        pos = (player_pos[player_name][0][0], player_pos[player_name][0][1] - CARD_OFFSET*n)

    rot = player_pos[player_name][1]
    draw_image_animated(BACK_CARD_URL, CARD_SIZE, CARD_SIZE, mazo_pos, pos, 0, rot, player_name + " " + str(n), DRAW_CARD_TIME)

def mostrarMensaje(parametro):
    l = tkinter.Label(_root, text=parametro, font=BASIC_FONT)
    l.pack(pady=20)

def button_call(index = None): #si, ya se que esto es una chapuza. son las 3 y tengo sueño dejame
    global index_eleccion
    index_eleccion = index
    global button_guard
    button_guard = True
    sleep(0.1)
    button_guard = False

def card_button_call(index, e): #si, ya se que esto es una chapuza. son las 3 y tengo sueño dejame
    global carta_eleccion
    carta_eleccion = index, e
    global card_guard
    card_guard = True
    sleep(0.1)
    card_guard = False

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
    input_box = tkinter.Entry(_root, font=BASIC_FONT)
    input_box.pack(pady=20)

    button = make_button(_root, "aceptar", "#FFFFFF", BUTTON_IMG, "accept", button_call)
    button.pack(pady=20)

    id = _root.bind('<Return>', button_call)
    
    while button_guard == False:
        sleep(0.05)
    var = input_box.get()

    _root.unbind('<Return>', id)
    return var

def select_hand_card():
    print("selecting")
    while card_guard == False:
        sleep(0.05)

    id = carta_eleccion[0]
    print("choosen card", id)
    pos = hand_cards[id][1]
    path = id.replace("this player ", "")
    global main_canvas
    main_canvas.delete(hand_cards[id][0])
    hand_cards[id] = None
    images[id] = None
    draw_image_animated("Images/" + path + ".png", MY_CARD_SIZE, CARD_SIZE, pos, (WINDOW_SIZE[0]/2, WINDOW_SIZE[1]*0.65),\
        0, 0, "this player selected", DRAW_CARD_TIME)
    return path

def choose_action(options, res):
    for i in action_buttons:
        a = False
        for e in options:
            if e == i.cget('text'): #feo, estupido, son las 1:30 y me dije hace una hora que iba a parar ya. Ayuda
                a = True
        if a:
            i.config(state="normal")

    while button_guard == False:
        sleep(0.05)

    for i in action_buttons:
        i.config(state="disabled")

    for i in range(len(options)):
        if options[i] == index_eleccion:
            return res[i]

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

    global vira_pos
    vira_pos = (WINDOW_SIZE[0]*0.4, WINDOW_SIZE[1]*0.25)
    global secvira_pos
    secvira_pos = (WINDOW_SIZE[0]*0.6, WINDOW_SIZE[1]*0.25)
    global mazo_pos
    mazo_pos = (WINDOW_SIZE[0]*0.6, WINDOW_SIZE[1]*0.5)
    global pila_pos
    pila_pos = (WINDOW_SIZE[0]*0.4, WINDOW_SIZE[1]*0.5)
    
    #placeholder de la pila
    draw_image("Images/test1.png", CARD_SIZE, mazo_pos, 0, "pila")
    #placeholder del mazo
    draw_image("Images/test2.png", CARD_SIZE, pila_pos, 0, "mazo")
    #botones
    up_button = make_button(_root, "Echar boca arriba", "#FFFFFF", BUTTON_IMG, "up button", lambda: button_call("Echar boca arriba"))
    up_button.config(state="disabled")
    up_button.place(relx=0.025, rely=0.7, relheight=0.1, relwidth=0.3)
    down_button = make_button(_root, "Echar boca abajo", "#FFFFFF", BUTTON_IMG, "down button", lambda: button_call("Echar boca abajo"))
    down_button.config(state="disabled")
    down_button.place(relx=0.025, rely=0.85, relheight=0.1, relwidth=0.3)

    global action_buttons
    action_buttons.append(up_button)
    action_buttons.append(down_button)

    order = []
    index: int = None
    for i in range(len(players)):
        if players[i] == player_name:
            index = i
    for i in players[index + 1:]:
        order.append(i)
    for i in players[:index]:
        order.append(i)

    #estoy convencidisimo de que hay una forma mil veces mas eficiente de hacer esto. Dicho lo cual, no creo que tu ordenador vaya
    #a petar por jugar al rentoy
    side_left = []
    side_right = []
    side_top = []
    for i in range(len(order)):
            if i % 3 == 0:
                side_left.append(i)
            elif i % 3  == 1:
                side_right.append(i)
            elif i % 3 == 2:
                side_top.append(i)
    for i in range(len(order)):
            if i % 3 == 0:
                player_pos[order[i]] = ((WINDOW_CARD_MARGIN, (WINDOW_SIZE[1] - HAND_FRAME_HEIGHT)/(len(side_left)+1)), 270)
            elif i % 3  == 1:
                player_pos[order[i]] = (((WINDOW_SIZE[0])/(len(side_top)+1), WINDOW_CARD_MARGIN), 180)
            elif i % 3 == 2:
                player_pos[order[i]] = ((WINDOW_SIZE[0] - WINDOW_CARD_MARGIN, (WINDOW_SIZE[1] - HAND_FRAME_HEIGHT)/(len(side_right)+1)), 90)
    print(player_pos)

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
