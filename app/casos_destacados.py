"""
Contexto histórico para los 6 casos destacados del proyecto.

Investigado con búsquedas web (declarado en la nota metodológica del
Formulario de Inscripción, según Anexo A de las Bases y Condiciones).
Fuentes completas en el vault del proyecto ("Investigación Casos Destacados.md").
"""

CASOS_DESTACADOS = {
    "Neuquén": {
        "titulo": "Concentración productiva en torno a Vaca Muerta",
        "texto": (
            "Desde 2010, cuando YPF confirmó el potencial productivo de la Formación Vaca "
            "Muerta, Neuquén concentró su economía en los hidrocarburos no convencionales "
            "como ningún otro caso del país. La formación —30.000 km² en la Cuenca Neuquina, "
            "con 308 TCF de gas y 16.200 millones de barriles de petróleo— es la segunda "
            "reserva de gas no convencional y la cuarta de petróleo a nivel mundial. Atrajo "
            "inversión de YPF, Chevron, ExxonMobil y Total, y hoy aporta más de la mitad del "
            "petróleo y el gas que produce Argentina. Esa escala de inversión concentrada en "
            "un único recurso explica por qué Neuquén tiene, de las 24 jurisdicciones, la "
            "estructura productiva más concentrada del país."
        ),
        "fuente": "CONAE / Argentina.gob.ar; Real Instituto Elcano",
    },
    "Santiago del Estero": {
        "titulo": "La nueva frontera agrícola",
        "texto": (
            "El crecimiento del VAB santiagueño responde a la incorporación de una frontera "
            "agrícola nueva: desde los años 2000, la soja transgénica y los precios "
            "internacionales altos —impulsados en gran parte por la demanda china— hicieron "
            "rentable cultivar tierras extra-pampeanas hasta entonces marginales para la "
            "agricultura. Santiago del Estero pasó a ser una de las principales productoras "
            "de soja fuera de la región pampeana. El proceso tuvo un costo: desmonte de "
            "bosque nativo y desplazamiento de pequeños productores y trabajadores rurales "
            "que no pudieron adaptarse a la escala y tecnología del nuevo modelo agrícola."
        ),
        "fuente": "CONICET; Revista Pilquén (SciELO)",
    },
    "Tierra del Fuego, Antártida e Islas del Atlántico Sur": {
        "titulo": "Una estructura productiva inducida por política pública",
        "texto": (
            "A diferencia de Neuquén o Santiago del Estero, la estructura económica fueguina "
            "no responde a una ventaja natural sino a una política pública: la Ley 19.640 "
            "(1972) creó un régimen de exenciones impositivas y aduaneras para compensar el "
            "aislamiento geográfico de la provincia y sostener su poblamiento. Bajo ese "
            "régimen se instaló una industria de ensamblaje electrónico (televisores, "
            "celulares, aires acondicionados) que hoy explica buena parte del crecimiento "
            "fueguino en el período. El régimen fue prorrogado varias veces, la última "
            "extendiéndolo hasta 2038, lo que garantiza continuidad al modelo en el corto y "
            "mediano plazo."
        ),
        "fuente": "Ministerio de Producción y Ambiente de Tierra del Fuego; InfoLEG",
    },
    "Catamarca": {
        "titulo": "Cuando se agota el recurso",
        "texto": (
            "Catamarca es la única jurisdicción con una variación negativa del VAB entre "
            "2004 y 2022, y el caso más claro del dataset de una economía dependiente de un "
            "recurso finito. Bajo de la Alumbrera, primera mina de cobre a gran escala del "
            "país, operó entre 1997 y 2018 produciendo cobre, oro y molibdeno; en su pico "
            "llegó a representar el 77% de las exportaciones provinciales. Su cierre en "
            "2018 —dentro de la ventana temporal analizada— coincide con el estancamiento "
            "del agregado provincial. El sitio hoy se reconvierte para un nuevo proyecto "
            "minero (MARA), pero el caso ilustra el riesgo de una estructura productiva sin "
            "diversificación de reemplazo."
        ),
        "fuente": "Ámbito Financiero; Aprendamos de Minería",
    },
    "Ciudad Autónoma de Buenos Aires": {
        "titulo": "La continuidad de una transición ya consolidada",
        "texto": (
            "A diferencia de los demás casos, CABA no vive un \"boom\" durante 2004-2024 "
            "sino la continuidad de una transición ya consolidada antes del inicio de la "
            "serie. Durante los años 90, en el marco de la apertura económica y financiera "
            "de la convertibilidad, la ciudad atravesó un proceso de desindustrialización "
            "más intenso que el resto del país: la manufactura cayó del 16% al 11,4% del "
            "producto entre 1993 y 2001, mientras los servicios financieros e inmobiliarios "
            "ganaban participación. Hoy los servicios explican cerca de tres cuartas partes "
            "del VAB porteño, muy por encima del promedio nacional, con la intermediación "
            "financiera como una de las ramas de mayor peso."
        ),
        "fuente": "Dirección General de Estadística y Censos (GCBA); IADE",
    },
    "Corrientes": {
        "titulo": "Crecer sin transformarse",
        "texto": (
            "Corrientes es el contraejemplo de esta selección: no tuvo un shock puntual que "
            "reconfigurara su estructura productiva. Desde 1920, cuando el crecimiento del "
            "mercado interno impulsó la diversificación de una economía hasta entonces casi "
            "exclusivamente ganadera, la provincia construyó una canasta agropecuaria y "
            "forestal estable que se mantiene hasta hoy: es la primera productora de arroz "
            "del país, la segunda de yerba mate y la primera en superficie de bosque "
            "implantado. Esa estabilidad se refleja en un índice de concentración sectorial "
            "casi idéntico entre 2004 y 2024 — la prueba de que crecimiento (+61% en el "
            "período) no siempre implica transformación estructural."
        ),
        "fuente": "Secretaría de Provincias; Argentina.gob.ar",
    },
}
