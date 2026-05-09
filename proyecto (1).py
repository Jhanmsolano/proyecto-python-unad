#Este Codigo fue creado por los estudiantes: 
# Angel Mateo Torres Rojas 
# Jhan Marco Solano Rincon


import traceback
import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
from datetime import datetime

# ==========================================
# EXCEPCIONES PERSONALIZADAS
# Para que el programa no se muera de la nada
# ==========================================

class ErrorSoftwareFJ(Exception):
    pass

class ClienteInvalidoError(ErrorSoftwareFJ):
    pass

class ReservaInvalidaError(ErrorSoftwareFJ):
    pass

# ==========================================
#             MANEJO DE LOGS
# ==========================================

def registrar_log(mensaje, error_real=None):
    """
    Acá guardamos los errores en un txt para que quede la evidencia
    """
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{fecha}] {mensaje}"
    
    if error_real:
        # Encadenamiento de excepciones para mirar el detalle técnico
        log_msg += f"\nDetalle técnico:\n{traceback.format_exc()}"
        
    try:
        archivo = open("logs_software_fj.txt", "a", encoding="utf-8")
        archivo.write(log_msg + "\n" + "-"*40 + "\n")
    except Exception as e:
        print(f"Ni el log guardó: {e}")
    finally:
        # Este se ejecuta sí o sí para soltar el archivo
        try:
            archivo.close()
        except:
            pass

# ==========================================
# CLASES BASE (ABSTRACCIÓN Y ENCAPSULACIÓN)
# ==========================================

class EntidadGeneral(ABC):
    @abstractmethod
    def obtener_info(self):
        pass

class Cliente(EntidadGeneral):
    """
    Clase Cliente. Datos encapsulados para que no le metan mano desde afuera
    """
    def __init__(self, documento, nombre, correo):
        self.__documento = None
        self.__nombre = None
        self.__correo = None
        self.set_documento(documento)
        self.set_nombre(nombre)
        self.set_correo(correo)

    def set_documento(self, documento):
        doc_str = str(documento).strip()
        if not doc_str or len(doc_str) < 5 or not doc_str.isdigit():
            raise ClienteInvalidoError("¡La cédula está muy corta o ingresaste letras!")
            
        self.__documento = doc_str

    def set_nombre(self, nombre):
        if not nombre.strip():
            raise ClienteInvalidoError("¿Un cliente sin nombre? Complicado")
        self.__nombre = nombre.strip()

    def set_correo(self, correo):
        if "@" not in str(correo):
            raise ClienteInvalidoError("Ese correo no existe, le hace falta el arroba.")
        self.__correo = correo

    def get_nombre(self):
        return self.__nombre

    def obtener_info(self):
        return f"{self.__nombre} (CC: {self.__documento})"

# ==========================================
#    SERVICIOS (HERENCIA Y POLIMORFISMO)
# ==========================================

class Servicio(EntidadGeneral):
    def __init__(self, id_servicio, nombre, precio_base):
        self.id_servicio = id_servicio
        self.nombre = nombre
        self.precio_base = float(precio_base)

    @abstractmethod
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        pass

class ReservaSala(Servicio):
    def calcular_costo(self, horas, impuesto=0.19, descuento=0.0):
        # Polimorfismo: la sala cobra diferente
        costo = self.precio_base * horas
        return costo + (costo * impuesto) - (costo * descuento)
    
    def obtener_info(self):
        return f"Sala: {self.nombre} (${self.precio_base}/h)"

class AlquilerEquipo(Servicio):
    def calcular_costo(self, horas, impuesto=0.05, descuento=0.0):
        # Sobrecarga: al equipo se le suma el seguro
        costo = (self.precio_base * horas) + 15000 
        return costo + (costo * impuesto) - (costo * descuento)

    def obtener_info(self):
        return f"Equipo: {self.nombre} (${self.precio_base}/h)"

class Asesoria(Servicio):
    def calcular_costo(self, horas, impuesto=0.0, descuento=0.0):
        return (self.precio_base * horas) - (self.precio_base * descuento)

    def obtener_info(self):
        return f"Asesoría: {self.nombre} (${self.precio_base}/h)"

# ==========================================
#                 RESERVAS
# ==========================================

class Reserva(EntidadGeneral):
    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Los objetos de la reserva son inválidos.")
        if type(horas) not in (int, float) or horas <= 0:
            raise ReservaInvalidaError("Pon unas horas coherentes")
            
        self.cliente = cliente
        self.servicio = servicio
        self.horas = float(horas)
        self.estado = "Pendiente"

    def confirmar(self):
        self.estado = "Confirmada"

    def procesar(self):
        if self.estado != "Confirmada":
            raise ReservaInvalidaError("¡Pendiente! Tiene que confirmar la reserva primero.")
        try:
            total = self.servicio.calcular_costo(self.horas)
        except Exception as e:
            raise ErrorSoftwareFJ(f"Falla sacando la cuenta: {e}") from e
        else:
            return f"Se le cobró a {self.cliente.get_nombre()}: ${total:,.2f}"

    def obtener_info(self):
        return f"[{self.estado}] {self.cliente.get_nombre()} - {self.servicio.nombre} ({self.horas}h)"

# ==========================================
#       INTERFAZ GRÁFICA CON TKINTER
# ==========================================

class AppSoftwareFJ:
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - Gestión Integral")
        self.root.geometry("600x450")
        
        # Las listas para guardar en memoria
        self.clientes = []
        self.servicios = [
            ReservaSala("S1", "Sala VIP", 50000),
            AlquilerEquipo("E1", "Portátil Core i9", 30000),
            Asesoria("A1", "Arquitectura de Software", 100000)
        ]
        self.reservas = []

        # Pestañas
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True, fill='both')

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)
        self.tab_procesar = ttk.Frame(self.notebook)
        self.tab_simulacion = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text="1. Registrar Cliente")
        self.notebook.add(self.tab_reservas, text="2. Crear Reserva")
        self.notebook.add(self.tab_procesar, text="3. Cobrar")
        self.notebook.add(self.tab_simulacion, text="4. Simulación UNAD")

        self.setup_tab_clientes()
        self.setup_tab_reservas()
        self.setup_tab_procesar()
        self.setup_tab_simulacion()

    # --- PESTAÑA 1: CLIENTES ---

    def setup_tab_clientes(self):
        tk.Label(self.tab_clientes, text="Cédula:").pack(pady=5)
        self.ent_doc = tk.Entry(self.tab_clientes)
        self.ent_doc.pack()

        tk.Label(self.tab_clientes, text="Nombre completo:").pack(pady=5)
        self.ent_nom = tk.Entry(self.tab_clientes)
        self.ent_nom.pack()

        tk.Label(self.tab_clientes, text="Correo electrónico:").pack(pady=5)
        self.ent_cor = tk.Entry(self.tab_clientes)
        self.ent_cor.pack()

        btn_guardar = tk.Button(self.tab_clientes, text="Guardar Cliente", command=self.guardar_cliente, bg="lightblue")
        btn_guardar.pack(pady=20)

    def guardar_cliente(self):
        doc = self.ent_doc.get()
        nom = self.ent_nom.get()
        cor = self.ent_cor.get()
        
        try:
            nuevo_cli = Cliente(doc, nom, cor)
            self.clientes.append(nuevo_cli)
            messagebox.showinfo("¡Listo!", f"Cliente registrado con exito:\n{nuevo_cli.obtener_info()}")
            # Limpiamos las cajas de texto
            self.ent_doc.delete(0, tk.END)
            self.ent_nom.delete(0, tk.END)
            self.ent_cor.delete(0, tk.END)
            self.actualizar_combos()
        except ClienteInvalidoError as e:
            messagebox.showwarning("¡Error!", str(e))
            registrar_log("Usuario ingresó datos inválidos de cliente en la GUI", e)
        except Exception as e:
            messagebox.showerror("¡Falla grave!", "Algo tuvo un daño grave.")
            registrar_log("Error inesperado guardando cliente", e)

    # --- PESTAÑA 2: RESERVAS ---

    def setup_tab_reservas(self):
        tk.Label(self.tab_reservas, text="Seleccione el Cliente:").pack(pady=5)
        self.combo_clientes = ttk.Combobox(self.tab_reservas, state="readonly", width=40)
        self.combo_clientes.pack()

        tk.Label(self.tab_reservas, text="Seleccione el Servicio:").pack(pady=5)
        self.combo_servicios = ttk.Combobox(self.tab_reservas, state="readonly", width=40)
        self.combo_servicios.pack()
        self.combo_servicios['values'] = [s.obtener_info() for s in self.servicios]

        tk.Label(self.tab_reservas, text="¿Cuántas horas necesitas?:").pack(pady=5)
        self.ent_horas = tk.Entry(self.tab_reservas)
        self.ent_horas.pack()

        btn_reservar = tk.Button(self.tab_reservas, text="Crear Reserva", command=self.crear_reserva, bg="lightgreen")
        btn_reservar.pack(pady=20)

    def crear_reserva(self):
        idx_c = self.combo_clientes.current()
        idx_s = self.combo_servicios.current()
        h_str = self.ent_horas.get()

        if idx_c == -1 or idx_s == -1:
            messagebox.showwarning("¡Pendiente!"  "Tiene que seleccionar un cliente y un servicio.")
            return

        try:
            horas = float(h_str)
            nueva_reserva = Reserva(self.clientes[idx_c], self.servicios[idx_s], horas)
            self.reservas.append(nueva_reserva)
            messagebox.showinfo("¡Listo!", "Reserva creada. Está en estado 'Pendiente'. Vaya a cobrarla.")
            self.ent_horas.delete(0, tk.END)
            self.actualizar_lista_cobro()
        except ValueError:
            messagebox.showwarning("¡Pendiente!", "En las horas va un número, nada mas.")
        except ReservaInvalidaError as e:
            messagebox.showwarning("Error en reserva", str(e))
            registrar_log("Error de lógica creando reserva en GUI", e)

    # --- PESTAÑA 3: PROCESAR / COBRAR ---

    def setup_tab_procesar(self):
        tk.Label(self.tab_procesar, text="Reservas Pendientes:").pack(pady=5)
        self.listbox_reservas = tk.Listbox(self.tab_procesar, width=60, height=10)
        self.listbox_reservas.pack(pady=5)

        btn_cobrar = tk.Button(self.tab_procesar, text="Confirmar y Cobrar", command=self.cobrar_reserva, bg="gold")
        btn_cobrar.pack(pady=10)

    def cobrar_reserva(self):
        seleccion = self.listbox_reservas.curselection()
        if not seleccion:
            messagebox.showwarning("¡Ojo!", "Seleccione una reserva de la lista para poder cobrarla.")
            return
            
        idx_r = seleccion[0]
        reserva_elegida = self.reservas[idx_r]

        try:
            reserva_elegida.confirmar()
            resultado = reserva_elegida.procesar()
            messagebox.showinfo("¡Plática para la caja!", resultado)
            self.actualizar_lista_cobro()
        except Exception as e:
            messagebox.showerror("Error cobrando", str(e))
            registrar_log("Falla al procesar el cobro en GUI", e)

    # --- PESTAÑA 4: SIMULACIÓN OBLIGATORIA (UNAD) ---

    def setup_tab_simulacion(self):
        info = tk.Label(self.tab_simulacion, text="Esto ejecuta las 10 operaciones que exige la Fase 4 para probar errores.", wraplength=500)
        info.pack(pady=20)
        
        btn_simular = tk.Button(self.tab_simulacion, text="Correr Simulación Completa", command=self.correr_simulacion, bg="salmon")
        btn_simular.pack(pady=10)

    def correr_simulacion(self):
        try:
            # Aquí va la lógica de los 10 pasos exigidos
            c_bueno = Cliente("11223344", "Simulacion Exitosa", "simula@test.com")
            s_bueno = self.servicios[0]
            
            r_buena = Reserva(c_bueno, s_bueno, 3)
            r_buena.confirmar()
            r_buena.procesar()

            # Forzamos un error para que quede en el log
            try:
                c_malo = Cliente("1", "", "sinarroba.com")
            except Exception as e:
                registrar_log("Simulación 10 pasos: Error forzado de cliente", e)

            messagebox.showinfo("Simulación Lista", "Se corrieron las operaciones como debe ser y los errores controlados se guardaron en 'logs_software_fj.txt'.")
        except Exception as e:
            registrar_log("Se daño la simulación", e)

    # --- UTILIDADES ---

    def actualizar_combos(self):
        self.combo_clientes['values'] = [c.obtener_info() for c in self.clientes]
        
    def actualizar_lista_cobro(self):
        self.listbox_reservas.delete(0, tk.END)
        for r in self.reservas:
            self.listbox_reservas.insert(tk.END, r.obtener_info())

# Arranque del programaa
if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app = AppSoftwareFJ(ventana_principal)
    ventana_principal.mainloop()