def asignar_mesas_automatico(evento):
    
    # 1. Limpiar asignaciones previas
    for mesa in evento.mesas:
        mesa.participantes = []
    for participante in evento.participantes:
        participante.mesa_asignada = None
    
    # 2. Lista de participantes sin asignar
    sin_asignar = evento.participantes.copy()
    
    # 3. Asignar cada participante
    for participante in sin_asignar:
        mejor_mesa = None
        mejor_puntuacion = -999
        
        # Buscar la mejor mesa para este participante
        for mesa in evento.mesas:
            # Si la mesa está llena, saltar
            if mesa.estaLlena():
                continue
            
            # Verificar conflictos: si alguno de la mesa está en evitados
            tiene_conflicto = False
            for p in mesa.participantes:
                if p.nombre in participante.evitados or participante.nombre in p.evitados:
                    tiene_conflicto = True
                    break
            
            if tiene_conflicto:
                continue
            
            # Calcular puntuación de esta mesa
            puntuacion = 0
            
            # +10 puntos por cada preferencia que ya está en la mesa
            for p in mesa.participantes:
                if p.nombre in participante.preferencias:
                    puntuacion += 10
            
            # +5 puntos por llenar mesas (preferir mesas con gente)
            puntuacion += len(mesa.participantes) * 5
            
            # Actualizar si es la mejor hasta ahora
            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_mesa = mesa
        
        # Asignar a la mejor mesa encontrada
        if mejor_mesa:
            mejor_mesa.anadirParticipante(participante)
            participante.mesa_asignada = mejor_mesa.id_mesa
    
    # 4. Detectar excepciones (conflictos que quedaron)
    excepciones = []
    for mesa in evento.mesas:
        for i, p1 in enumerate(mesa.participantes):
            for p2 in mesa.participantes[i+1:]:
                if p2.nombre in p1.evitados or p1.nombre in p2.evitados:
                    if p1 not in excepciones:
                        excepciones.append(p1)
                    if p2 not in excepciones:
                        excepciones.append(p2)
    
    return excepciones