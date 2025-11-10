# -*- coding: utf-8 -*-
# models/participante.py

class Participante:
    """
    Clase modelo que representa a un participante (invitado).
    No debe contener lógica de interfaz ni dependencias de PyQt.
    """

    def __init__(self, id_participante, nombre):
        
        self.id_participante = id_participante
        self.nombre = nombre

        # Listas de nombres (podrías cambiarlas a objetos Participante si lo necesitas)
        self.preferencias = []
        self.evitados = []

        # Para guardar el id de la mesa asignada
        self.mesa_asignada = None
        

    # --- MÉTODOS DE GESTIÓN DE PREFERENCIAS ---

    def anadir_preferencia(self, nombre_participante):
        """Añade a otro participante como preferido."""
        if (
            nombre_participante not in self.preferencias
            and nombre_participante != self.nombre
        ):
            self.preferencias.append(nombre_participante)
            return True
        return False

    def eliminar_preferencia(self, nombre_participante):
        """Elimina un nombre de la lista de preferencias."""
        try:
            self.preferencias.remove(nombre_participante)
            return True
        except ValueError:
            return False

    # --- MÉTODOS DE GESTIÓN DE EVITADOS ---

    def anadir_evitado(self, nombre_participante):
        """Añade a otro participante a la lista de evitados."""
        if (
            nombre_participante not in self.evitados
            and nombre_participante != self.nombre
        ):
            self.evitados.append(nombre_participante)
            return True
        return False

    def eliminar_evitado(self, nombre_participante):
        """Elimina a otro participante de la lista de evitados."""
        try:
            self.evitados.remove(nombre_participante)
            return True
        except ValueError:
            return False

    # --- MÉTODOS DE GESTIÓN DE MESA ---

    def asignar_mesa(self, id_mesa):
        """Asigna una mesa al participante."""
        self.mesa_asignada = id_mesa

    def quitar_mesa(self):
        """Elimina la asignación de mesa."""
        self.mesa_asignada = None

    # --- CONSULTAS / UTILIDADES ---

    def tiene_conflicto_con(self, otro_nombre):
        """Devuelve True si el participante no puede sentarse con otro."""
        return otro_nombre in self.evitados

    def mostrar_info(self):
        """Devuelve un resumen del participante."""
        return {
            "id": self.id_participante,
            "nombre": self.nombre,
            "preferencias": list(self.preferencias),
            "evitados": list(self.evitados),
            "mesa_asignada": self.mesa_asignada,
        }

    def __repr__(self):
        return f"Participante({self.id_participante}, {self.nombre})"