
def mostrarMensaje(parametro):
    print(parametro)

def esperaRespuesta(parametros, funciones):
    var = input()
    index = None
    for i in range(len(parametros)):
        if var == parametros[i]:
            index = i
            break
    if index == None:
        mostrarMensaje("Esta opción no existe.")
        return esperaRespuesta(parametros, funciones)
    else:
        return funciones[index]