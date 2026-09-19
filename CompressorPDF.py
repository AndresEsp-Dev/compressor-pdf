import io
import zipfile
import streamlit as st
import pymupdf

# Configuración de la página en modo ancho para responsividad total
st.set_page_config(
    page_title="Suite PDF | AppLogic Solutions", 
    page_icon="⚡", 
    layout="wide"
)

# Estilos CSS avanzados para centrar elementos, mejorar responsividad y dar un aspecto corporativo
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    .main-wrapper {
        max-width: 950px;
        margin: 0 auto;
        padding: 0 20px;
    }
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px 30px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    }
    .hero-container h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        color: #ffffff;
    }
    .hero-container p {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 0;
    }
    .company-badge {
        display: inline-block;
        background: #38bdf8;
        color: #0f172a;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .privacy-notice {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        padding: 12px 18px;
        border-radius: 6px;
        color: #cbd5e1;
        font-size: 0.95rem;
        margin-bottom: 25px;
        text-align: center;
    }
    .warning-notice {
        background-color: #451a03;
        border-left: 4px solid #f59e0b;
        padding: 12px 18px;
        border-radius: 6px;
        color: #fde68a;
        font-size: 0.95rem;
        margin-bottom: 20px;
        text-align: center;
    }
    .footer {
        text-align: center;
        margin-top: 50px;
        color: #64748b;
        font-size: 0.9rem;
        border-top: 1px solid #1e293b;
        padding-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # Banner Fijo y Centrado de AppLogic Solutions
    st.markdown("""
        <div class="hero-container">
            <div class="company-badge">AppLogic Solutions</div>
            <h1>Suite Inteligente de Documentos PDF</h1>
            <p>Comprime, une y divide tus archivos de forma profesional y segura.</p>
        </div>
    """, unsafe_allow_html=True)

    # Nota de Privacidad Global
    st.markdown("""
        <div class="privacy-notice">
            🔒 <b>Política de Privacidad y Confidencialidad:</b> Tus archivos no se almacenan en ningún servidor ni base de datos externa. Todo el procesamiento se realiza de forma temporal y privada en memoria RAM exclusivamente para tu tranquilidad.
        </div>
    """, unsafe_allow_html=True)

    # Pestañas principales de herramientas
    tab_comprimir, tab_unir, tab_dividir = st.tabs(["🗜️ Comprimir PDF", "📎 Unir PDFs", "✂️ Dividir PDF"])

    # ==========================================
    # PESTAÑA 1: COMPRIMIR PDF
    # ==========================================
    with tab_comprimir:
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = {}
        if "file_stats" not in st.session_state:
            st.session_state.file_stats = {}
        if "uploader_counter" not in st.session_state:
            st.session_state.uploader_counter = 0

        uploader_key = f"uploader_{st.session_state.uploader_counter}"

        uploaded_files = st.file_uploader(
            "📂 Selecciona o arrastra tus archivos PDF a comprimir", 
            type="pdf", 
            accept_multiple_files=True,
            key=uploader_key
        )

        nivel_opcion = st.selectbox(
            "⚙️ Selecciona el Nivel de Compresión",
            options=["bajo", "medio", "maximo"],
            format_func=lambda x: {
                "bajo": "Bajo — Mejor Calidad Visual (Mínima reducción de peso)", 
                "medio": "Medio — Recomendado (Equilibrio ideal entre peso y calidad)", 
                "maximo": "Máximo — Máxima Compresión (Menor peso posible para archivos pesados)"
            }[x],
            index=1,
            key="comp_nivel"
        )

        st.write("")

        if uploaded_files:
            if st.button("🚀 Iniciar Compresión de Archivos", type="primary", use_container_width=True, key="btn_comprimir"):
                configuraciones = {
                    "bajo": {"dpi": 150, "quality": 80},
                    "medio": {"dpi": 120, "quality": 60},
                    "maximo": {"dpi": 90, "quality": 30}
                }
                params = configuraciones[nivel_opcion]
                
                st.session_state.processed_files = {}
                st.session_state.file_stats = {}
                
                progress_bar = st.progress(0)
                total_files = len(uploaded_files)
                
                for i, uploaded_file in enumerate(uploaded_files):
                    with st.spinner(f"Procesando: {uploaded_file.name}..."):
                        bytes_data = uploaded_file.read()
                        size_orig = len(bytes_data) / 1024
                        
                        doc_orig = pymupdf.open(stream=bytes_data, filetype="pdf")
                        doc_nuevo = pymupdf.open()
                        
                        for pagina in doc_orig:
                            pix = pagina.get_pixmap(dpi=params["dpi"])
                            img_bytes = pix.tobytes("jpeg", jpg_quality=params["quality"])
                            
                            nueva_pagina = doc_nuevo.new_page(width=pagina.rect.width, height=pagina.rect.height)
                            nueva_pagina.insert_image(nueva_pagina.rect, stream=img_bytes)
                            
                        output_bytes = doc_nuevo.tobytes()
                        size_comp = len(output_bytes) / 1024
                        
                        doc_orig.close()
                        doc_nuevo.close()
                        
                        nombre_salida = f"Optimizado-{nivel_opcion}-{uploaded_file.name}"
                        st.session_state.processed_files[nombre_salida] = output_bytes
                        
                        ahorro = 100 - (size_comp / size_orig * 100) if size_orig > 0 else 0
                        st.session_state.file_stats[nombre_salida] = {
                            "orig": f"{size_orig / 1024:.2f} MB" if size_orig > 1024 else f"{size_orig:.2f} KB",
                            "comp": f"{size_comp / 1024:.2f} MB" if size_comp > 1024 else f"{size_comp:.2f} KB",
                            "ahorro": f"{ahorro:.1f}%"
                        }
                        
                        progress_bar.progress((i + 1) / total_files)
                        
                st.success("¡Todos los archivos han sido optimizados con éxito!")

        if st.session_state.processed_files:
            st.markdown("---")
            col_title, col_action = st.columns()
            with col_title:
                st.subheader("📦 Resultados Listos para Descargar")
                
            with col_action:
                col_zip_btn, col_clean_btn = st.columns()
                with col_zip_btn:
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        for filename, data in st.session_state.processed_files.items():
                            zip_file.writestr(filename, data)
                    zip_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Descargar ZIP",
                        data=zip_buffer,
                        file_name="pdfs_optimizados_applogic.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True,
                        key="dl_zip_comp"
                    )
                with col_clean_btn:
                    confirmar_limpieza = st.checkbox("Confirmar", key="chk_clean_comp")
                    if st.button("🧹 Limpiar", use_container_width=True, key="btn_clean_comp"):
                        if confirmar_limpieza:
                            st.session_state.processed_files = {}
                            st.session_state.file_stats = {}
                            st.session_state.uploader_counter += 1
                            st.rerun()
                        else:
                            st.warning("Marque la casilla.")

            st.markdown("""
                <div class="warning-notice">
                    ⚠️ <b>Aviso Importante:</b> Antes de cerrar o recargar esta ventana, asegúrese de descargar todos sus archivos procesados.
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📂 Ver detalles de reducción de peso y descargar archivos de forma individual", expanded=True):
                for filename, data in st.session_state.processed_files.items():
                    stats = st.session_state.file_stats.get(filename, {"orig": "N/A", "comp": "N/A", "ahorro": "N/A"})
                    
                    col_file_info, col_file_btn = st.columns()
                    with col_file_info:
                        st.markdown(f"""
                            <div style="background: #1e293b; padding: 12px 15px; border-radius: 8px; border: 1px solid #334155;">
                                <b>📄 {filename}</b><br>
                                <span style="color: #94a3b8; font-size: 0.85rem;">
                                    Original: <b>{stats['orig']}</b> | 
                                    Optimizado: <b style="color: #38bdf8;">{stats['comp']}</b> | 
                                    Ahorro: <b style="color: #4ade80;">{stats['ahorro']}</b>
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                    with col_file_btn:
                        st.write("")
                        st.download_button(
                            label="⬇️ Descargar",
                            data=data,
                            file_name=filename,
                            mime="application/pdf",
                            key=f"dl_{filename}",
                            use_container_width=True
                        )
                    st.write("")

    # ==========================================
    # PESTAÑA 2: UNIR PDFS
    # ==========================================
    with tab_unir:
        st.subheader("📎 Unir Varios PDFs en uno solo")
        archivos_unir = st.file_uploader(
            "Selecciona los archivos PDF en el orden que deseas unirlos", 
            type="pdf", 
            accept_multiple_files=True, 
            key="unir_uploader"
        )
        nombre_salida_unido = st.text_input("Nombre del archivo final", value="Documento_Unido_AppLogic.pdf", key="nombre_unido")

        if archivos_unir and len(archivos_unir) > 1:
            if st.button("🔗 Unir PDFs Ahora", type="primary", use_container_width=True, key="btn_unir"):
                with st.spinner("Uniendo documentos..."):
                    doc_final = pymupdf.open()
                    for f in archivos_unir:
                        doc_temp = pymupdf.open(stream=f.read(), filetype="pdf")
                        doc_final.insert_pdf(doc_temp)
                        doc_temp.close()
                    
                    unido_bytes = doc_final.tobytes()
                    doc_final.close()
                    
                    st.success("¡Documentos unidos con éxito!")
                    st.markdown("""
                        <div class="warning-notice">
                            ⚠️ <b>Aviso Importante:</b> Antes de cerrar o recargar esta ventana, por favor descargue el archivo unificado.
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Descargar PDF Unido",
                        data=unido_bytes,
                        file_name=nombre_salida_unido if nombre_salida_unido.endswith(".pdf") else f"{nombre_salida_unido}.pdf",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="dl_unido"
                    )
        elif archivos_unir and len(archivos_unir) == 1:
            st.info("ℹ️ Por favor selecciona al menos 2 archivos PDF para realizar la unión.")

    # ==========================================
    # PESTAÑA 3: DIVIDIR PDF
    # ==========================================
    with tab_dividir:
        st.subheader("✂️ Dividir / Extraer Rango de Páginas de un PDF")
        archivo_dividir = st.file_uploader(
            "Sube el archivo PDF que deseas dividir", 
            type="pdf", 
            accept_multiple_files=False, 
            key="dividir_uploader"
        )

        if archivo_dividir:
            doc_div = pymupdf.open(stream=archivo_dividir.read(), filetype="pdf")
            total_paginas = len(doc_div)
            st.info(f"📄 El documento cargado tiene un total de **{total_paginas} página(s)**.")

            col_p1, col_p2 = st.columns(2)
            with col_p1:
                pag_inicio = st.number_input("Página inicial (desde 1)", min_value=1, max_value=total_paginas, value=1, key="div_inicio")
            with col_p2:
                pag_fin = st.number_input("Página final (hasta)", min_value=1, max_value=total_paginas, value=min(2, total_paginas), key="div_fin")

            doc_div.close()

            if pag_inicio <= pag_fin:
                if st.button("✂️ Dividir y Extraer Rango", type="primary", use_container_width=True, key="btn_dividir"):
                    # Reabrir para procesamiento fresco
                    archivo_dividir.seek(0)
                    doc_src = pymupdf.open(stream=archivo_dividir.read(), filetype="pdf")
                    doc_part = pymupdf.open()
                    
                    # Convertir a índice base 0
                    doc_part.insert_pdf(doc_src, from_page=pag_inicio-1, to_page=pag_fin-1)
                    part_bytes = doc_part.tobytes()
                    doc_src.close()
                    doc_part.close()

                    st.success(f"¡Páginas {pag_inicio} a {pag_fin} extraídas con éxito!")
                    st.markdown("""
                        <div class="warning-notice">
                            ⚠️ <b>Aviso Importante:</b> Antes de cerrar o recargar esta ventana, por favor descargue el archivo dividido.
                        </div>
                    """, unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Descargar Páginas Extraídas (PDF)",
                        data=part_bytes,
                        file_name=f"Dividido_pag_{pag_inicio}_a_{pag_fin}_{archivo_dividir.name}",
                        mime="application/pdf",
                        type="primary",
                        use_container_width=True,
                        key="dl_dividido"
                    )
            else:
                st.error("❌ La página inicial no puede ser mayor que la página final.")

    # Pie de página corporativo
    st.markdown("""
        <div class="footer">
            Desarrollado con pasión por <b>AppLogic Solutions</b> 🚀 | Todos los derechos reservados.
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
