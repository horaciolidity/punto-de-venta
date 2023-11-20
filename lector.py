import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import keyboard
import sys
import threading
from ttkthemes import ThemedStyle  # Agrega esta línea


sys.stderr = open("error_log.txt", "w")


class SistemaPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("Almacen Olascoaga - Sistema de Punto de Venta")
        self.root.geometry("1200x500")  # Tamaño de la ventana

        self.lock = threading.Lock()

        # Base de datos SQLite
        self.conn = sqlite3.connect("productos.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT,
                precio REAL,
                cantidad INTEGER,
                ultima_edicion TEXT,
                novedades TEXT
            )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT,
                cantidad INTEGER,
                fecha TEXT
            )
        ''')

        self.c.execute('''
            CREATE TABLE IF NOT EXISTS ventas_realizadas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                total REAL,
                fecha TEXT
            )
        ''')

        self.conn.commit()

        # Variables
        self.codigo_var = tk.StringVar()
        self.nombre_var = tk.StringVar()
        self.precio_var = tk.DoubleVar()
        self.cantidad_var = tk.IntVar()
        self.importe_var = tk.DoubleVar()

        # Lista de productos y total de la venta
        self.productos_seleccionados = []
        self.total_venta_var = tk.DoubleVar()

       
        # Interfaz
        self.create_gui()

        # Cargar productos existentes en la lista al inicio
        self.cargar_lista_productos()

    def create_gui(self):
        self.root.configure(bg='#421D97')  # Color de fondo

        # Utiliza ttkthemes para mejorar la apariencia
        self.style = ThemedStyle(self.root)
        self.style.set_theme("clam")

        # Crear un frame para el título
        titulo_frame = tk.Frame(self.root, bg='#421D97')
        titulo_frame.grid(row=0, column=0, columnspan=3, sticky="n")

        # Configurar la fuente y el tamaño para el título
        title_font = ('Arial', 24)

        # Etiqueta para el título
        tk.Label(titulo_frame, text="Almacen Jose", font=title_font, bg='#421D97', fg='white').grid(row=0, column=0, pady=20)

        # Crear un frame principal para contener los dos cards
        main_card_frame = tk.Frame(self.root, bg='#421D97', bd=2, relief=tk.GROOVE, borderwidth=2, padx=10, pady=10)
        main_card_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="n")
        
       



        # Crear un frame para la tarjeta de productos
        self.card_frame = tk.Frame(main_card_frame, bd=2, relief=tk.GROOVE, borderwidth=2, padx=10, pady=10, bg="white")
        self.card_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # Crear un marco principal dentro de la tarjeta
        main_frame = ttk.Frame(self.card_frame, padding=(20, 10))
        main_frame.grid(row=0, column=0, rowspan=5, padx=(5, 0), pady=(10, 10), sticky="n")

        # Etiquetas
        label_font = ('Arial', 12)
        label_bg = '#B3ADB9'
        label_fg = '#2F0550'
        row_padding = 5
        sticky_alignment = "w"

        self.inventario_label = tk.Label(main_frame, text="", font=label_font, bg=label_bg, fg=label_fg)
        self.inventario_label.grid(row=5, column=0, pady=row_padding, sticky=sticky_alignment)

        tk.Label(main_frame, text="Código de Barras:", font=label_font, bg=label_bg, fg=label_fg).grid(row=0, column=0, pady=row_padding, sticky=sticky_alignment)
        tk.Label(main_frame, text="Nombre del Producto:", font=label_font, bg=label_bg, fg=label_fg).grid(row=1, column=0, pady=row_padding, sticky=sticky_alignment)
        tk.Label(main_frame, text="Precio:", font=label_font, bg=label_bg, fg=label_fg).grid(row=2, column=0, pady=row_padding, sticky=sticky_alignment)
        tk.Label(main_frame, text="Cantidad:", font=label_font, bg=label_bg, fg=label_fg).grid(row=3, column=0, pady=row_padding, sticky=sticky_alignment)
        tk.Label(main_frame, text="Importe:", font=label_font, bg=label_bg, fg=label_fg).grid(row=4, column=0, pady=row_padding, sticky=sticky_alignment)

        # Entradas
        entry_padding = 5
        tk.Entry(main_frame, textvariable=self.codigo_var).grid(row=0, column=1, pady=entry_padding, padx=(0, 20), sticky=sticky_alignment)
        tk.Entry(main_frame, textvariable=self.nombre_var).grid(row=1, column=1, pady=entry_padding, padx=(0, 20), sticky=sticky_alignment)
        tk.Entry(main_frame, textvariable=self.precio_var).grid(row=2, column=1, pady=entry_padding, padx=(0, 20), sticky=sticky_alignment)
        tk.Entry(main_frame, textvariable=self.cantidad_var).grid(row=3, column=1, pady=entry_padding, padx=(0, 20), sticky=sticky_alignment)
        tk.Entry(main_frame, textvariable=self.importe_var, state="readonly").grid(row=4, column=1, pady=entry_padding, padx=(0, 20), sticky=sticky_alignment)

         # Lista de productos y productos seleccionados
        tk.Label(self.card_frame, text="Lista de Productos", font=('Arial', 14)).grid(row=0, column=1, pady=(0, 10))
        tk.Label(self.card_frame, text="Productos Seleccionados:", font=('Arial', 12)).grid(row=0, column=2, padx=5, pady=(10, 5), sticky="w")
        
        # Agregar Scrollbar a la lista de productos
        scrollbar_productos = tk.Scrollbar(self.card_frame, orient="vertical")
        self.productos_listbox = tk.Listbox(self.card_frame, selectmode=tk.SINGLE, height=12, width=30, yscrollcommand=scrollbar_productos.set)
        scrollbar_productos.config(command=self.productos_listbox.yview)

        self.productos_listbox.grid(row=1, column=1, padx=5, pady=5, sticky="n")
        scrollbar_productos.grid(row=1, column=2, pady=5, sticky="ns")


        # Agregar Scrollbar a la lista de productos seleccionados
        scrollbar_seleccionados = tk.Scrollbar(self.card_frame, orient="vertical")
        self.productos_seleccionados_listbox = tk.Listbox(self.card_frame, selectmode=tk.MULTIPLE, height=12, width=30, yscrollcommand=scrollbar_seleccionados.set)
        scrollbar_seleccionados.config(command=self.productos_seleccionados_listbox.yview)

        self.productos_seleccionados_listbox.grid(row=1, column=3, padx=1, pady=(1, 1), sticky="w")
        scrollbar_seleccionados.grid(row=1, column=4, pady=(1, 1), sticky="ns")
         # Crear el estilo para los botones
        button_style = ttk.Style()
        button_style.configure("Green.TButton", foreground="black", background="#2F9CBF", font=('Arial', 12))

        # Distribuir y organizar los botones de manera compacta
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=13, column=0, columnspan=2, pady=(10, 5), sticky="w") 
        button_style.configure("Red.TButton", foreground="black", background="red", font=('Arial', 12))


        ttk.Button(button_frame, text="Eliminar Historial", command=self.eliminar_historial, style="Green.TButton").grid(row=0, column=6, pady=(0, 5), padx=(0, 5))
        ttk.Button(button_frame, text="Cargar/Editar", command=self.cargar_editar_producto, style="Green.TButton").grid(row=0, column=0, pady=(0, 5), padx=(0, 5))
        ttk.Button(button_frame, text="Eliminar", command=self.eliminar_producto, style="Green.TButton").grid(row=0, column=1, pady=(0, 5), padx=(0, 5))    
        ttk.Button(button_frame, text="Vender", command=self.realizar_venta, style="Red.TButton").grid(row=0, column=2, pady=(0, 5), padx=(0, 5))
        ttk.Button(button_frame, text="Cerrar Venta", command=self.cerrar_venta, style="Green.TButton").grid(row=0, column=3, pady=(0, 5), padx=(0, 5))
        ttk.Button(button_frame, text="Imprimir Ticket", command=lambda: self.imprimir_ticket(self.productos_seleccionados, self.total_venta_var.get()), style="Green.TButton").grid(row=0, column=4, pady=(0, 5), padx=(0, 5))
        ttk.Button(button_frame, text="Ver Ventas Realizadas", command=self.mostrar_ventas_realizadas, style="Green.TButton").grid(row=0, column=5, pady=(0, 5))


        # Crear un frame para el card de la venta
        card_venta_frame = tk.Frame(main_card_frame, bd=2, relief=tk.GROOVE, borderwidth=2, padx=10, pady=10, bg="white")
        card_venta_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ne")

        # Etiqueta y campo de total de la venta dentro del card
        tk.Label(card_venta_frame, text="Total de la Venta:", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=(5, 0), sticky="w")
        venta_entry = tk.Entry(card_venta_frame, textvariable=self.total_venta_var, state="readonly", font=('Arial', 68), foreground='blue')
        venta_entry.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="w", columnspan=2)

        # Crear un frame para la tarjeta
        self.card_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE, borderwidth=2, padx=10, pady=10, bg="white")
        self.card_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="n")

        self.productos_listbox.bind("<<ListboxSelect>>", self.actualizar_campos)


        # Escuchar el evento de teclado
        keyboard.on_press_key("enter", self.cargar_editar_producto)


    def cargar_editar_producto(self, _=None):
        codigo = self.codigo_var.get()
        nombre = self.nombre_var.get()
        precio = self.precio_var.get()
        cantidad = self.cantidad_var.get()

        if codigo and nombre and precio and cantidad:
            try:
                fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Utiliza el bloque with para garantizar la gestión adecuada de la conexión y el cursor
                with self.lock:
                    producto_existente = self.c.execute("SELECT * FROM productos WHERE codigo=?", (codigo,)).fetchone()

                    if producto_existente:
                        self.c.execute("UPDATE productos SET nombre=?, precio=?, cantidad=?, ultima_edicion=?, novedades=? WHERE codigo=?",
                                       (nombre, precio, cantidad, fecha_actual, f"Editado: {fecha_actual}", codigo))
                        messagebox.showinfo("Éxito", "Producto editado exitosamente.")
                    else:
                        self.c.execute("INSERT INTO productos VALUES (?, ?, ?, ?, ?, ?)", (codigo, nombre, precio, cantidad, fecha_actual, f"Creado: {fecha_actual}"))

                    self.conn.commit()
                    self.calcular_importe()
                    self.cargar_lista_productos()  # Actualizar la lista después de cargar/editar
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El producto ya existe en la base de datos.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar/editar el producto: {str(e)}")

        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")

    
    def cerrar_conexion(self):
        self.conn.close()




    def eliminar_producto(self):
        seleccion = self.productos_listbox.curselection()
        if seleccion:
            producto_seleccionado = self.productos_listbox.get(seleccion[0])
            self.c.execute("DELETE FROM productos WHERE nombre=?", (producto_seleccionado,))
            self.conn.commit()
            self.calcular_importe()
            messagebox.showinfo("Éxito", "Producto eliminado exitosamente.")
            self.cargar_lista_productos()  # Actualizar la lista después de eliminar
        else:
            messagebox.showerror("Error", "Seleccione un producto de la lista.")

    def eliminar_historial(self):
        # Pregunta al usuario para confirmar la eliminación del historial
        confirmacion = messagebox.askyesno("Eliminar Historial", "¿Está seguro de que desea eliminar el historial de ventas realizadas?")

        if confirmacion:
            # Elimina todos los registros de la tabla ventas_realizadas
            self.c.execute("DELETE FROM ventas_realizadas")
            self.conn.commit()
            messagebox.showinfo("Historial Eliminado", "El historial de ventas realizadas ha sido eliminado correctamente.")


    def cerrar_venta(self):
     try:
        if not self.productos_seleccionados:
            # Si no hay productos seleccionados, muestra un mensaje y retorna
            messagebox.showwarning("Venta no válida", "No hay productos seleccionados para la venta.")
            return

        # Itera sobre los productos seleccionados y agrega cada venta realizada a la base de datos
        for producto in self.productos_seleccionados:
            self.c.execute("INSERT INTO ventas_realizadas (producto, cantidad, precio_unitario, total, fecha) VALUES (?, ?, ?, ?, ?)",
                           (producto[0], producto[1], producto[2], producto[3], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            self.conn.commit()

        # Limpia la lista de productos seleccionados y el total de la venta
        self.productos_seleccionados = []
        self.actualizar_lista_productos_seleccionados()
        self.total_venta_var.set(0)

        messagebox.showinfo("Venta cerrada", "La venta ha sido cerrada correctamente.")
     except Exception as e:
        # Maneja cualquier excepción que pueda ocurrir durante el proceso
        messagebox.showerror("Error", f"Error al cerrar la venta: {str(e)}")
    def editar_precio(self):
        codigo = self.codigo_var.get()
        nuevo_precio = self.precio_var.get()

        if codigo and nuevo_precio:
            self.c.execute("UPDATE productos SET precio=? WHERE codigo=?", (nuevo_precio, codigo))
            self.conn.commit()
            messagebox.showinfo("Éxito", "Precio actualizado exitosamente.")
        else:
            messagebox.showerror("Error", "Ingrese un código de barras y un nuevo precio válido.")


   

    def calcular_importe(self):
        cantidad = self.cantidad_var.get()
        precio = self.precio_var.get()
        importe = cantidad * precio
        self.importe_var.set(importe)

    def cargar_lista_productos(self):
        # Limpiar la lista antes de cargarla nuevamente
        self.productos_listbox.delete(0, tk.END)

        # Obtener todos los productos de la base de datos
        productos = self.c.execute("SELECT nombre FROM productos").fetchall()

        # Agregar productos a la lista
        for producto in productos:
            self.productos_listbox.insert(tk.END, producto[0])

    def actualizar_campos(self, event):
        seleccion = self.productos_listbox.curselection()
        if seleccion:
            producto_seleccionado = self.productos_listbox.get(seleccion[0])
            # Obtener datos del producto seleccionado
            datos_producto = self.c.execute("SELECT codigo, nombre, precio, cantidad FROM productos WHERE nombre=?", (producto_seleccionado,)).fetchone()
            # Actualizar campos con los datos del producto
            self.codigo_var.set(datos_producto[0])
            self.nombre_var.set(datos_producto[1])
            self.precio_var.set(datos_producto[2])
            self.cantidad_var.set(datos_producto[3])
            self.calcular_importe()
            # Mostrar la cantidad del producto seleccionado
            self.inventario_label.config(text=f"Inventario Actual: {datos_producto[3]}")



    def realizar_venta(self):
        codigo = self.codigo_var.get()
        nombre = self.nombre_var.get()
        cantidad_vendida = self.cantidad_var.get()

        if codigo and nombre and cantidad_vendida:
            try:
                # Obtener el inventario actual del producto
                inventario_producto = self.c.execute("SELECT cantidad, precio FROM productos WHERE nombre=?", (nombre,)).fetchone()
                inventario_actual, precio_unitario = inventario_producto if inventario_producto else (0, 0)

                # Verificar si hay suficiente inventario para la venta
                if inventario_actual >= cantidad_vendida:
                    # Actualizar el inventario después de la venta
                    nuevo_inventario = inventario_actual - cantidad_vendida
                    self.c.execute("UPDATE productos SET cantidad=? WHERE nombre=?", (nuevo_inventario, nombre))

                    # Agregar el producto a la lista de productos seleccionados
                    total_venta_producto = cantidad_vendida * precio_unitario
                    self.productos_seleccionados.append((nombre, cantidad_vendida, precio_unitario, total_venta_producto))
                    self.actualizar_lista_productos_seleccionados()

                    # Calcular el total de la venta
                    total_venta = sum(item[3] for item in self.productos_seleccionados)
                    self.total_venta_var.set(total_venta)

                    # Agrega estas líneas para imprimir valores de depuración
                    print(f"Inventario actual después de la venta: {nuevo_inventario}")
                    print(f"Productos seleccionados: {self.productos_seleccionados}")
                    print(f"Total de la Venta: {self.total_venta_var.get()}")

                    messagebox.showinfo("Éxito", f"Venta realizada: {cantidad_vendida} {nombre}. Inventario actual: {nuevo_inventario}")
                    self.cargar_lista_productos()  # Actualizar la lista después de la venta
                else:
                    messagebox.showerror("Error", f"No hay suficiente inventario para vender {cantidad_vendida} {nombre}.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al realizar la venta: {str(e)}")
        else:
            messagebox.showerror("Error", "Seleccione un producto de la lista y especifique la cantidad a vender.")

    def actualizar_lista_productos_seleccionados(self):
        # Limpiar la lista antes de cargarla nuevamente
        self.productos_seleccionados_listbox.delete(0, tk.END)

        # Agregar productos seleccionados a la lista
        for producto in self.productos_seleccionados:
            self.productos_seleccionados_listbox.insert(tk.END, f"{producto[0]} - Cantidad: {producto[1]}, Precio Unitario: ${producto[2]}, Total: ${producto[3]}")

    def mostrar_ventas_realizadas(self):
        # Obtener todos los productos vendidos de la base de datos
        ventas = self.c.execute("SELECT producto, cantidad, precio_unitario, total, fecha FROM ventas_realizadas").fetchall()

        # Mostrar las ventas realizadas en una nueva ventana
        ventana_ventas = tk.Toplevel(self.root)
        ventana_ventas.title("Ventas Realizadas")

        # Crear una etiqueta para mostrar las ventas
        tk.Label(ventana_ventas, text="Productos Vendidos").pack()

        for venta in ventas:
            tk.Label(ventana_ventas, text=f"{venta[0]} - Cantidad: {venta[1]}, Precio Unitario: ${venta[2]}, Total: ${venta[3]}, Fecha: {venta[4]}").pack()

        # Calcular el total del valor de todas las ventas
        total_valor = sum(venta[3] for venta in ventas)
        tk.Label(ventana_ventas, text=f"Total del Valor: ${total_valor}").pack()

        # Agregar un botón para imprimir el ticket
        tk.Button(ventana_ventas, text="Imprimir Ticket", command=lambda: self.imprimir_ticket(ventas, total_valor)).pack()

    def imprimir_ticket(self, ventas, total_valor):
        # Implementa la lógica para imprimir el ticket aquí
        # Puedes utilizar una biblioteca externa para imprimir, como reportlab o una impresora térmica si estás utilizando una.

        # Ejemplo: Imprimir en la consola por ahora
        print("---- Ticket de Venta ----")
        for venta in ventas:
            print(f"{venta[0]} - Cantidad: {venta[1]}, Precio Unitario: ${venta[2]}, Total: ${venta[3]}, Fecha: {venta[4]}")
        print("-------------------------")
        print(f"Total valor antes de imprimir: ${total_valor}")

        print(f"Total del Valor: ${total_valor}")

if __name__ == "__main__":
    root = tk.Tk()
    sistema_pos = SistemaPOS(root)
    root.mainloop()
