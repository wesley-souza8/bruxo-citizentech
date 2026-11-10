# 🎬 Roteiros de Gravação e Checklist de Entrega — Totem Cidadão Bruxo

**Requisitos do Edital (Maker Lab / Global Solution 2026):** Vídeo demonstrativo de no máximo **6 minutos**, publicado no YouTube como **Não listado** (ou Público), apresentando a justificativa CitizenTech, a explicação da solução física/software e o **MVP real funcionando** na bancada.  
**Integrantes (`4ESR`):** Deivison Pertel (`RM 550803`) · Eduardo Akira Murata (`RM 98713`) · Wesley Souza de Oliveira (`RM 97874`)  
**Disciplina / Professores:** *Project-Based Maker Lab* — Hellynson Cassio Lana, Gedeane Kenshima, Marcus Grillo e Thais Kabuchi.

> Escolha **uma** das duas opções de roteiro abaixo conforme a preferência de gravação (ambas têm **4 a 5 minutos**, com folga para o limite de 6 minutos).

---

## 🎥 Opção 1: Roteiro ao Vivo (Apresentador Falando na Câmera — 4:00 a 4:45)

* **Formato:** Apenas **1 integrante** fala durante todo o vídeo.
* **Cenário:** Totem montado em MDF sobre a mesa, notebook visível ao lado exibindo o terminal do Bruxo rodando (`python main.py`) e uma folha impressa com texto nítido para o teste de OCR.
* **Dicas práticas:** Deixe o volume do notebook no máximo para captar o bipe do buzzer e a voz do Bruxo; se quiser, apoie o roteiro atrás da câmera/monitor para leitura natural. Na leitura OCR (`"Bruxo, escanear texto"`), lembre-se de posicionar o papel na webcam e pressionar **`S`** na janela do OpenCV.

### Bloco 1: Abertura e Contextualização CitizenTech (`0:00 – 1:00`)
*(Apresentador na câmera, ao lado do totem sobre a mesa.)*

> **Apresentador:**  
> *"Olá a todos! Eu sou o Wesley, representando o grupo formado também pelo Deivison Pertel e pelo Eduardo Akira Murata. Nós somos da turma 4ESR de Engenharia de Software da FIAP e este é o projeto final para a disciplina de Project-Based Maker Lab com o professor Hellynson Lana e equipe.*
>
> *No contexto de CitizenTech e cidades inteligentes, nós identificamos um problema crítico de exclusão: a maioria dos totens de autoatendimento em estações e órgãos públicos exige telas touch-screen complexas, o que cria uma barreira enorme para pessoas com deficiência visual, idosos e pessoas com mobilidade reduzida.*
>
> *Para solucionar isso, nós desenvolvemos o Totem Cidadão Bruxo: uma estação interativa de acessibilidade urbana que funciona sem nenhum contato físico, acionada autonomamente por aproximação e controlada totalmente por comandos de voz e visão computacional."*

### Bloco 2: Gabinete Físico (`SolidCraft`) e Eletrônica Embarcada (`1:00 – 2:15`)
*(Câmera aproxima no totem de MDF fechado e depois foca na parte interna com a tampa aberta.)*

> **Apresentador:**  
> *"Começando pela parte física de fabricação digital, todo o gabinete foi projetado por nós no SolidCraft e cortado a laser em MDF de 3 milímetros.*
>
> *Como vocês podem ver aqui no painel frontal, temos duas aberturas circulares calibradas exatamente para os olhos do sensor ultrassônico HC-SR04. E na parte traseira, fizemos um recorte em canaleta para a passagem segura do cabo USB que alimenta o microcontrolador e transmite a telemetria serial.*
>
> *Abrindo aqui a tampa superior de inspeção — que deixamos removível justamente para manutenção —, temos um Arduino Uno R3 conectado a uma mini-protoboard. O circuito conta com o sensor ultrassônico nos pinos digitais 9 e 10, um buzzer piezoelétrico de feedback sonoro no pino 8 e um LED verde indicador no pino 13 com resistor de proteção de 220 ohms."*

### Bloco 3: Demonstração Prática — O Robô Funcionando (`2:15 – 4:00`)
*(Apresentador fecha a tampa do gabinete. Enquadra o totem em primeiro plano e o terminal do notebook rodando `python main.py` ao fundo.)*

> **Apresentador:**  
> *"Agora vamos ver a integração do hardware com o software funcionando na prática. O totem está em modo de espera, com o LED apagado e a aplicação Python escutando a porta serial em segundo plano.*
>
> *Vou simular um cidadão se aproximando a menos de 50 centímetros do totem..."*

*(O apresentador aproxima a mão/corpo em frente ao sensor HC-SR04. O LED verde acende, o buzzer emite o bipe curto de `100 ms` e o Bruxo fala a saudação automática pelo alto-falante: `"Olá! Bem-vindo ao Totem Cidadão. Detectei sua aproximação. Posso orientar seu trajeto, informar serviços ou ler um documento para você. Como posso ajudar?"`)*

> **Apresentador:**  
> *"Notem que no mesmo instante em que a distância baixou de 50 centímetros, o LED verde acendeu, o buzzer emitiu o alerta auditivo e o Bruxo iniciou o atendimento por voz de forma passiva, sem que eu precisasse tocar em nada ou falar palavras de ativação!*
>
> *Agora, como cidadão, vou solicitar uma informação pública por voz..."*

*(Apresentador fala para o microfone, com ou sem wake word durante a sessão ativa):*  
> *"Bruxo, quais são os serviços de transporte público essenciais nesta região?"*

*(O Bruxo consulta a IA via Groq Cloud e sintetiza a resposta vocal em tempo real.)*

> **Apresentador:**  
> *"Além da IA generativa para tirar dúvidas, nós integramos a visão computacional para ajudar cidadãos com baixa visão a ler documentos físicos. Vou pedir para ele escanear este papel..."*

*(Apresentador aponta a folha impressa para a webcam, diz o comando e pressiona `S` na janela do OpenCV para capturar):*  
> *"Bruxo, escanear texto."*

*(O Bruxo processa a imagem via EasyOCR e lê o texto do papel em voz alta.)*

### Bloco 4: Conclusão e Resiliência (`4:00 – 4:45`)
*(Apresentador se afasta/retira a mão do sensor e volta a enquadrar o totem e o terminal.)*

> **Apresentador:**  
> *"Para finalizar, quando o cidadão se afasta do totem, a distância no sensor ultrassônico volta a subir, o LED verde se apaga automaticamente e a aplicação retorna ao modo standby, pronta para o próximo atendimento sem travar o fluxo principal.*
>
> *Toda a documentação, os arquivos vetoriais DXF e do SolidCraft, o código em C++ do Arduino e a arquitetura modular em Python estão disponíveis publicamente no nosso repositório no GitHub.*
>
> *Muito obrigado a todos e um agradecimento especial ao professor Hellynson e toda a equipe pela mentoria em Maker Lab!"*

---

## 🎙️ Opção 2: Roteiro de Locução em Off / Voice-Over (Bancada + Tela — ~4:15)

* **Formato:** Gravação em duas etapas — primeiro capture a tela (OBS Studio) e os takes da bancada (celular em tripé/suporte); depois grave a narração em off no editor (CapCut ou DaVinci Resolve) sincronizando as falas com cada movimento.

### Bloco 1: Identificação e Contexto CitizenTech (`0:00 – 0:45`)
* **Vídeo (Tela):** Captura do [`README.md`](../README.md) no GitHub (`bruxo-citizentech`), rolando suavemente pelos nomes completos, RMs e Ficha Técnica, seguida por diagrama/tela de contexto.

> **Locução em off:**  
> *"Olá a todos! Este é o projeto de encerramento da disciplina de Project-Based Maker Lab, ministrada pelos professores Hellynson Lana, Gedeane Kenshima, Marcus Grillo e Thais Kabuchi. A equipe é formada por Deivison Pertel, Eduardo Akira Murata e Wesley Souza de Oliveira, da turma 4ESR de Engenharia de Software da FIAP.*
>
> *No ecossistema de CitizenTech e cidades inteligentes, identificamos um obstáculo severo de acessibilidade urbana: grande parte dos totens públicos de autoatendimento depende exclusivamente de interfaces touch-screen visuais. Essa arquitetura exclui idosos, analfabetos funcionais e cidadãos com baixa visão ou mobilidade reduzida. Nossa proposta é o Totem Cidadão Bruxo: uma estação pública acessível que detecta a presença de forma autônoma e opera integralmente por voz e visão computacional, eliminando qualquer contato físico."*

### Bloco 2: Fabricação Digital (`SolidCraft`) e Hardware (`0:45 – 1:45`)
* **Vídeo (Tela → Bancada):** Mostra o SolidCraft / [`img/Pecas.png`](../img/Pecas.png) com as 6 peças cotadas (destaque para furos `Ø 16,2 mm` em [`img/Painel_Frontal_Olhos.png`](../img/Painel_Frontal_Olhos.png) e rasgo USB em [`img/Painel_Traseiro_USB.png`](../img/Painel_Traseiro_USB.png)). Corta para a bancada com o gabinete montado em plano detalhe; uma mão remove a tampa superior e aponta os componentes internos.

> **Locução em off:**  
> *"Na etapa de fabricação digital, modelamos no SolidCraft um gabinete paramétrico composto por seis peças cortadas a laser em MDF de 3 milímetros. O painel frontal conta com dois orifícios circulares calibrados exatamente para as cápsulas do sensor ultrassônico, e o painel traseiro possui um rasgo em canaleta para a conexão do cabo USB.*
>
> *A tampa superior é removível para facilitar a manutenção. No interior, temos uma mini-protoboard e um Arduino Uno R3 gerenciando o sensoriamento. O circuito conecta o sensor ultrassônico HC-SR04 aos pinos 9 e 10, um buzzer piezoelétrico no pino 8 para retorno auditivo imediato, e um LED verde no pino 13 com resistor de 220 ohms, que sinaliza visualmente o início do atendimento."*

### Bloco 3: Demonstração do Sensor e Gatilho Autônomo (`1:45 – 2:45`)
* **Vídeo (Bancada + Terminal ao fundo):** Gabinete fechado em primeiro plano e terminal rodando `python main.py` ao fundo mostrando telemetria de Standby e detecção.

> **Locução em off:**  
> *"Agora, vamos demonstrar a integração de hardware e software na prática. O sistema está ativo em modo de espera, com o LED desligado e o orquestrador em Python monitorando a porta serial sem bloqueio. Vou simular um cidadão se aproximando da estação a menos de 50 centímetros..."*

* **Ação na bancada:** A mão/braço se aproxima da frente do sensor HC-SR04. O LED verde acende, o buzzer dá o bipe curto e o Bruxo reproduz a saudação automática pelo alto-falante:  
  > *"Olá! Bem-vindo ao Totem Cidadão. Detectei sua aproximação. Posso orientar seu trajeto, informar serviços ou ler um documento para você. Como posso ajudar?"*

> **Locução em off:**  
> *"Como pudemos observar no terminal e no hardware, assim que a telemetria do Arduino registrou menos de 50 centímetros, o LED acendeu, o buzzer confirmou a presença e a inteligência artificial assumiu o diálogo por voz de forma passiva, sem toques na tela e sem a necessidade de comandos de ativação."*

### Bloco 4: Demonstração da IA e Visão Computacional (`2:45 – 3:30`)
* **Vídeo (Terminal + Webcam OCR):** Terminal exibindo pergunta e resposta gerada via Groq Cloud; em seguida, folha impressa posicionada diante da webcam para o OCR (pressionando **`S`** para capturar).

> **Locução em off:**  
> *"A partir da saudação, o usuário pode tirar dúvidas sobre serviços urbanos através da IA generativa integrada via Groq Cloud, ou utilizar visão computacional. Vamos testar a leitura assistida para pessoas com deficiência visual."*

* **Ação na bancada:** Áudio do comando *"Bruxo, escanear texto"*, captura pela câmera (tecla `S`), processamento EasyOCR no terminal e leitura em voz alta.

> **Locução em off:**  
> *"O módulo EasyOCR extrai o texto do papel físico e o sintetizador neural lê as orientações diretamente ao cidadão, garantindo autonomia informativa completa."*

### Bloco 5: Teste de Resiliência e Conclusão (`3:30 – 4:15`)
* **Vídeo (Bancada → Tela do GitHub):** Mão se afasta do totem, LED verde apaga, terminal volta a registrar distâncias `>= 50 cm` (`[STANDBY HC-SR04]`) — ou desconexão/reconexão rápida do USB comprovando tratamento não-bloqueante em [`SensorArduino`](../src/sensor_arduino.py). Transição final para o repositório mostrando `cad/` (`.dxf`, `.sc`, `.json`), `arduino/totem_sensor.ino` e `src/`.

> **Locução em off:**  
> *"Por fim, demonstramos a resiliência do sistema: quando o cidadão se afasta da área de alcance, o sensor identifica a ausência, o LED indicador apaga e o robô retorna automaticamente ao modo standby sem travar o loop de escuta.*
>
> *Todos os arquivos vetoriais para corte a laser, diagramas do Tinkercad, firmware em C++ e o código-fonte modular em Python estão documentados no repositório público bruxo-citizentech. Agradecemos a atenção da banca e a orientação dos professores em Maker Lab."*

---

## ✅ Checklist Final de Entrega (Maker Lab & Global Solution)

### 1. Vídeo no YouTube
- [ ] **Duração:** Máximo absoluto de **6 minutos** (roteiros acima ficam entre 4 min 15 s e 4 min 45 s).
- [ ] **Visibilidade:** Publicado como **Não listado** (ou Público).
- [ ] **Teste em janela anônima:** Abrir a URL sem login Google para garantir que não está como *Privado* ou restrito.
- [ ] **Conteúdo obrigatório:** Problema CitizenTech + explicação da solução + **MVP real funcionando** na bancada (HC-SR04 acionando atuadores e IA/OCR por voz).

### 2. Repositório GitHub (`bruxo-citizentech`)
- [ ] **Visibilidade:** Configurado como **Público** (repositório privado zera a avaliação).
- [ ] **Link do vídeo no topo:** Inserir a URL do YouTube no destaque do topo do [`README.md`](../README.md).
- [ ] **Identificação completa e Ficha Técnica:** Nomes completos, RMs (`550803`, `98713`, `97874`), turma `4ESR` e Ficha Técnica visíveis logo na abertura do [`README.md`](../README.md).
- [ ] **Código e fabricação reprodutíveis:** Firmware [`.ino`](../arduino/totem_sensor.ino), código Python modular em [`src/`](../src/) sem caminhos locais absolutos, arquivos de corte/CAD em [`cad/`](../cad/) e guia completo com [`requirements.txt`](../requirements.txt).
- [ ] **Segurança e sigilo:** Nenhuma chave real (`GROQ_API_KEY`, `OPENWEATHER_API_KEY`, `AWESOME_API_KEY`), `.env` ou `contexto.md` comitado — apenas [`.env.example`](../.env.example).

### 3. Envio na Plataforma da Faculdade (Teams / AVA)
- [ ] **Formato único:** Enviar **exclusivamente o link do repositório GitHub** na tarefa de Maker Lab *(não enviar ZIP, RAR, PDF, DOC ou DOCX avulsos)*.
- [ ] **Responsável pelo envio:** Apenas **um integrante** do grupo realiza a entrega antes do prazo limite.
- [ ] **Persistência:** Manter repositório (Público) e vídeo (Não listado/Público) acessíveis durante toda a correção da banca.
