import asyncio
import os
import tempfile
import streamlit as st
import edge_tts

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Gerador de Áudio Pro - Vozes Neurais",
    page_icon="🎙️",
    layout="centered"
)

# 10 Vozes neurais estáveis do código original
voice_profiles = {
    # === VOZES MASCULINAS (5) ===
    "Homem 1 - Antônio (Brasil - Versátil)": "pt-BR-AntonioNeural",
    "Homem 2 - Nicolau (Brasil - Jovem)": "pt-BR-NicolauNeural",
    "Homem 3 - Duarte (Portugal - Formal / Grave)": "pt-PT-DuarteNeural",
    "Homem 4 - Humberto (Angola - Cadenciado)": "pt-AO-HumbertoNeural",
    "Homem 5 - Fernando (Guiné-Bissau - Firme)": "pt-GW-FernandoNeural",
    
    # === VOZES FEMININAS (5) ===
    "Mulher 1 - Francisca (Brasil - Natural)": "pt-BR-FranciscaNeural",
    "Mulher 2 - Thalita (Brasil - Suave)": "pt-BR-ThalitaNeural",
    "Mulher 3 - Brenda (Brasil - Expressiva)": "pt-BR-BrendaNeural",
    "Mulher 4 - Raquel (Portugal - Clara)": "pt-PT-RaquelNeural",
    "Mulher 5 - Yara (Angola - Cadenciada)": "pt-AO-YaraNeural",
}

# Função assíncrona para gerar o áudio com edge-tts
async def generate_audio(text, voice_id, rate_str, output_file):
    if rate_str:
        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
    else:
        communicate = edge_tts.Communicate(text, voice_id)
    await communicate.save(output_file)

# Interface Gráfica com Streamlit
st.title("🎙️ Sintetizador de Voz Neural Humana")
st.write("Converta textos em áudio de alta qualidade utilizando vozes neurais.")

# Entrada de Texto
text_input = st.text_area(
    "Digite o texto que deseja converter em áudio:",
    value="Olá Bruno, bom dia! Como você está?",
    height=150
)

# Painel de Configurações em duas colunas
col1, col2 = st.columns(2)

with col1:
    selected_profile = st.selectbox(
        "Seleção de Voz Neural:", 
        list(voice_profiles.keys())
    )
    voice_id = voice_profiles[selected_profile]

with col2:
    slider_val = st.slider(
        "Velocidade da Fala (%)", 
        min_value=-30, 
        max_value=30, 
        value=0, 
        step=1
    )
    
    if slider_val > 0:
        rate_str = f"+{slider_val}%"
    elif slider_val < 0:
        rate_str = f"{slider_val}%"
    else:
        rate_str = None

# Espaçamento
st.write("")

# Botão para Gerar o Áudio
if st.button("▶ Gerar e Ouvir Áudio", type="primary", use_container_width=True):
    if not text_input or len(text_input.strip()) < 2:
        st.warning("Digite uma frase com mais de 2 letras para gerar o áudio.")
    else:
        with st.spinner("Sintetizando voz humana..."):
            # Cria um arquivo temporário para salvar o MP3
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            temp_path = temp_file.name
            temp_file.close()

            try:
                # Executa a geração assíncrona
                asyncio.run(generate_audio(text_input, voice_id, rate_str, temp_path))
                
                st.success("Áudio gerado com sucesso!")
                
                # Player de áudio integrado do Streamlit
                st.audio(temp_path, format="audio/mp3")

                # Botão para baixar o arquivo gerado
                with open(temp_path, "rb") as f:
                    audio_bytes = f.read()

                st.download_button(
                    label="💾 Baixar Arquivo MP3",
                    data=audio_bytes,
                    file_name="audio_neural.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )

            except Exception as e:
                st.error(f"Erro ao sintetizar áudio: {e}")
