import tkinter as tk
import random

LARGURA_JANELA = 500
ALTURA_JANELA = 400

LARGURA_JOGADOR_INICIAL = 60
ALTURA_JOGADOR = 15
VELOCIDADE_JOGADOR = 15

TAMANHO_INIMIGO_PADRAO = 25
VELOCIDADE_INIMIGO_INICIAL = 3
AUMENTO_VELOCIDADE = 0.4

PONTOS_POR_FASE = 5
VIDAS_INICIAIS = 3
VIDAS_MAX = 5

# Tipos de inimigo (frutas): tamanho, cor, multiplicador de velocidade e pontuação
# Laranja  = 1 ponto
# Verde    = 2 pontos (mais rápida)
# Vermelho = -1 ponto
TIPOS_INIMIGO = [
    {"tamanho": 30, "cor": "orange", "mult_vel": 1.0, "pontos": 1},   # laranja
    {"tamanho": 30, "cor": "green", "mult_vel": 1.3, "pontos": 2},    # verde
    {"tamanho": 30, "cor": "red", "mult_vel": 0.9, "pontos": -1},     # vermelho
]

# Parâmetros de dificuldade
DIFICULDADES = {
    "Fácil": {
        "vel_inimigo": 2.5,
        "vel_powerup": 2.5,
        "vel_espinho": 3.0,
        "chance_powerup": 0.35,
        "chance_espinho": 0.05,
    },
    "Médio": {
        "vel_inimigo": 3.0,
        "vel_powerup": 3.0,
        "vel_espinho": 3.8,
        "chance_powerup": 0.3,
        "chance_espinho": 0.1,
    },
    "Difícil": {
        "vel_inimigo": 3.6,
        "vel_powerup": 3.6,
        "vel_espinho": 4.5,
        "chance_powerup": 0.25,
        "chance_espinho": 0.18,
    },
    "Hardcore": {
        "vel_inimigo": 4.2,
        "vel_powerup": 3.8,
        "vel_espinho": 5.0,
        "chance_powerup": 0.15,
        "chance_espinho": 0.28,
    },
}

# Chances adicionais (apenas fase >= 10) – agora bem menores
CHANCE_ESTRELA = 0.02       # antes era maior
CHANCE_RAINBOW = 0.01       # esfera rosa bem mais rara
DURACAO_MODO_RAINBOW_MS = 10000  # 10 segundos


class Jogo:
    def __init__(self, root):
        self.root = root
        self.root.title("Pegue o Quadrado - Versão Turbinada")

        self.canvas = tk.Canvas(
            root,
            width=LARGURA_JANELA,
            height=ALTURA_JANELA,
            bg="black"
        )
        self.canvas.pack()

        # Botão de jogar (tela inicial)
        self.botao_jogar = tk.Button(
            root,
            text="Jogar",
            font=("Arial", 14, "bold"),
            command=self.iniciar_jogo
        )
        self.botao_jogar.pack(pady=10)

        # Seleção de dificuldade
        self.dificuldade_var = tk.StringVar(value="Médio")
        self.frame_dificuldade = tk.Frame(root, bg="black")
        self.frame_dificuldade.pack(pady=5)
        tk.Label(
            self.frame_dificuldade,
            text="Dificuldade:",
            fg="white",
            bg="black",
            font=("Arial", 10, "bold")
        ).pack(side="left", padx=(0, 8))
        for nome in ["Fácil", "Médio", "Difícil", "Hardcore"]:
            tk.Radiobutton(
                self.frame_dificuldade,
                text=nome,
                variable=self.dificuldade_var,
                value=nome,
                fg="white",
                selectcolor="gray20",
                bg="black",
                activebackground="black",
                activeforeground="white",
                font=("Arial", 9)
            ).pack(side="left")

        # Estado
        self.estado = "menu"     # "menu", "jogando", "pausado", "game_over"
        self.loop_iniciado = False

        # Variáveis do jogo
        self.pontos = 0
        self.fase = 1
        self.vidas = VIDAS_INICIAIS
        self.velocidade_inimigo_base = VELOCIDADE_INIMIGO_INICIAL
        self.velocidade_inimigo_atual = VELOCIDADE_INIMIGO_INICIAL
        self.inimigo = None
        self.tipo_inimigo_atual = None

        # Power-up de vida
        self.powerup = None
        self.velocidade_powerup = 3

        # Espinho que tira vidas
        self.espinho = None
        self.velocidade_espinho = 3.5

        # Estrela (aumenta barra)
        self.estrela = None
        self.velocidade_estrela = 3.2
        self.buff_estrela_ativo = False

        # Esfera arco-íris (modo rainbow)
        self.esfera_rainbow = None
        self.velocidade_rainbow = 3.2
        self.modo_rainbow_ativo = False

        # Parâmetros de dificuldade em uso
        self.params_dificuldade = DIFICULDADES["Médio"]
        self.chance_powerup = self.params_dificuldade["chance_powerup"]
        self.chance_espinho = self.params_dificuldade["chance_espinho"]

        # HUD
        self.texto_pontos = None
        self.texto_fase = None
        self.texto_vidas = None
        self.texto_status = None

        # Jogador
        self.jogador = None
        self.largura_jogador_atual = LARGURA_JOGADOR_INICIAL

        # Tela de menu inicial
        self.desenhar_menu()

        # Teclas
        self.root.bind("<Left>", self.mover_esquerda)
        self.root.bind("<Right>", self.mover_direita)
        self.root.bind("<p>", self.toggle_pausa)
        self.root.bind("<P>", self.toggle_pausa)
        self.root.bind("<Return>", self.reiniciar)

        # Controle por mouse
        self.canvas.bind("<Motion>", self.mover_com_mouse)

        # Inicia o loop geral uma vez
        if not self.loop_iniciado:
            self.loop_iniciado = True
            self.atualizar()

    def desenhar_menu(self):
        self.canvas.delete("all")
        self.canvas.create_text(
            LARGURA_JANELA / 2,
            ALTURA_JANELA / 2 - 40,
            text="Pegue o Quadrado",
            fill="white",
            font=("Arial", 24, "bold")
        )
        self.canvas.create_text(
            LARGURA_JANELA / 2,
            ALTURA_JANELA / 2 + 10,
            text=(
                "Use o MOUSE ou setas Esquerda/Direita para mover.\n"
                "Laranjas = +1 | Verdes = +2 | Vermelhos = -1.\n"
                "Espinhos tiram vida ao tocar na barra.\n"
                "A partir da fase 10: Estrela aumenta a barra, esfera rosa ativa frenesi positivo.\n"
                "Escolha a dificuldade e clique em Jogar.\n"
                "P: Pausar / Continuar   Power-ups verdes dão +1 vida."
            ),
            fill="lightgray",
            font=("Arial", 10),
            justify="center"
        )

    def iniciar_jogo(self):
        if self.estado == "jogando":
            return

        # Limpa e configura estado inicial
        self.estado = "jogando"

        # Aplica parâmetros da dificuldade selecionada
        nome_dif = self.dificuldade_var.get()
        self.params_dificuldade = DIFICULDADES.get(nome_dif, DIFICULDADES["Médio"])
        self.velocidade_inimigo_base = self.params_dificuldade["vel_inimigo"]
        self.velocidade_inimigo_atual = self.velocidade_inimigo_base
        self.velocidade_powerup = self.params_dificuldade["vel_powerup"]
        self.velocidade_espinho = self.params_dificuldade["vel_espinho"]
        self.chance_powerup = self.params_dificuldade["chance_powerup"]
        self.chance_espinho = self.params_dificuldade["chance_espinho"]

        self.pontos = 0
        self.fase = 1
        self.vidas = VIDAS_INICIAIS
        self.inimigo = None
        self.tipo_inimigo_atual = None
        self.powerup = None
        self.espinho = None
        self.estrela = None
        self.esfera_rainbow = None
        self.modo_rainbow_ativo = False
        self.buff_estrela_ativo = False
        self.largura_jogador_atual = LARGURA_JOGADOR_INICIAL

        self.canvas.delete("all")

        # Remove botão de jogar (deixa só para a tela inicial)
        if self.botao_jogar is not None:
            self.botao_jogar.pack_forget()

        # HUD
        self.texto_pontos = self.canvas.create_text(
            10, 10,
            anchor="nw",
            fill="white",
            font=("Arial", 12),
            text="Pontos: 0"
        )
        self.texto_fase = self.canvas.create_text(
            LARGURA_JANELA / 2, 10,
            anchor="n",
            fill="white",
            font=("Arial", 12),
            text="Fase: 1"
        )
        self.texto_vidas = self.canvas.create_text(
            LARGURA_JANELA - 10, 10,
            anchor="ne",
            fill="white",
            font=("Arial", 12),
            text=f"Vidas: {self.vidas}"
        )

        # Jogador
        x_inicial = LARGURA_JANELA / 2 - self.largura_jogador_atual / 2
        y_inicial = ALTURA_JANELA - ALTURA_JOGADOR - 10
        self.jogador = self.canvas.create_rectangle(
            x_inicial,
            y_inicial,
            x_inicial + self.largura_jogador_atual,
            y_inicial + ALTURA_JOGADOR,
            fill="dodgerblue"
        )

        self.texto_status = None
        self.resetar_inimigo()

    def atualizar_hud(self):
        self.canvas.itemconfig(self.texto_pontos, text=f"Pontos: {self.pontos}")
        self.canvas.itemconfig(self.texto_fase, text=f"Fase: {self.fase}")
        self.canvas.itemconfig(self.texto_vidas, text=f"Vidas: {self.vidas}")

    def mover_com_mouse(self, event):
        if self.estado != "jogando" or self.jogador is None:
            return
        x_mouse = event.x
        metade = self.largura_jogador_atual / 2
        novo_x1 = max(0, min(LARGURA_JANELA - self.largura_jogador_atual, x_mouse - metade))
        x1_atual, _, x2_atual, _ = self.canvas.coords(self.jogador)
        atual_centro = (x1_atual + x2_atual) / 2
        delta = novo_x1 + metade - atual_centro
        self.canvas.move(self.jogador, delta, 0)

    def mover_esquerda(self, event=None):
        if self.estado != "jogando":
            return
        x1, _, _, _ = self.canvas.coords(self.jogador)
        if x1 > 0:
            self.canvas.move(self.jogador, -VELOCIDADE_JOGADOR, 0)

    def mover_direita(self, event=None):
        if self.estado != "jogando":
            return
        _, _, x2, _ = self.canvas.coords(self.jogador)
        if x2 < LARGURA_JANELA:
            self.canvas.move(self.jogador, VELOCIDADE_JOGADOR, 0)

    def toggle_pausa(self, event=None):
        if self.estado not in ("jogando", "pausado"):
            return

        if self.estado == "jogando":
            self.estado = "pausado"
            if self.texto_status is None:
                self.texto_status = self.canvas.create_text(
                    LARGURA_JANELA / 2,
                    ALTURA_JANELA / 2,
                    text="PAUSADO\nPressione P para continuar",
                    fill="yellow",
                    font=("Arial", 16),
                    justify="center"
                )
        else:
            self.estado = "jogando"
            if self.texto_status is not None:
                self.canvas.delete(self.texto_status)
                self.texto_status = None

    def escolher_tipo_inimigo(self):
        # Modo arco-íris: apenas frutas com pontos positivos
        if self.modo_rainbow_ativo:
            positivos = [t for t in TIPOS_INIMIGO if t["pontos"] > 0]
            return random.choice(positivos)

        nome_dif = self.dificuldade_var.get()
        if nome_dif == "Hardcore":
            # Hardcore: muito mais vermelhos
            lista_pesos = (
                [TIPOS_INIMIGO[0]] * 2 +   # laranja
                [TIPOS_INIMIGO[1]] * 2 +   # verde
                [TIPOS_INIMIGO[2]] * 8     # vermelho
            )
            return random.choice(lista_pesos)

        return random.choice(TIPOS_INIMIGO)

    def resetar_inimigo(self):
        if self.inimigo is not None:
            self.canvas.delete(self.inimigo)

        self.tipo_inimigo_atual = self.escolher_tipo_inimigo()
        tamanho = self.tipo_inimigo_atual["tamanho"]
        cor = self.tipo_inimigo_atual["cor"]

        x = random.randint(0, LARGURA_JANELA - tamanho)
        self.inimigo = self.canvas.create_rectangle(
            x,
            -tamanho,
            x + tamanho,
            0,
            fill=cor
        )

        self.atualizar_velocidade_inimigo()

    def atualizar_velocidade_inimigo(self):
        if self.tipo_inimigo_atual is None:
            self.velocidade_inimigo_atual = self.velocidade_inimigo_base
        else:
            mult = self.tipo_inimigo_atual["mult_vel"]
            base = self.velocidade_inimigo_base
            # Modo arco-íris: torna tudo mais rápido
            if self.modo_rainbow_ativo:
                base *= 1.5
            self.velocidade_inimigo_atual = base * mult

    def criar_powerup(self):
        if self.powerup is not None:
            return

        tamanho = 20
        x = random.randint(0, LARGURA_JANELA - tamanho)
        self.powerup = self.canvas.create_rectangle(
            x,
            -tamanho,
            x + tamanho,
            0,
            fill="limegreen"
        )

    def mover_powerup(self):
        if self.powerup is None:
            return

        self.canvas.move(self.powerup, 0, self.velocidade_powerup)

        # Verifica colisão com jogador
        if self.verificar_colisao_com(self.powerup):
            self.canvas.delete(self.powerup)
            self.powerup = None
            if self.vidas < VIDAS_MAX:
                self.vidas += 1
                self.atualizar_hud()
        else:
            _, y1, _, y2 = self.canvas.coords(self.powerup)
            if y1 > ALTURA_JANELA or y2 > ALTURA_JANELA:
                self.canvas.delete(self.powerup)
                self.powerup = None

    def criar_espinho(self):
        if self.espinho is not None:
            return
        largura_base = 40
        altura = 25
        x = random.randint(0, LARGURA_JANELA - largura_base)
        self.espinho = self.canvas.create_polygon(
            x, -altura,
            x + largura_base, -altura,
            x + largura_base / 2, 0,
            fill="gray80",
            outline="gray30"
        )

    def mover_espinho(self):
        if self.espinho is None:
            return
        self.canvas.move(self.espinho, 0, self.velocidade_espinho)

        if self.verificar_colisao_com(self.espinho):
            self.canvas.delete(self.espinho)
            self.espinho = None
            self.perder_vida()
        else:
            bbox = self.canvas.bbox(self.espinho)
            if bbox is None:
                return
            _, y1, _, y2 = bbox
            if y1 > ALTURA_JANELA or y2 > ALTURA_JANELA:
                self.canvas.delete(self.espinho)
                self.espinho = None

    def criar_estrela(self):
        if self.estrela is not None or self.fase < 10:
            return
        tamanho = 22
        x = random.randint(0, LARGURA_JANELA - tamanho)
        self.estrela = self.canvas.create_polygon(
            x + tamanho * 0.5, -tamanho,
            x + tamanho * 0.6, -tamanho * 0.7,
            x + tamanho, -tamanho * 0.7,
            x + tamanho * 0.7, -tamanho * 0.4,
            x + tamanho * 0.8, 0,
            x + tamanho * 0.5, -tamanho * 0.25,
            x + tamanho * 0.2, 0,
            x + tamanho * 0.3, -tamanho * 0.4,
            x, -tamanho * 0.7,
            x + tamanho * 0.4, -tamanho * 0.7,
            fill="gold",
            outline="orange"
        )

    def mover_estrela(self):
        if self.estrela is None:
            return
        self.canvas.move(self.estrela, 0, self.velocidade_estrela)

        if self.verificar_colisao_com(self.estrela):
            self.canvas.delete(self.estrela)
            self.estrela = None
            self.aplicar_buff_estrela()
        else:
            bbox = self.canvas.bbox(self.estrela)
            if bbox is None:
                return
            _, y1, _, y2 = bbox
            if y1 > ALTURA_JANELA or y2 > ALTURA_JANELA:
                self.canvas.delete(self.estrela)
                self.estrela = None

    def aplicar_buff_estrela(self):
        if self.buff_estrela_ativo or self.jogador is None:
            return
        self.buff_estrela_ativo = True
        x1, y1, x2, y2 = self.canvas.coords(self.jogador)
        centro = (x1 + x2) / 2
        nova_largura = self.largura_jogador_atual * 1.5
        nova_largura = min(nova_largura, LARGURA_JANELA)
        novo_x1 = max(0, centro - nova_largura / 2)
        novo_x2 = min(LARGURA_JANELA, centro + nova_largura / 2)
        self.canvas.coords(self.jogador, novo_x1, y1, novo_x2, y2)
        self.largura_jogador_atual = novo_x2 - novo_x1

    def criar_esfera_rainbow(self):
        if self.esfera_rainbow is not None or self.fase < 10:
            return
        tamanho = 26
        x = random.randint(0, LARGURA_JANELA - tamanho)
        self.esfera_rainbow = self.canvas.create_oval(
            x,
            -tamanho,
            x + tamanho,
            0,
            fill="magenta",
            outline="white"
        )

    def mover_esfera_rainbow(self):
        if self.esfera_rainbow is None:
            return
        self.canvas.move(self.esfera_rainbow, 0, self.velocidade_rainbow)

        if self.verificar_colisao_com(self.esfera_rainbow):
            self.canvas.delete(self.esfera_rainbow)
            self.esfera_rainbow = None
            self.ativar_modo_rainbow()
        else:
            _, y1, _, y2 = self.canvas.coords(self.esfera_rainbow)
            if y1 > ALTURA_JANELA or y2 > ALTURA_JANELA:
                self.canvas.delete(self.esfera_rainbow)
                self.esfera_rainbow = None

    def ativar_modo_rainbow(self):
        if self.modo_rainbow_ativo:
            return
        self.modo_rainbow_ativo = True

        # Ao ativar: remover espinhos e inimigos vermelhos existentes
        if self.espinho is not None:
            self.canvas.delete(self.espinho)
            self.espinho = None
        if self.inimigo is not None and self.tipo_inimigo_atual and self.tipo_inimigo_atual.get("pontos", 0) < 0:
            self.canvas.delete(self.inimigo)
            self.inimigo = None
            self.resetar_inimigo()

        # Bloqueia novos espinhos durante o frenesi
        self.chance_espinho_backup = self.chance_espinho
        self.chance_espinho = 0.0
        self.atualizar_velocidade_inimigo()

        # Desativar depois de alguns segundos
        def desativar():
            self.modo_rainbow_ativo = False
            self.chance_espinho = getattr(self, "chance_espinho_backup", self.chance_espinho)
            self.atualizar_velocidade_inimigo()

        self.root.after(DURACAO_MODO_RAINBOW_MS, desativar)

    def verificar_colisao(self):
        return self.verificar_colisao_com(self.inimigo)

    def verificar_colisao_com(self, objeto):
        if self.jogador is None or objeto is None:
            return False
        x1_j, y1_j, x2_j, y2_j = self.canvas.coords(self.jogador)

        bbox = self.canvas.bbox(objeto)
        if bbox is None:
            return False
        x1_o, y1_o, x2_o, y2_o = bbox

        colisao_horizontal = (x1_j < x2_o) and (x2_j > x1_o)
        colisao_vertical = (y1_j < y2_o) and (y2_j > y1_o)

        return colisao_horizontal and colisao_vertical

    def subir_fase_se_preciso(self):
        nova_fase = max(1, self.pontos // PONTOS_POR_FASE + 1)
        if nova_fase > self.fase:
            self.fase = nova_fase
            self.velocidade_inimigo_base += 0.8
            self.atualizar_velocidade_inimigo()
            self.atualizar_hud()
            self.mostrar_mensagem_temporaria(f"Fase {self.fase}!", 1200)

    def mostrar_mensagem_temporaria(self, texto, duracao_ms):
        msg = self.canvas.create_text(
            LARGURA_JANELA / 2,
            ALTURA_JANELA / 2 - 60,
            text=texto,
            fill="lightgreen",
            font=("Arial", 18),
            justify="center"
        )

        def apagar():
            self.canvas.delete(msg)

        self.root.after(duracao_ms, apagar)

    def perder_vida(self):
        self.vidas -= 1
        self.atualizar_hud()

        if self.vidas <= 0:
            self.game_over()
        else:
            self.resetar_inimigo()

    def game_over(self):
        self.estado = "game_over"

        if self.texto_status is not None:
            self.canvas.delete(self.texto_status)

        self.texto_status = self.canvas.create_text(
            LARGURA_JANELA / 2,
            ALTURA_JANELA / 2,
            text=(
                f"GAME OVER\n"
                f"Pontos: {self.pontos}\n"
                f"Fase alcançada: {self.fase}\n\n"
                f"Pressione Enter para reiniciar"
            ),
            fill="white",
            font=("Arial", 18),
            justify="center"
        )

    def reiniciar(self, event=None):
        if self.estado != "game_over":
            return
        self.iniciar_jogo()

    def atualizar(self):
        if self.estado == "jogando":
            # Mover inimigo
            self.canvas.move(self.inimigo, 0, self.velocidade_inimigo_atual)

            if self.verificar_colisao():
                pontos_inimigo = self.tipo_inimigo_atual.get("pontos", 1) if self.tipo_inimigo_atual else 1
                self.pontos += pontos_inimigo

                if pontos_inimigo > 0:
                    self.velocidade_inimigo_base += AUMENTO_VELOCIDADE
                self.atualizar_velocidade_inimigo()
                self.atualizar_hud()
                self.subir_fase_se_preciso()

                if random.random() < self.chance_powerup:
                    self.criar_powerup()

                self.resetar_inimigo()
            else:
                _, y1_i, _, y2_i = self.canvas.coords(self.inimigo)
                if y1_i > ALTURA_JANELA or y2_i > ALTURA_JANELA:
                    if random.random() < self.chance_powerup:
                        self.criar_powerup()
                    self.resetar_inimigo()

            # Power-up de vida
            if self.powerup is not None:
                self.mover_powerup()

            # Espinho (não aparece no modo arco-íris)
            if not self.modo_rainbow_ativo and self.espinho is None and random.random() < self.chance_espinho:
                self.criar_espinho()
            if self.espinho is not None:
                self.mover_espinho()

            # Estrela (buff de tamanho, só fase >= 10)
            if self.fase >= 10 and self.estrela is None and random.random() < CHANCE_ESTRELA:
                self.criar_estrela()
            if self.estrela is not None:
                self.mover_estrela()

            # Esfera arco-íris (modo rainbow, só fase >= 10)
            if self.fase >= 10 and not self.modo_rainbow_ativo and self.esfera_rainbow is None and random.random() < CHANCE_RAINBOW:
                self.criar_esfera_rainbow()
            if self.esfera_rainbow is not None:
                self.mover_esfera_rainbow()

        self.root.after(20, self.atualizar)


if __name__ == "__main__":
    root = tk.Tk()
    jogo = Jogo(root)
    root.mainloop()