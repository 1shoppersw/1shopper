import time
import sys
from raspar_ofertas import raspar_e_verificar_ofertas

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

INTERVALO_SEGUNDOS = 180  # 3 minutos (3 * 60 = 180s)

print("🚀 Iniciando monitoramento continuo de precos Mercado Livre...")
print(f"⏰ Intervalo de verificacao: a cada {INTERVALO_SEGUNDOS // 60} minutos.")

while True:
    try:
        raspar_e_verificar_ofertas()
    except Exception as e:
        print(f"[ERRO NO LOOP] {e}")
        
    print(f"⏳ Aguardando {INTERVALO_SEGUNDOS // 60} minutos para a proxima checagem...\n")
    time.sleep(INTERVALO_SEGUNDOS)
