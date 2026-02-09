Wireless Communication Simulator - FDTD 2D 📡💻

Este projeto simula um sistema de comunicação wireless completo utilizando o método FDTD (Finite-Difference Time-Domain) para resolver as Equações de Maxwell em um ambiente bidimensional. O simulador permite visualizar a propagação de ondas eletromagnéticas, a interação com obstáculos físicos e a transmissão/recepção de dados digitais em tempo real.
🚀 Funcionalidades

    Simulação Física: Resolução numérica das equações de Maxwell para campos Ez​, Hx​ e Hy​.

    Modulação Digital: Implementação de modulação ASK/OOK (On-Off Keying) para envio de mensagens de texto.

    Processamento de Sinais: Receptor com filtro de envelope (Média Móvel Exponencial) e retificação de sinal.

    Sincronização Inteligente: Algoritmo de decodificação que corrige atrasos de propagação (Propagation Delay) e deslocamento de bits (Bit Shift).

    Visualização Dinâmica: Dashboard em tempo real mostrando o status da transmissão, níveis de sinal e mensagem decodificada.

🏗️ O Cenário: "Flat Room with Receiver"

A simulação padrão consiste em:

    Transmissor (TX): Posicionado no centro de uma sala blindada (condutividade σ=800).

    Lente Dielétrica: Uma lente com ϵr​=2.0 posicionada em uma abertura na parede para focalizar o sinal.

    Receptor (RX): Posicionado no ambiente externo (X=0.9), capturando o sinal que atravessa a lente.

🛠️ Detalhes Técnicos
Codificação de Linha e Modulação

Utilizamos a técnica Unipolar NRZ (Non-Return-to-Zero). O bit '1' é representado pela ativação da fonte senoidal (Amplitude = 2000) e o bit '0' pelo silêncio.
Protocolo de Start Bit

Para garantir que o receptor consiga "acordar" e sincronizar seu relógio interno com o transmissor, adicionamos um Start Bit (1) fixo no início de cada mensagem.
Filtro Digital

O receptor utiliza um filtro EMA (Exponential Moving Average) para extrair o envelope da portadora:
St​=St−1​⋅(1−α)+∣Xt​∣⋅α

Onde α=0.2, permitindo uma resposta rápida para a detecção dos bits sem a interferência das oscilações de alta frequência da portadora.

📦 Como Executar

    1. Clone o repositório:

    git clone https://github.com/seu-usuario/fdtd-wireless-comm.git

    2. Certifique-se de ter as dependências instaladas:

    pip install numpy matplotlib opencv-python

    3. Execute o Jupyter Notebook ou o script principal:

    python main.py

📊 Resultados

Ao final da execução, o simulador gera um relatório de transmissão comparando os bits enviados com os recebidos, além de salvar um vídeo (output.mp4) com a animação da propagação das ondas e o painel de telemetria.

========================================
       RELATÓRIO DE TRANSMISSÃO       
========================================
TX (Enviado):  10100111101101001
RX (Recebido): 10100111101101001
----------------------------------------
Mensagem Decodificada: 'Oi'
----------------------------------------
Status: Sucesso (0 erros de bit)
========================================