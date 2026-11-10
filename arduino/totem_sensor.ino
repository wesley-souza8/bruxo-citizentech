// Definição dos pinos conforme o circuito montado no Tinkercad
const int TRIG_PIN = 9;   // Fio azul no pino digital 9
const int ECHO_PIN = 10;  // Fio roxo no pino digital 10
const int LED_PIN  = 13;  // Fio verde no pino digital 13
const int BUZZER   = 8;   // Fio amarelo no pino digital 8

// Distância de disparo (< 50 cm) e histerese para evitar repique no limite
const int DISTANCIA_GATILHO = 50;
const int HISTERESE_SAIDA_CM = 5;
const int MAX_LEITURAS_SEM_ECO = 3;

bool cidadaoPresente = false;
int leiturasSemEco = 0;

void setup() {
  // Inicia a comunicação serial para conversar com o Python do Bruxo
  Serial.begin(9600);

  // Configuração dos modos dos pinos
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER, OUTPUT);

  // Garante atuadores desligados ao inicializar
  digitalWrite(LED_PIN, LOW);
  noTone(BUZZER);
}

void loop() {
  // 1. Emite o pulso ultrassônico limpo de 10 microssegundos
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // 2. Mede o tempo de retorno do eco (timeout de 30 ms para ~5 metros)
  long duracao = pulseIn(ECHO_PIN, HIGH, 30000);

  // 3. Converte tempo para distância em centímetros (v = 340 m/s)
  int distancia = duracao * 0.034 / 2;

  // 4. Lógica de detecção de aproximação (CitizenTech - Totem Acessível)
  if (distancia > 0 && distancia < DISTANCIA_GATILHO) {
    leiturasSemEco = 0;
    digitalWrite(LED_PIN, HIGH);  // Mantém o LED verde aceso durante o atendimento

    // Toca o bip curto apenas na chegada (< 50 cm), evitando interferência no microfone
    if (!cidadaoPresente) {
      cidadaoPresente = true;
      tone(BUZZER, 1200, 100);
    }
  } else if (distancia >= (DISTANCIA_GATILHO + HISTERESE_SAIDA_CM)) {
    leiturasSemEco = 0;
    cidadaoPresente = false;
    digitalWrite(LED_PIN, LOW);   // Apaga o LED em modo de espera
    noTone(BUZZER);
  } else if (distancia <= 0) {
    // Tolera falhas pontuais de eco sem apagar ou re-bipar durante a conversa
    leiturasSemEco++;
    if (leiturasSemEco >= MAX_LEITURAS_SEM_ECO) {
      cidadaoPresente = false;
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER);
    }
  }

  // Envia a distância válida pela Serial (< 50 cm aciona o Bruxo; >= 50 cm telemetria Standby)
  if (distancia > 0) {
    Serial.println(distancia);
  }

  // Intervalo estável entre as leituras
  delay(200);
}
