import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

def agrupar_formatos(f):
    return 'LV' if f in ['LVS','LVP','LVI','LVC'] else 'TZ AC' if f in ['TAC/OR','TZ AC','TZ AC SO'] else f

def leer_datos(path):
    df = pd.read_excel(path, sheet_name='MES', usecols="A,D,H,L,N")
    df.columns = ['Fecha','Horno','Cantidad','Formato','PesoTotal']
    df = df[df.Fecha.astype(str).str.match(r'^\d{2}\.\d{2}\.\d{4}$')]
    df['Fecha'] = pd.to_datetime(df.Fecha, format='%d.%m.%Y', errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df = df[df.Horno.isin([1,2,4,5])]
    df['Formato'] = df.Formato.apply(agrupar_formatos)
    return df

def calcular_resumen(df):
    return df.groupby(['Fecha','Horno','Formato'], as_index=False).PesoTotal.sum().rename(columns={'PesoTotal':'PesoTotalReal'})

def peso_por_dia_horno(res):
    return res.groupby(['Fecha','Horno'], as_index=False).PesoTotalReal.sum()

def pareto_por_horno(resumen, pesos_prog):
    rf = resumen[resumen.Horno.isin([1,2])].copy()
    rf['PesoProgramado'] = rf.apply(lambda r: pesos_prog.get((r.Horno,r.Formato),0), axis=1)
    rf['DesviacionKg'] = rf.PesoTotalReal - rf.PesoProgramado
    out = {}
    for h, dfh in rf.groupby('Horno'):
        p = dfh.groupby('Formato').DesviacionKg.sum().abs().sort_values(ascending=False).reset_index(name='DesviacionKgAbs')
        p['DesviacionAcum'] = p.DesviacionKgAbs.cumsum()
        tot = p.DesviacionKgAbs.sum()
        p['PorcAcum'] = 100 * p.DesviacionAcum / tot if tot else 0
        out[h] = p
    return out

def guardar_excel_unificado(res, dia, cumpl, paretos, carpeta):
    f = os.path.join(carpeta, 'Reporte_Completo_Hornos.xlsx')
    with pd.ExcelWriter(f, engine='openpyxl') as w:
        res.to_excel(w, 'DetalleFormato', index=False)
        dia.to_excel(w, 'ResumenDiaHorno', index=False)
        cumpl.to_excel(w, 'CumplimientoHorno', index=False)
        if paretos:
            for h, df in paretos.items():
                df.to_excel(w, f'Pareto_Horno_{h}', index=False)
    return f

def grafica_pareto(paretos, carpeta):
    figuras_pareto = {}
    for h, df in paretos.items():
        if df.empty: continue
        plt.style.use('default')
        fig, ax1 = plt.subplots(figsize=(12, 8))
        fig.patch.set_facecolor('#f0f0f0')
        
        bars = ax1.bar(df.Formato, df.DesviacionKgAbs, color='#3498db', alpha=0.7)
        ax1.set_xlabel('Formato', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Desviación Absoluta (kg)', fontsize=12, fontweight='bold', color='#3498db')
        ax1.tick_params(axis='y', labelcolor='#3498db')
        
        ax2 = ax1.twinx()
        ax2.plot(df.Formato, df.PorcAcum, color='#e74c3c', marker='o', linewidth=3, markersize=8)
        ax2.set_ylabel('Porcentaje Acumulado (%)', fontsize=12, fontweight='bold', color='#e74c3c')
        ax2.tick_params(axis='y', labelcolor='#e74c3c')
        ax2.set_ylim(0, 105)
        ax2.axhline(y=80, color='red', linestyle='--', alpha=0.7)
        
        for i, (bar, val) in enumerate(zip(bars, df.DesviacionKgAbs)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01, f'{val:.0f}', ha='center', va='bottom', fontweight='bold')
        
        for i, (x, y) in enumerate(zip(df.Formato, df.PorcAcum)):
            ax2.text(i, y + 2, f'{y:.1f}%', ha='center', va='bottom', fontweight='bold', color='#e74c3c')
        
        plt.title(f'Diagrama de Pareto - Desviaciones Horno {h}', fontsize=16, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        path_pareto = os.path.join(carpeta, f'Pareto_Desviacion_Horno_{h}.png')
        fig.savefig(path_pareto, dpi=300, bbox_inches='tight')
        figuras_pareto[h] = fig
    return figuras_pareto

def grafica_dia(dia, kg_prog_dia, carpeta):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(12,6))
    fig.patch.set_facecolor('#f0f0f0')
    colors = ['#1f77b4', '#ff7f0e']
    for i, h in enumerate([1,2]):
        d = dia[dia.Horno==h]
        if d.empty: continue
        ax.plot(d.Fecha, d.PesoTotalReal, 'o-', label=f'H{h} Real', color=colors[i], linewidth=2.5, markersize=8)
        ax.plot(sorted(d.Fecha.unique()), [kg_prog_dia[h]]*len(d.Fecha.unique()), '--', label=f'H{h} Programado', color=colors[i], alpha=0.7, linewidth=2)
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    fig.autofmt_xdate(rotation=45)
    ax.set_title('Kg cargados vs programados por día', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Kilogramos', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(frameon=True, shadow=True, fontsize=10)
    plt.tight_layout()
    p = os.path.join(carpeta, 'Grafica_PesoVsProgramado_Dia.png')
    fig.savefig(p, dpi=300, bbox_inches='tight')
    return fig, p

def grafica_cumplimiento(df, carpeta):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,8))
    fig.patch.set_facecolor('#f0f0f0')
    x = range(len(df))
    colors = ['#3498db', '#e74c3c']
    
    bars1 = ax1.bar([i - 0.2 for i in x], df.KgProgramado, width=0.35, label='Programado (30 d)', color=colors[0], alpha=0.8)
    bars2 = ax1.bar([i + 0.2 for i in x], df.KgCargado, width=0.35, label='Cargado', color=colors[1], alpha=0.8)
    
    for i, (bar1, bar2) in enumerate(zip(bars1, bars2)):
        height1 = bar1.get_height()
        height2 = bar2.get_height()
        ax1.text(bar1.get_x() + bar1.get_width()/2., height1 + height1*0.01, f'{height1:.0f}', ha='center', va='bottom', fontweight='bold')
        ax1.text(bar2.get_x() + bar2.get_width()/2., height2 + height2*0.01, f'{height2:.0f}', ha='center', va='bottom', fontweight='bold')
    
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Horno {h}' for h in df.Horno])
    ax1.set_ylabel('Kilogramos (mes)', fontweight='bold')
    ax1.set_title('Kg totales mes por horno', fontsize=14, fontweight='bold', pad=15)
    ax1.legend(frameon=True, shadow=True)
    ax1.grid(True, alpha=0.3)
    
    bars3 = ax2.bar(x, df.PorcCumplimiento, color='#2ecc71', alpha=0.8)
    ax2.set_ylim(0, 120)
    ax2.set_ylabel('% Cumplimiento', fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'Horno {h}' for h in df.Horno])
    ax2.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.grid(True, alpha=0.3)
    
    for i, (bar, v) in enumerate(zip(bars3, df.PorcCumplimiento)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 2, f'{v:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    p = os.path.join(carpeta, 'Grafica_de_cumplimiento.png')
    fig.savefig(p, dpi=300, bbox_inches='tight')
    return fig, p

class PesosFormatoDialog(ctk.CTkToplevel):
    def __init__(self, parent, formatos):
        super().__init__(parent)
        self.formatos = formatos
        self.pesos = {}
        self.entries = {}
        self.title("Configurar Pesos por Formato")
        self.geometry("600x500")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.winfo_screenheight() // 2) - (500 // 2)
        self.geometry(f"600x500+{x}+{y}")
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        title_label = ctk.CTkLabel(main_frame, text="⚙️ Configuración de Pesos por Formato", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(20, 30))
        table_frame = ctk.CTkScrollableFrame(main_frame, height=300)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        header_frame = ctk.CTkFrame(table_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(header_frame, text="Formato", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkLabel(header_frame, text="Horno 1 (kg)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkLabel(header_frame, text="Horno 2 (kg)", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=20, pady=10)
        
        for i, f in enumerate(self.formatos):
            row_frame = ctk.CTkFrame(table_frame)
            row_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(row_frame, text=f, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=10)
            entry1 = ctk.CTkEntry(row_frame, placeholder_text="0", width=120)
            entry1.grid(row=0, column=1, padx=20, pady=10)
            entry2 = ctk.CTkEntry(row_frame, placeholder_text="0", width=120)
            entry2.grid(row=0, column=2, padx=20, pady=10)
            self.entries[(1, f)] = entry1
            self.entries[(2, f)] = entry2
        
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(button_frame, text="💾 Guardar Configuración", command=self.apply, height=40, font=ctk.CTkFont(size=14, weight="bold")).pack(side="right", padx=10)
        ctk.CTkButton(button_frame, text="❌ Cancelar", command=self.destroy, height=40, fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray80", "gray20")).pack(side="right")
    
    def apply(self):
        for (h, f), entry in self.entries.items():
            val = entry.get().strip()
            if val:
                try:
                    self.pesos[(h, f)] = float(val)
                except ValueError:
                    messagebox.showerror("Error", f"Valor inválido para Horno {h} - Formato {f}")
                    return
        self.destroy()

class ModernFurnaceApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🔥 Analizador de Hornos - Sistema Avanzado")
        self.geometry("900x700")
        self.resizable(True, True)
        self.df = None
        self.file_path = ""
        self.pesos_prog_formato = None
        self.chart_frame = None
        self.center_window()
        self.setup_ui()
        
    def center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"900x700+{x}+{y}")
        
    def setup_ui(self):
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self.setup_header(main_frame)
        self.setup_file_section(main_frame)
        self.setup_config_section(main_frame)
        self.setup_action_buttons(main_frame)
        self.chart_frame = ctk.CTkFrame(main_frame)
        self.chart_frame.pack(fill="both", expand=True, pady=20)
        self.setup_footer(main_frame)
        
    def setup_header(self, parent):
        header_frame = ctk.CTkFrame(parent, height=120)
        header_frame.pack(fill="x", pady=(0, 30))
        header_frame.pack_propagate(False)
        title_label = ctk.CTkLabel(header_frame, text="🔥 ADHERENCIA EN HORNOS TÚNEL", font=ctk.CTkFont(size=28, weight="bold"))
        title_label.pack(pady=(20, 5))
        subtitle_label = ctk.CTkLabel(header_frame, text="Análisis de producción y rendimiento", font=ctk.CTkFont(size=14), text_color="gray")
        subtitle_label.pack()
        
    def setup_file_section(self, parent):
        file_frame = ctk.CTkFrame(parent)
        file_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(file_frame, text="📁 Selección de Archivo", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 10))
        button_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 10))
        self.file_button = ctk.CTkButton(button_frame, text="📂 Seleccionar archivo Excel", command=self.open_file, height=50, width=300, font=ctk.CTkFont(size=14, weight="bold"))
        self.file_button.pack(pady=10)
        self.file_label = ctk.CTkLabel(file_frame, text="Ningún archivo seleccionado", font=ctk.CTkFont(size=12), text_color="gray")
        self.file_label.pack(pady=(0, 20))
        
    def setup_config_section(self, parent):
        config_frame = ctk.CTkFrame(parent)
        config_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(config_frame, text="⚙️ Configuración de producción", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20, 15))
        inputs_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        inputs_frame.pack(pady=(0, 15))
        input_row = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        input_row.pack()
        
        h1_frame = ctk.CTkFrame(input_row)
        h1_frame.pack(side="left", padx=20, pady=10)
        ctk.CTkLabel(h1_frame, text="🔥 Horno 1", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(h1_frame, text="Kg programados (día)").pack()
        self.kg1_entry = ctk.CTkEntry(h1_frame, placeholder_text="Ej: 1500", width=150, height=35)
        self.kg1_entry.pack(pady=(5, 15))
        
        h2_frame = ctk.CTkFrame(input_row)
        h2_frame.pack(side="right", padx=20, pady=10)
        ctk.CTkLabel(h2_frame, text="🔥 Horno 2", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(15, 5))
        ctk.CTkLabel(h2_frame, text="Kg programados (día)").pack()
        self.kg2_entry = ctk.CTkEntry(h2_frame, placeholder_text="Ej: 1200", width=150, height=35)
        self.kg2_entry.pack(pady=(5, 15))
        
        self.format_button = ctk.CTkButton(config_frame, text="🎯 Configurar pesos por formato", command=self.open_format_dialog, height=45, width=300, font=ctk.CTkFont(size=14))
        self.format_button.pack(pady=(0, 20))
        
    def setup_action_buttons(self, parent):
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(pady=20)
        self.process_button = ctk.CTkButton(action_frame, text="CALCULAR Y GENERAR REPORTES", command=self.process_data, height=60, width=400, font=ctk.CTkFont(size=16, weight="bold"))
        self.process_button.pack()
        self.progress_bar = ctk.CTkProgressBar(action_frame, width=400)
        self.progress_bar.pack(pady=(20, 0))
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(action_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
        
    def setup_footer(self, parent):
        footer_frame = ctk.CTkFrame(parent, height=80)
        footer_frame.pack(fill="x", pady=(30, 0))
        footer_frame.pack_propagate(False)
        dev_label = ctk.CTkLabel(footer_frame, text="👨‍💻 Desarrollado por Diego Barón R.", font=ctk.CTkFont(size=14, weight="bold"))
        dev_label.pack(pady=(15, 5))
        contact_label = ctk.CTkLabel(footer_frame, text="📱 WhatsApp: (312) 393-6365", font=ctk.CTkFont(size=12), text_color="gray")
        contact_label.pack()
        
    def open_file(self):
        file_path = filedialog.askopenfilename(title="Seleccionar archivo Excel", filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")])
        if file_path:
            self.file_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.configure(text=f"✅ {filename}")
            try:
                self.df = leer_datos(file_path)
                self.status_label.configure(text="✅ Archivo cargado correctamente", text_color="green")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo:\n{str(e)}")
                self.status_label.configure(text="❌ Error al cargar el archivo", text_color="red")
                
    def open_format_dialog(self):
        if self.df is None:
            messagebox.showerror("Error", "Primero debe cargar un archivo Excel")
            return
        formatos = sorted(self.df.Formato.unique())
        dialog = PesosFormatoDialog(self, formatos)
        self.wait_window(dialog)
        if hasattr(dialog, 'pesos') and dialog.pesos:
            self.pesos_prog_formato = dialog.pesos
            self.status_label.configure(text="✅ Configuración de formatos guardada", text_color="green")
            
    def process_data(self):
        if self.df is None:
            messagebox.showerror("Error", "Primero debe cargar un archivo Excel")
            return
        try:
            kg1 = float(self.kg1_entry.get())
            kg2 = float(self.kg2_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Por favor ingrese valores numéricos válidos")
            return
        self.process_button.configure(state="disabled", text="🔄 Procesando...")
        self.progress_bar.set(0)
        thread = threading.Thread(target=self.process_thread, args=(kg1, kg2))
        thread.daemon = True
        thread.start()
        
    def process_thread(self, kg1, kg2):
        try:
            self.update_status("Calculando resúmenes...", 0.2)
            kg_prog_dia = {1: kg1, 2: kg2}
            kg_prog_mes = {h: v * 30 for h, v in kg_prog_dia.items()}
            res = calcular_resumen(self.df)
            dia = peso_por_dia_horno(res)
            kg_carg_mes = dia.groupby('Horno').PesoTotalReal.sum().to_dict()
            
            self.update_status("Generando reportes...", 0.4)
            dfc = pd.DataFrame({
                'Horno': [1, 2],
                'KgProgramado': [kg_prog_mes[1], kg_prog_mes[2]],
                'KgCargado': [kg_carg_mes.get(1, 0), kg_carg_mes.get(2, 0)]
            })
            dfc['PorcCumplimiento'] = dfc.KgCargado / dfc.KgProgramado * 100
            carpeta = os.path.dirname(self.file_path)
            
            paretos = {}
            figuras_pareto = {}
            if self.pesos_prog_formato:
                self.update_status("Calculando análisis Pareto...", 0.5)
                paretos = pareto_por_horno(res, self.pesos_prog_formato)
                if paretos:
                    figuras_pareto = grafica_pareto(paretos, carpeta)
            
            self.update_status("Guardando archivo Excel unificado...", 0.7)
            excel_path = guardar_excel_unificado(res, dia, dfc, paretos, carpeta)
            
            self.update_status("Generando gráficos principales...", 0.9)
            fig1, _ = grafica_dia(dia, kg_prog_dia, carpeta)
            fig2, _ = grafica_cumplimiento(dfc, carpeta)
            
            self.update_status("Finalizando...", 1.0)
            self.after(100, lambda: self.show_results(fig1, fig2, figuras_pareto, excel_path))
            
        except Exception as e:
            self.after(100, lambda: self.show_error(str(e)))
            
    def update_status(self, message, progress):
        self.after(0, lambda: [self.status_label.configure(text=message, text_color="blue"), self.progress_bar.set(progress)])
        
    def show_results(self, fig1, fig2, figuras_pareto, excel_path):
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        title_label = ctk.CTkLabel(self.chart_frame, text="📊 Resultados del análisis", font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(20, 10))
        notebook_frame = ctk.CTkFrame(self.chart_frame)
        notebook_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=notebook_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, pady=5)
        
        canvas2 = FigureCanvasTkAgg(fig2, master=notebook_frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, pady=5)
        
        for h, fig_pareto in figuras_pareto.items():
            canvas_p = FigureCanvasTkAgg(fig_pareto, master=notebook_frame)
            canvas_p.draw()
            canvas_p.get_tk_widget().pack(fill="both", expand=True, pady=5)
        
        self.process_button.configure(state="normal", text="CALCULAR Y GENERAR REPORTES")
        self.status_label.configure(text="✅ Análisis completado exitosamente", text_color="green")
        self.progress_bar.set(1.0)
        messagebox.showinfo("Éxito", f"🎉 Análisis completado\n\nTodos los reportes se guardaron en:\n{excel_path}")
        
    def show_error(self, error_msg):
        self.process_button.configure(state="normal", text="CALCULAR Y GENERAR REPORTES")
        self.status_label.configure(text="❌ Error en el procesamiento", text_color="red")
        self.progress_bar.set(0)
        messagebox.showerror("Error", f"Error durante el procesamiento:\n{error_msg}")

if __name__ == "__main__":
    app = ModernFurnaceApp()
    app.mainloop()