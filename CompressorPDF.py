import io
import streamlit as st
import pymupdf

st.set_page_config(page_title="Compresor de PDF", page_icon="📄", layout="centered")

st.title("📄 Compresor de PDF Profesional")
st.write("Sube uno o varios archivos PDF, selecciona el nivel de compresión y descárgalos optimizados.")

# Permitir múltiples archivos
uploaded_files = st.file_uploader("Elige uno o más archivos PDF", type="pdf", accept_multiple_files=True)

# Selector de nivel de compresión con las etiquetas solicitadas
nivel = st.selectbox(
    "Nivel de Compresión",
    options=["bajo", "medio", "maximo"],
    format_func=lambda x: {
        "bajo": "Bajo (Mejor Calidad Visual / Minima Reducción del Peso)", 
        "medio": "Medio (Recomendado / Peso Equilibrado)", 
        "maximo": "Maximo (Menor Calidad Visual / Menor Peso)"
    }[x],
    index=1
)

if uploaded_files:
    if st.button("Comprimir Archivos", type="primary"):
        configuraciones = {
            "bajo": {"dpi": 150, "quality": 80},
            "medio": {"dpi": 120, "quality": 60},
            "maximo": {"dpi": 90, "quality": 30}
        }
        params = configuraciones[nivel]
        
        st.write("---")
        st.subheader("Archivos listos para descargar:")
        
        for uploaded_file in uploaded_files:
            with st.spinner(f"Procesando {uploaded_file.name}..."):
                bytes_data = uploaded_file.read()
                
                doc_orig = pymupdf.open(stream=bytes_data, filetype="pdf")
                doc_nuevo = pymupdf.open()
                
                for pagina in doc_orig:
                    pix = pagina.get_pixmap(dpi=params["dpi"])
                    img_bytes = pix.tobytes("jpeg", jpg_quality=params["quality"])
                    
                    nueva_pagina = doc_nuevo.new_page(width=pagina.rect.width, height=pagina.rect.height)
                    nueva_pagina.insert_image(nueva_pagina.rect, stream=img_bytes)
                    
                output_bytes = doc_nuevo.tobytes()
                doc_orig.close()
                doc_nuevo.close()
                
                st.download_button(
                    label=f"📥 Descargar {uploaded_file.name}",
                    data=output_bytes,
                    file_name=f"optimizado_{uploaded_file.name}",
                    mime="application/pdf",
                    key=uploaded_file.name
                )
