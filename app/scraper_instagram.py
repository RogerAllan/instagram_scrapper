import psycopg2
import requests
import time
import random
import csv
from datetime import datetime

# === CONFIGURAÇÕES ===
USERNAME = "username"  # Substitua pelo nome de usuário desejado
LIMITE_SEGUIDORES = 150
PAUSA_MINIMA = 15
PAUSA_MAXIMA = 30
CSV_FILENAME = f"seguidores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# === COOKIES E HEADERS ===
COOKIES = {
    "csrftoken": "insira seu csrftoken",
    "ds_user_id": "ds_user_id",
    "sessionid": "sessionid"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "X-CSRFToken": COOKIES["csrftoken"],
    "Referer": f"https://www.instagram.com/{USERNAME}/",
    "Cookie": "; ".join([f"{k}={v}" for k, v in COOKIES.items()])
}

# === FUNÇÕES ===
def pausa_aleatoria():
    delay = random.uniform(PAUSA_MINIMA, PAUSA_MAXIMA)
    print(f"[PAUSA] Aguardando {delay:.1f}s...")
    time.sleep(delay)

def salvar_csv(data, filename):
    try:
        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        print(f"[✓] CSV salvo: {filename}")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar CSV: {e}")

def coletar_usuarios():
    print(f"\n[✓] Iniciando coleta para @{USERNAME}...")

    # GraphQL para pegar seguidores
    query_hash = ""
    url = f"https://www.instagram.com/graphql/query/"

    variables = {
        "id": COOKIES["ds_user_id"],
        "include_reel": True,
        "fetch_mutual": False,
        "first": 50
    }

    dados_coletados = []
    has_next = True
    end_cursor = None
    sessao = requests.Session()

    try:
        while has_next and len(dados_coletados) < LIMITE_SEGUIDORES:
            if end_cursor:
                variables["after"] = end_cursor

            response = sessao.get(url, headers=HEADERS, cookies=COOKIES, params={
                "query_hash": query_hash,
                "variables": json.dumps(variables)
            })

            if response.status_code != 200:
                print(f"[ERRO] Código HTTP {response.status_code}")
                break

            data = response.json()
            edges = data['data']['user']['edge_followed_by']['edges']
            page_info = data['data']['user']['edge_followed_by']['page_info']

            for edge in edges:
                node = edge['node']
                dados_coletados.append({
                    "username": node['username'],
                    "full_name": node['full_name'],
                    "is_private": node['is_private'],
                    "is_verified": node['is_verified'],
                    "profile_pic_url": node['profile_pic_url'],
                    "is_business_account": node.get('is_business_account', False),
                    "is_joined_recently": node.get('is_joined_recently', False),
                    "has_channel": node.get('has_channel', False),
                    "data_coleta": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"[{len(dados_coletados)}] @{node['username']}")

                if len(dados_coletados) >= LIMITE_SEGUIDORES:
                    break

            has_next = page_info["has_next_page"]
            end_cursor = page_info["end_cursor"]
            pausa_aleatoria()

    except Exception as e:
        print(f"[ERRO] {e}")
        return []

    return dados_coletados
# === INSERÇÃO DOS DADOS NO POSTGRES ===
def conectar_postgres():
    return psycopg2.connect(
        host="localhost",
        database="database",
        user="user",
        password="password"
    )

def inserir_no_postgres(dados):
    try:
        conn = conectar_postgres()
        cur = conn.cursor()
        
        for seguidor in dados:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS seguidores_instagram (
                INSERT INTO seguidores_instagram 
                (username, full_name, is_verified, is_private, data_coleta)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                seguidor['username'],
                seguidor['full_name'],
                seguidor['is_verified'],
                seguidor['is_private'],
                seguidor['data_coleta']
            ))

        conn.commit()
        cur.close()
        conn.close()
        print(f"\n[✓] {len(dados)} seguidores inseridos com sucesso no PostgreSQL.")
    except Exception as e:
        print(f"[ERRO BD] Falha ao inserir dados no PostgreSQL: {e}")

# === EXECUÇÃO ===
def main():
    print("[TESTE] Verificando conexão com Instagram...")
    try:
        dados = coletar_usuarios()
        if dados:
            salvar_csv(dados, CSV_FILENAME)
            print("\n[✓] Coleta finalizada com sucesso.")
        else:
            print("[!] Nenhum dado coletado.")
    except Exception as e:
        print(f"[FALHA GERAL] {e}")
    print("[✓] Script encerrado.")

if __name__ == "__main__":
    import json
    main()
