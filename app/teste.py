import requests
import time
import random
import csv
import json
from datetime import datetime

# === CONFIGURAÇÕES ===
USERNAME = "username"
LIMITE_SEGUIDORES = 15
PAUSA_MINIMA = 15
PAUSA_MAXIMA = 30
CSV_FILENAME = f"seguidores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

# === COOKIES E HEADERS ===
COOKIES = {
    "csrftoken": "csrftoken",
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
                    "data_coleta": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

                if len(dados_coletados) >= LIMITE_SEGUIDORES:
                    break

            has_next = page_info["has_next_page"]
            end_cursor = page_info["end_cursor"]
            pausa_aleatoria()

    except Exception as e:
        print(f"[ERRO] {e}")
        return []

    return dados_coletados

def coletar_curtidores(username, user_id, cookies, headers, max_posts=10):
    print(f"\n[✓] Buscando últimos {max_posts} posts de @{username}...")
    sessao = requests.Session()
    curtidores = set()
    shortcode_list = []

    try:
        url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
        resp = sessao.get(url, headers=headers, cookies=cookies)

        if resp.status_code != 200:
            print(f"[ERRO] Não consegui acessar o perfil. Código HTTP {resp.status_code}")
            return curtidores

        json_data = resp.json()
        edges = json_data['graphql']['user']['edge_owner_to_timeline_media']['edges']

        for edge in edges[:max_posts]:
            shortcode = edge['node']['shortcode']
            shortcode_list.append(shortcode)

        print(f"[✓] Encontrados {len(shortcode_list)} posts. Coletando curtidores...")

        for shortcode in shortcode_list:
            print(f"[POST] {shortcode}")
            url_post = f"https://i.instagram.com/api/v1/media/{shortcode}/likers/"
            headers_post = headers.copy()
            headers_post["User-Agent"] = ""
            headers_post["X-IG-App-ID"] = ""

            resp_post = sessao.get(url_post, headers=headers_post, cookies=cookies)
            if resp_post.status_code != 200:
                print(f"[ERRO] Código HTTP curtidas {resp_post.status_code}")
                continue

            data = resp_post.json()
            for user in data.get('users', []):
                curtidores.add(user['username'])

            time.sleep(random.uniform(2, 5))

    except Exception as e:
        print(f"[ERRO] Coleta de curtidas falhou: {e}")

    return curtidores

def main():
    print("[TESTE] Verificando conexão com Instagram...")
    try:
        dados = coletar_usuarios()
        curtidores = coletar_curtidores(USERNAME, COOKIES["ds_user_id"], COOKIES, HEADERS)

        if dados:
            for item in dados:
                item['curtiu_post'] = item['username'] in curtidores
                item['interacao_score'] = 2 if item['curtiu_post'] else 0

            salvar_csv(dados, CSV_FILENAME)
            print("\n[✓] Coleta finalizada com sucesso.")
        else:
            print("[!] Nenhum dado coletado.")

    except Exception as e:
        print(f"[FALHA GERAL] {e}")

    print("[✓] Script encerrado.")

if __name__ == "__main__":
    main()