import customtkinter as ctk
import edge_tts
import pygame
import asyncio
import threading
import os
import tempfile
from tkinter import filedialog

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AudioGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerador de Áudio Pro - Vozes Neurais Naturais")
        self.geometry("780x680")
        self.minsize(700, 580)

        # Configuração do Pygame Mixer
        try:
            pygame.mixer.quit()
        except:
            pass
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        
        self.temp_audio_file = os.path.join(tempfile.gettempdir(), "speech_temp.mp3")

        # Event Loop assíncrono permanente
        self.loop = asyncio.new_event_loop()
        self.loop_thread = threading.Thread(target=self._start_async_loop, daemon=True)
        self.loop_thread.start()

        # 10 Vozes neurais estáveis, ativas e testadas com ajuste de velocidade
        self.voice_profiles = {
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

        self.setup_ui()

    def _start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Cabeçalho
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        title = ctk.CTkLabel(
            header_frame, 
            text="🎙️ Sintetizador de Voz Neural Humana", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")

        # Entrada de Texto
        text_frame = ctk.CTkFrame(self)
        text_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        lbl_text = ctk.CTkLabel(text_frame, text="Digite o texto que deseja converter em áudio:", font=ctk.CTkFont(size=14))
        lbl_text.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.txt_input = ctk.CTkTextbox(text_frame, font=ctk.CTkFont(size=14), wrap="word")
        self.txt_input.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.txt_input.insert("1.0", "Olá Bruno, bom dia! Como você está?")

        # Painel de Configurações
        config_frame = ctk.CTkFrame(self)
        config_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        config_frame.grid_columnconfigure((0, 1), weight=1)

        lbl_voice = ctk.CTkLabel(config_frame, text="Seleção de Voz Neural:", font=ctk.CTkFont(size=13, weight="bold"))
        lbl_voice.grid(row=0, column=0, padx=15, pady=(10, 0), sticky="w")

        self.combo_voice = ctk.CTkOptionMenu(
            config_frame, 
            values=list(self.voice_profiles.keys())
        )
        self.combo_voice.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Rótulo de Velocidade com indicação de porcentagem
        self.lbl_speed = ctk.CTkLabel(
            config_frame, 
            text="Velocidade da Fala: 0%", 
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.lbl_speed.grid(row=0, column=1, padx=15, pady=(10, 0), sticky="w")

        # Slider para ajuste fino de velocidade
        self.slider_speed = ctk.CTkSlider(
            config_frame, 
            from_=-30, 
            to=30, 
            number_of_steps=60,
            command=self.update_speed_label
        )
        self.slider_speed.grid(row=1, column=1, padx=15, pady=(5, 15), sticky="ew")
        self.slider_speed.set(0)

        # Botões de Ação
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="ew")
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.btn_speak = ctk.CTkButton(
            btn_frame, 
            text="▶ Ouvir Áudio", 
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            command=self.start_speaking
        )
        self.btn_speak.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.btn_stop = ctk.CTkButton(
            btn_frame, 
            text="⏹ Parar", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#D32F2F", 
            hover_color="#9A0007",
            height=45,
            command=self.stop_speaking
        )
        self.btn_stop.grid(row=0, column=1, padx=5, sticky="ew")

        self.btn_export = ctk.CTkButton(
            btn_frame, 
            text="💾 Exportar Áudio", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2E7D32", 
            hover_color="#1B5E20",
            height=45,
            command=self.start_export
        )
        self.btn_export.grid(row=0, column=2, padx=(5, 0), sticky="ew")

        # Barra de Status
        self.lbl_status = ctk.CTkLabel(self, text="Pronto.", font=ctk.CTkFont(size=12), text_color="gray")
        self.lbl_status.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="w")

    def update_speed_label(self, value):
        val = int(value)
        if val > 0:
            self.lbl_speed.configure(text=f"Velocidade da Fala: +{val}%")
        else:
            self.lbl_speed.configure(text=f"Velocidade da Fala: {val}%")

    def get_speech_params(self):
        text = self.txt_input.get("1.0", "end-1c").strip()
        profile_name = self.combo_voice.get()
        voice_id = self.voice_profiles[profile_name]

        slider_val = int(self.slider_speed.get())
        
        if slider_val > 0:
            rate_str = f"+{slider_val}%"
        elif slider_val < 0:
            rate_str = f"{slider_val}%"
        else:
            rate_str = None

        return text, voice_id, rate_str

    def start_speaking(self):
        text, voice_id, rate_str = self.get_speech_params()
        if not text or len(text) < 2:
            self.lbl_status.configure(text="Digite uma frase com mais de 2 letras para gerar o áudio.", text_color="#FF9800")
            return

        self.stop_speaking()
        self.btn_speak.configure(state="disabled")
        self.lbl_status.configure(text="Sintetizando voz humana...", text_color="#2196F3")
        
        asyncio.run_coroutine_threadsafe(
            self.generate_and_play(text, voice_id, rate_str), 
            self.loop
        )

    async def generate_and_play(self, text, voice_id, rate_str):
        try:
            if rate_str:
                communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
            else:
                communicate = edge_tts.Communicate(text, voice_id)

            await communicate.save(self.temp_audio_file)

            self.lbl_status.configure(text="Reproduzindo...", text_color="#4CAF50")
            
            pygame.mixer.music.load(self.temp_audio_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)

            self.lbl_status.configure(text="Concluído.", text_color="gray")

        except Exception as e:
            self.lbl_status.configure(text=f"Erro ao sintetizar áudio: {e}", text_color="#F44336")
        finally:
            pygame.mixer.music.unload()
            self.btn_speak.configure(state="normal")

    def start_export(self):
        text, voice_id, rate_str = self.get_speech_params()
        if not text or len(text) < 2:
            self.lbl_status.configure(text="Digite uma frase com mais de 2 letras para exportar.", text_color="#FF9800")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".mp3",
            filetypes=[("Arquivo MP3", "*.mp3"), ("Arquivo WAV", "*.wav")],
            title="Salvar Áudio"
        )

        if not file_path:
            return

        self.btn_export.configure(state="disabled")
        self.lbl_status.configure(text="Exportando áudio...", text_color="#2196F3")

        asyncio.run_coroutine_threadsafe(
            self.export_audio(text, voice_id, rate_str, file_path), 
            self.loop
        )

    async def export_audio(self, text, voice_id, rate_str, file_path):
        try:
            if rate_str:
                communicate = edge_tts.Communicate(text, voice_id, rate=rate_str)
            else:
                communicate = edge_tts.Communicate(text, voice_id)
            
            if file_path.lower().endswith('.wav'):
                temp_mp3 = os.path.join(tempfile.gettempdir(), "export_temp.mp3")
                await communicate.save(temp_mp3)
                
                sound = pygame.mixer.Sound(temp_mp3)
                buffer = sound.get_raw()
                
                import wave
                with wave.open(file_path, 'wb') as wave_file:
                    wave_file.setnchannels(2)
                    wave_file.setsampwidth(2)
                    wave_file.setframerate(44100)
                    wave_file.writeframes(buffer)
                
                if os.path.exists(temp_mp3):
                    os.remove(temp_mp3)
            else:
                await communicate.save(file_path)

            self.lbl_status.configure(text="Áudio salvo com sucesso!", text_color="#4CAF50")

        except Exception as e:
            self.lbl_status.configure(text=f"Erro ao exportar: {e}", text_color="#F44336")
        finally:
            self.btn_export.configure(state="normal")

    def stop_speaking(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        self.btn_speak.configure(state="normal")
        self.lbl_status.configure(text="Reprodução interrompida.", text_color="gray")

if __name__ == "__main__":
    app = AudioGeneratorApp()
    app.mainloop()
