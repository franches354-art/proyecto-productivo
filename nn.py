import sqlite3
import csv
import os
from tkinter import *
from tkinter import ttk, messagebox

# ================= BASE DE DATOS =================
def inicializar_bd():
    conn = sqlite3.connect("sistema.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS personas 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    nombre TEXT, apellido TEXT, dni TEXT, pais TEXT)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios_login 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    usuario TEXT UNIQUE, password TEXT)""")
    
    try:
        cur.execute("INSERT INTO usuarios_login (usuario, password) VALUES (?, ?)", ("crimeidy", "mantequilla"))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    conn.close()

# ================= VENTANA PRINCIPAL (CRUD) =================
class RegistroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión - Acceso Autorizado")
        self.root.geometry("850x600")

        # Variables
        self.id_db = StringVar()
        self.nombre = StringVar()
        self.apellido = StringVar()
        self.dni_id = StringVar()
        self.pais = StringVar()

        # --- Interfaz ---
        Label(root, text="REGISTRO DE PERSONAL", font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=10)
        
        frame_campos = LabelFrame(root, text=" Datos del Personal ", padx=20, pady=10)
        frame_campos.pack(fill="x", padx=20)

        Label(frame_campos, text="Nombre:").grid(row=0, column=0, sticky=W)
        Entry(frame_campos, textvariable=self.nombre).grid(row=0, column=1, padx=5, pady=5)

        Label(frame_campos, text="Apellido:").grid(row=0, column=2, sticky=W)
        Entry(frame_campos, textvariable=self.apellido).grid(row=0, column=3, padx=5, pady=5)

        Label(frame_campos, text="ID/DNI:").grid(row=1, column=0, sticky=W)
        Entry(frame_campos, textvariable=self.dni_id).grid(row=1, column=1, padx=5, pady=5)

        Label(frame_campos, text="Pais:").grid(row=1, column=2, sticky=W)
        Entry(frame_campos, textvariable=self.pais).grid(row=1, column=3, padx=5, pady=5)

        # --- Botones ---
        btn_frame = Frame(root)
        btn_frame.pack(pady=10)
        
        Button(btn_frame, text="Guardar", bg="#27ae60", fg="white", width=12, command=self.guardar).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Actualizar", bg="#2980b9", fg="white", width=12, command=self.actualizar).grid(row=0, column=1, padx=5)
        Button(btn_frame, text="Eliminar", bg="#c0392b", fg="white", width=12, command=self.eliminar).grid(row=0, column=2, padx=5)
        
        # Botón Registro Excel (Separado por columnas A-E)
        Button(btn_frame, text="Registro (Excel)", bg="#8e44ad", fg="white", width=15, command=self.abrir_en_excel).grid(row=0, column=3, padx=5)
        
        # --- Tabla ---
        self.tree = ttk.Treeview(root, columns=(1,2,3,4,5), show="headings")
        for i, col in enumerate(["DB ID", "Nombre", "Apellido", "DNI", "Pais"], 1):
            self.tree.heading(i, text=col)
            self.tree.column(i, width=100)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.obtener_fila)
        
        self.cargar_datos()

    # --- FUNCIÓN EXCEL (COLUMNAS SEPARADAS A, B, C, D, E) ---
    def abrir_en_excel(self):
        try:
            conn = sqlite3.connect("sistema.db")
            cur = conn.cursor()
            # Seleccionamos en orden exacto para las columnas A, B, C, D, E
            cur.execute("SELECT id, nombre, apellido, dni, pais FROM personas")
            datos = cur.fetchall()
            conn.close()

            if not datos:
                messagebox.showwarning("Aviso", "No hay datos para exportar")
                return

            nombre_archivo = "registro_base_datos.csv"
            
            with open(nombre_archivo, 'w', newline='', encoding='utf-8-sig') as f:
                # El comando 'sep=;' fuerza a Excel a separar las columnas inmediatamente
                f.write("sep=;\n")
                escritor = csv.writer(f, delimiter=';')
                # Fila de encabezados
                escritor.writerow(['ID', 'Nombre', 'Apellido', 'DNI', 'Pais'])
                # Filas de datos
                escritor.writerows(datos)

            # Abrir archivo automáticamente
            os.startfile(nombre_archivo) 
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el registro: {e}")

    def cargar_datos(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        conn = sqlite3.connect("sistema.db")
        for fila in conn.execute("SELECT * FROM personas"): self.tree.insert("", END, values=fila)
        conn.close()

    def guardar(self):
        if self.nombre.get() == "" or self.dni_id.get() == "":
            messagebox.showwarning("Atención", "Rellene Nombre y DNI")
            return
        conn = sqlite3.connect("sistema.db")
        conn.execute("INSERT INTO personas VALUES (NULL,?,?,?,?)", 
                     (self.nombre.get(), self.apellido.get(), self.dni_id.get(), self.pais.get()))
        conn.commit()
        conn.close()
        self.cargar_datos()
        self.limpiar_campos()

    def obtener_fila(self, event):
        item = self.tree.focus()
        if item:
            fila = self.tree.item(item)['values']
            self.id_db.set(fila[0]); self.nombre.set(fila[1])
            self.apellido.set(fila[2]); self.dni_id.set(fila[3]); self.pais.set(fila[4])

    def actualizar(self):
        if not self.id_db.get(): return
        conn = sqlite3.connect("sistema.db")
        conn.execute("UPDATE personas SET nombre=?, apellido=?, dni=?, pais=? WHERE id=?",
                    (self.nombre.get(), self.apellido.get(), self.dni_id.get(), self.pais.get(), self.id_db.get()))
        conn.commit()
        conn.close()
        self.cargar_datos()

    def eliminar(self):
        if not self.id_db.get(): return
        conn = sqlite3.connect("sistema.db")
        conn.execute("DELETE FROM personas WHERE id=?", (self.id_db.get(),))
        conn.commit()
        conn.close()
        self.cargar_datos()
        self.limpiar_campos()

    def limpiar_campos(self):
        self.id_db.set(""); self.nombre.set(""); self.apellido.set(""); self.dni_id.set(""); self.pais.set("")

# ================= VENTANA DE LOGIN =================
class LoginVentana:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x250")
        
        Label(root, text="Iniciar Sesión", font=("Arial", 14, "bold")).pack(pady=20)
        Label(root, text="Usuario:").pack()
        self.user_entry = Entry(root)
        self.user_entry.pack(pady=5)
        Label(root, text="Contraseña:").pack()
        self.pass_entry = Entry(root, show="*")
        self.pass_entry.pack(pady=5)
        Button(root, text="Entrar", command=self.validar, bg="#34495e", fg="white", width=15).pack(pady=20)

    def validar(self):
        usuario = self.user_entry.get()
        password = self.pass_entry.get()

        conn = sqlite3.connect("sistema.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM usuarios_login WHERE usuario=? AND password=?", (usuario, password))
        resultado = cur.fetchone()
        conn.close()

        if resultado:
            self.root.destroy()
            main_root = Tk()
            # Importante: Inicializar la clase después de crear el nuevo root
            RegistroApp(main_root)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Datos incorrectos")

# ================= INICIO =================
if __name__ == "__main__":
    inicializar_bd()
    root_login = Tk()
    app = LoginVentana(root_login)
    root_login.mainloop()
