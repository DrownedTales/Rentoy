from time import sleep
import tkinter
from PIL import ImageTk, Image
import os

from events import Events

#ESTE CODIGO ES FEO DE COJONES Y HAY QUE LIMPIARLO. PERO FUNCIONA Y SOY VAGO

WINDOW_SIZE = (1080, 720)
WINDOW_PLAY_SIZE = (720, 720)
CARD_SIZE = 125
MY_CARD_SIZE = 175
HAND_FRAME_HEIGHT = 175
BACK_CARD_URL = "Images/detras.png"
BUTTON_IMG = "Images/buttontest1.png"
CARD_OFFSET = 50
MY_CARD_OFFSET = 175
BUTTON_FONT = ("Comic Sans MS", 20)
TITLE_FONT = ("Comic Sans MS", 30)
BASIC_FONT = ("Comic Sans MS", 15)
WINDOW_CARD_MARGIN = 50
SELECTED_CARD_MARGIN = 135
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
team_labels = []
points_label = None

vira_pos = None
secvira_pos = None
mazo_pos = None

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

def make_election_popup(label_text, options, funcs):
    global popup
    popup = tkinter.Toplevel()
    l = tkinter.Label(popup, text=label_text, font=BASIC_FONT)
    l.pack(pady=20)
    
    ltest = tkinter.Label(_root, text="blablablabla", font=BASIC_FONT)
    ltest.place(relx=0.5, rely=0.5)

    #popup.protocol("WM_DELETE_WINDOW", lambda: )
    res = espera_eleccion(options, funcs, popup)
    popup.destroy()

    ltest.destroy()

    return res

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
    pos = ((WINDOW_PLAY_SIZE[0]/2) + 30 + (MY_CARD_OFFSET*n), WINDOW_PLAY_SIZE[1] - (HAND_FRAME_HEIGHT/2))
    item = draw_image_animated("Images/" + card_path + ".png", CARD_SIZE, MY_CARD_SIZE, mazo_pos, pos, 0, 0, id, DRAW_CARD_TIME)
    main_canvas.tag_bind(item, '<ButtonPress-1>', lambda e: card_button_call(id, e))
    global hand_cards
    hand_cards[id] = item, pos

def draw_vira(card_path):
    draw_image_animated("Images/" + card_path + ".png", CARD_SIZE, CARD_SIZE, mazo_pos, vira_pos, 0, 0, "vira", DRAW_CARD_TIME)

def draw_sec_vira(card_path):
    #draw_image_animated("Images/" + card_path + ".png", CARD_SIZE, CARD_SIZE, mazo_pos, secvira_pos, 0, 0, "sec vira", DRAW_CARD_TIME)
    draw_image("Images/" + card_path + ".png", CARD_SIZE, secvira_pos, 0, "sec vira")

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
    l = tkinter.Label(_root, text=parametro, font=TITLE_FONT)
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

def espera_eleccion(parametros, funciones, base=_root):
    buttons = []
    for i in range(len(parametros)):
        button = make_button(base, parametros[i], "#FFFFFF", BUTTON_IMG, "eleccion" + str(i), lambda i=i: button_call(i))
        button.config(width=(WINDOW_PLAY_SIZE[0]/len(parametros)-30))
        button.pack(side=tkinter.LEFT, padx=20, expand=1, fill=tkinter.X, anchor=tkinter.N)
        buttons.append(button)

    while button_guard == False:
        sleep(0.05)

    return funciones[index_eleccion]

def recibe_respuesta():
    input_box = tkinter.Entry(_root, font=BASIC_FONT)
    input_box.pack(pady=20)

    button = make_button(_root, "aceptar", "#FFFFFF", BUTTON_IMG, "accept", button_call)
    button.config(width=200, height=100)
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
    path = id.replace("this player ", "")
    return path

def card_to_selected_up(card_name):
    id = "this player " + card_name
    pos = hand_cards[id][1]
    global main_canvas
    main_canvas.delete(hand_cards[id][0])
    hand_cards[id] = None
    images[id] = None
    draw_image_animated("Images/" + card_name + ".png", MY_CARD_SIZE, CARD_SIZE, pos, (WINDOW_PLAY_SIZE[0]/2, WINDOW_PLAY_SIZE[1]-HAND_FRAME_HEIGHT*1.5),\
        0, 0, "this player selected", DRAW_CARD_TIME)

def card_to_selected_down(card_name):
    id = "this player " + card_name
    pos = hand_cards[id][1]
    global main_canvas
    main_canvas.delete(hand_cards[id][0])
    hand_cards[id] = None
    images[id] = None
    draw_image_animated(BACK_CARD_URL, MY_CARD_SIZE, CARD_SIZE, pos, (WINDOW_PLAY_SIZE[0]/2, WINDOW_PLAY_SIZE[1]-HAND_FRAME_HEIGHT*1.5),\
        0, 0, "this player selected", DRAW_CARD_TIME)

def another_card_to_selected_up(card_name, player_name):
    n = len([i for i in images.keys() if player_name in i])
    id = player_name + " " + str(n)
    pos = player_pos[player_name][0]
    pos2 = player_pos[player_name][2]
    rot = player_pos[player_name][1]
    global main_canvas
    images[id] = None
    draw_image_animated("Images/" + card_name + ".png", MY_CARD_SIZE, CARD_SIZE, pos, pos2,\
        rot, rot, player_name + " selected", DRAW_CARD_TIME)

def another_card_to_selected_down(player_name):
    n = len([i for i in images.keys() if player_name in i])
    id = player_name + " " + str(n)
    pos = player_pos[player_name][0]
    pos2 = player_pos[player_name][2]
    rot = player_pos[player_name][1]
    global main_canvas
    images[id] = None
    draw_image_animated(BACK_CARD_URL, MY_CARD_SIZE, CARD_SIZE, pos, pos2,\
        rot, rot, player_name + " selected", DRAW_CARD_TIME)

def choose_action(options, res):
    for i in action_buttons:
        a = False
        for e in options:
            if e == i[0]:
                a = True
        if a:
            i[1].config(state="normal")

    while button_guard == False:
        sleep(0.05)

    for i in action_buttons:
        i[1].config(state="disabled")

    for i in range(len(options)):
        if options[i] == index_eleccion:
            return res[i]

def update_points(teams):
    global team_labels
    for i in team_labels:
        i.destroy()
    team_labels.clear()
    for i in range(len(teams)):
        name = list(teams.keys())[i]
        l = tkinter.Label(_root, text= name + ": " + str(teams[name]), font=BASIC_FONT)
        l.place(relx=0.75, rely=(0.1 + i*0.1))
        team_labels.append(l)

def update_on_play_points(points):
    global points_label
    points_label = tkinter.Label(_root, text="Puntos en juego: " + str(points), font=BASIC_FONT)
    points_label.place(relx=0.75, rely=0.3)

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

    global images
    images.clear()

    global vira_pos
    vira_pos = (WINDOW_SIZE[0]*0.85, WINDOW_SIZE[1]*0.5)
    l = tkinter.Label(_root, text="Vira", font=TITLE_FONT)
    l.place(relx=0.8, rely=0.6)

    global secvira_pos
    secvira_pos = (WINDOW_SIZE[0]*0.85, WINDOW_SIZE[1]*0.8)
    l = tkinter.Label(_root, text="Segunda vira", font=TITLE_FONT)
    l.place(relx=0.75, rely=0.9)

    global mazo_pos
    mazo_pos = (WINDOW_PLAY_SIZE[0]*0.5, WINDOW_PLAY_SIZE[1]*0.45)

    l = tkinter.Label(_root, text="Puntos", font=TITLE_FONT)
    l.place(relx=0.8, rely=0)
    
    #placeholder del mazo
    draw_image(BACK_CARD_URL, CARD_SIZE, mazo_pos, 0, "mazo")
    #botones
    up_button = make_button(_root, "Echar boca arriba", "#FFFFFF", BUTTON_IMG, "up button", lambda: button_call("Echar boca arriba"))
    up_button.config(state="disabled")
    up_button.place(relx=0.025, rely=0.8, relheight=0.075, relwidth=0.25)
    down_button = make_button(_root, "Echar boca abajo", "#FFFFFF", BUTTON_IMG, "down button", lambda: button_call("Echar boca abajo"))
    down_button.config(state="disabled")
    down_button.place(relx=0.025, rely=0.9, relheight=0.075, relwidth=0.25)
    envio_button = make_button(_root, "Envio", "#FFFFFF", BUTTON_IMG, "envio button", lambda: button_call("Envio"))
    envio_button.config(state="disabled")
    envio_button.place(relx=0.025, rely=0.7, relheight=0.075, relwidth=0.25)


    global action_buttons
    action_buttons = []
    action_buttons.append(("Echar boca arriba", up_button))
    action_buttons.append(("Echar boca abajo", down_button))
    action_buttons.append(("Envio", envio_button))

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
    global player_pos
    for i in range(len(order)):
            if i % 3 == 0:
                player_pos[order[i]] = ((WINDOW_CARD_MARGIN, (WINDOW_PLAY_SIZE[1] - HAND_FRAME_HEIGHT)/(len(side_left)+1)), 270,\
                    (WINDOW_CARD_MARGIN + SELECTED_CARD_MARGIN, (WINDOW_PLAY_SIZE[1] - CARD_OFFSET - HAND_FRAME_HEIGHT)/(len(side_left)+1)))
                l = tkinter.Label(_root, text=order[i], font=BASIC_FONT)
                l.place(x=player_pos[order[i]][0][0], y=player_pos[order[i]][0][1] - 50)
            elif i % 3  == 1:
                player_pos[order[i]] = (((WINDOW_PLAY_SIZE[0])/(len(side_top)+1), WINDOW_CARD_MARGIN), 180,\
                    ((WINDOW_PLAY_SIZE[0] + CARD_OFFSET)/(len(side_top)+1), WINDOW_CARD_MARGIN + SELECTED_CARD_MARGIN))
                l = tkinter.Label(_root, text=order[i], font=BASIC_FONT)
                l.place(x=player_pos[order[i]][0][0], y=player_pos[order[i]][0][1] - 50)
            elif i % 3 == 2:
                player_pos[order[i]] = ((WINDOW_PLAY_SIZE[0] - WINDOW_CARD_MARGIN, (WINDOW_PLAY_SIZE[1] - HAND_FRAME_HEIGHT)/(len(side_right)+1)), 90, \
                    (WINDOW_PLAY_SIZE[0] - WINDOW_CARD_MARGIN - SELECTED_CARD_MARGIN, (WINDOW_PLAY_SIZE[1] - CARD_OFFSET - HAND_FRAME_HEIGHT)/(len(side_left)+1)))
                l = tkinter.Label(_root, text=order[i], font=BASIC_FONT)
                l.place(x=player_pos[order[i]][0][0], y=player_pos[order[i]][0][1] + 50)

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
