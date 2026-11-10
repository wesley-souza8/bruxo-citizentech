"""
Totem Cidadão Bruxo - CitizenTech (Global Solution FIAP 2026)
Integração do Assistente Virtual Bruxo com Arduino Uno + Sensor Ultrassônico HC-SR04.

Ponto de entrada da aplicação.
"""

from src.assistente import AssistenteBruxo
from src.config import (
    ARDUINO_BAUDRATE,
    ARDUINO_PORTA,
    COOLDOWN_TOTEM_SEGUNDOS,
    DISTANCIA_ATIVACAO_CM,
)
from src.sensor_arduino import SensorArduino


def main():
    assistente = AssistenteBruxo()

    sensor = SensorArduino(
        callback_aproximacao=assistente.saudar_aproximacao,
        callback_afastamento=assistente.encerrar_sessao_totem,
        porta=ARDUINO_PORTA,
        baudrate=ARDUINO_BAUDRATE,
        distancia_limite_cm=DISTANCIA_ATIVACAO_CM,
        cooldown_segundos=COOLDOWN_TOTEM_SEGUNDOS,
    )
    sensor.iniciar()

    try:
        assistente.iniciar()
    finally:
        sensor.parar()


if __name__ == "__main__":
    main()
