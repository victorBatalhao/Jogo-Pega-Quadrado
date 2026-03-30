# Pegue o Quadrado (Python + Tkinter)

Um jogo simples com interface visual, fases, vidas e power-ups.

## Objetivo
Coletar as peças que valem **pontos positivos** e evitar itens que tiram vidas.

## Controles
- **Mouse**: mova a barra horizontalmente.
- **Teclado (opcional)**:
  - `Seta Esquerda` / `Seta Direita`: mover a barra.
  - `P`: pausar/continuar.
  - `Enter`: reiniciar após *GAME OVER*.

## Pontuação e peças
O jogo lança 3 tipos de frutas (inimigos) caindo:
- **Laranja**: **+1 ponto**
- **Verde**: **+2 pontos** (se move mais rápido que a laranja)
- **Vermelho**: **-1 ponto**

## Vidas e *GAME OVER*
- Você começa com **3 vidas**.
- Perde 1 vida ao encostar no **espinho**.
- Se as vidas chegarem a **0**, aparece *GAME OVER* e você pode reiniciar com `Enter`.

## Fases (dificuldade progressiva)
- As **fases** sobem conforme seus pontos (progressão automática).
- Ao atingir novas fases, o jogo fica mais rápido (maior pressão).
- Recursos especiais ligados à **fase 10** passam a aparecer.

## Espinho (dano na barra)
- O jogo pode lançar um **espinho** (triângulo cinza) caindo.
- Se o espinho encostar na sua barra, você perde **1 vida**.

## Estrela (buff de tamanho) - a partir da fase 10
- A **Estrela** começa a cair quando você estiver em **fase >= 10**.
- Ao pegar a estrela, a barra cresce em **~50% da largura** (até o limite da tela).

## Esfera arco-íris (modo frenesi positivo) - a partir da fase 10
- A **Esfera arco-íris** aparece a partir da **fase >= 10**.
- Ao tocar nela:
  - começa um efeito de **10 segundos** em que **só caem frutas positivas** (**laranja e verde**).
  - espinhos e ameaças vermelhas deixam de aparecer durante o frenesi.

## Dificuldade
Na tela inicial você pode escolher:
- **Fácil**
- **Médio**
- **Difícil**
- **Hardcore**

A dificuldade altera velocidades e frequência de itens (principalmente espinhos/ameaças).

## Como rodar no Windows (PowerShell)
1. Instale Python 3 (se ainda não tiver).
2. Abra o PowerShell.
3. Acesse a pasta do projeto:
   ```powershell
   cd "c:\Users\\Documents\codigos"
   ```
4. Rode o jogo:
   ```powershell
   python jogo_pega_quadrado.py
   ```
   Se `python` não funcionar no seu PC:
   ```powershell
   py jogo_pega_quadrado.py
   ```

## Observações
- O jogo usa `tkinter` (normalmente já vem junto com o Python).
