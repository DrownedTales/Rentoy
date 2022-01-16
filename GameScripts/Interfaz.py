def mostrarMensaje(parametro):
    print(parametro)

def espera_eleccion(parametros, funciones):
    var = input()
    index = None
    for i in range(len(parametros)):
        if var == parametros[i]:
            index = i
            break
    if index == None:
        mostrarMensaje("Esta opción no existe.")
        return espera_eleccion(parametros, funciones)
    else:
        return funciones[index]


def recibe_respuesta():
    return input()