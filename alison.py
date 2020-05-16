def suma2(sumando1, sumando2):
    return sumando1 + sumando2


def multi2(multiplicando1, multiplicando2):
    return multiplicando1 * multiplicando2


def cuenta_palabras(texto):
    words = texto.split()
    return len(words)


def cuenta_palabra(texto, target_word):
    words = texto.split()
    filtered_list = list(filter(lambda current_word: current_word == target_word, words))
    return len(filtered_list)


if __name__ == '__main__':
    resultado = suma2(2, 3)
    print(resultado)

    resultado = multi2(2, 9)
    print(resultado)

    texto = """
    Es un hecho establecido hace demasiado tiempo que un lector se distraerá con el 
    contenido del texto de un sitio mientras que mira su diseño. El punto de usar 
    Lorem Ipsum es que tiene una distribución más o menos normal de las letras, al 
    contrario de usar textos como por ejemplo "Contenido aquí, contenido aquí". 
    Estos textos hacen parecerlo un español que se puede leer. Muchos paquetes de 
    autoedición y editores de páginas web usan el Lorem Ipsum como su texto por 
    defecto, y al hacer una búsqueda de "Lorem Ipsum" va a dar por resultado muchos
    sitios web que usan este texto si se encuentran en estado de desarrollo. 
    Muchas versiones han evolucionado a través de los años, algunas veces por 
    accidente, otras veces a propósito (por ejemplo insertándole humor y cosas por el estilo).
    """

    palabricas_num = cuenta_palabras(texto)
    print(palabricas_num)

    una_num = cuenta_palabra(texto, "caca")
    print(una_num)



