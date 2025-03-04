import datetime
import time
from plyer import notification

def verificar_validade(produto, validade, dias_aviso=90):
    # Converte a string de validade para um objeto datetime
    validade_data = datetime.datetime.strptime(validade, "%d/%m/%Y")
    
    # Data atual
    hoje = datetime.datetime.today()
    
    # Verifica se a validade está dentro do período de aviso
    dias_restantes = (validade_data - hoje).days
    if dias_restantes <= dias_aviso and dias_restantes > 0:
        # Envia uma notificação
        notification.notify(
            title=f"Aviso de validade: {produto}",
            message=f"O produto {produto} está prestes a vencer em {dias_restantes} dias. Validade: {validade}",
            timeout=10
        )
        print(f"Aviso: O produto {produto} está prestes a vencer!")
    elif dias_restantes <= 0:
        print(f"O produto {produto} já venceu!")
    else:
        print(f"O produto {produto} está válido ainda por {dias_restantes} dias.")

def main():
    # Cadastro do produto e validade
    produto = input("Digite o nome do produto: ")
    validade = input("Digite a validade do produto (dd/mm/aaaa): ")

    # Loop que verifica a validade constantemente
    while True:
        verificar_validade(produto, validade)
        time.sleep(86400)  # Verifica a cada 24 horas

if __name__ == "__main__":
    main()