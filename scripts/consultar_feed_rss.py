import xml.etree.ElementTree as ET
import requests
from typing import List, Dict
import os

def carregar_feed_rss_local(arquivo: str = '../RSS/feed_rss_procedimentos.xml') -> List[Dict]:
    """
    Carrega o feed RSS local e retorna uma lista de procedimentos
    """
    try:
        if not os.path.exists(arquivo):
            print(f"❌ Arquivo {arquivo} não encontrado!")
            print("Execute primeiro o script rss_dre_extractor.py")
            return []
            
        tree = ET.parse(arquivo)
        root = tree.getroot()
        
        procedimentos = []
        
        # Encontrar todos os items
        for item in root.findall('.//item'):
            proc = {}
            
            # Extrair informações básicas
            title = item.find('title')
            if title is not None:
                proc['titulo'] = title.text
            
            link = item.find('link')
            if link is not None:
                proc['link'] = link.text
            
            description = item.find('description')
            if description is not None:
                proc['descricao'] = description.text
            
            pub_date = item.find('pubDate')
            if pub_date is not None:
                proc['data_publicacao'] = pub_date.text
            
            procedimentos.append(proc)
        
        return procedimentos
        
    except Exception as e:
        print(f"❌ Erro ao carregar feed RSS: {e}")
        return []

def carregar_feed_rss_remoto(url: str = 'https://joaodamiao.github.io/RSS-DRE/feed_rss_procedimentos.xml') -> List[Dict]:
    """
    Carrega o feed RSS remoto e retorna uma lista de procedimentos
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        
        procedimentos = []
        
        # Encontrar todos os items
        for item in root.findall('.//item'):
            proc = {}
            
            # Extrair informações básicas
            title = item.find('title')
            if title is not None:
                proc['titulo'] = title.text
            
            link = item.find('link')
            if link is not None:
                proc['link'] = link.text
            
            description = item.find('description')
            if description is not None:
                proc['descricao'] = description.text
            
            pub_date = item.find('pubDate')
            if pub_date is not None:
                proc['data_publicacao'] = pub_date.text
            
            procedimentos.append(proc)
        
        return procedimentos
        
    except Exception as e:
        print(f"❌ Erro ao carregar feed RSS remoto: {e}")
        return []

def mostrar_procedimento(proc: Dict, numero: int):
    """
    Mostra informações detalhadas de um procedimento
    """
    print(f"\n--- PROCEDIMENTO {numero} ---")
    print("=" * 80)
    
    if 'titulo' in proc:
        print(f"TÍTULO: {proc['titulo']}")
        print("=" * 80)
    
    if 'link' in proc:
        print(f"Link: {proc['link']}")
    
    if 'data_publicacao' in proc:
        print(f"Data de publicação: {proc['data_publicacao']}")
    
    if 'descricao' in proc:
        print(f"\nDescrição HTML:")
        print(proc['descricao'][:500] + "..." if len(proc['descricao']) > 500 else proc['descricao'])

def buscar_por_entidade(procedimentos: List[Dict], termo: str) -> List[Dict]:
    """
    Busca procedimentos por entidade
    """
    termo_lower = termo.lower()
    resultados = []
    
    for proc in procedimentos:
        if 'titulo' in proc and termo_lower in proc['titulo'].lower():
            resultados.append(proc)
        elif 'descricao' in proc and termo_lower in proc['descricao'].lower():
            resultados.append(proc)
    
    return resultados

def mostrar_estatisticas(procedimentos: List[Dict]):
    """
    Mostra estatísticas dos procedimentos
    """
    print("\n📊 ESTATÍSTICAS DO FEED RSS")
    print("=" * 50)
    print(f"Total de procedimentos: {len(procedimentos)}")
    
    if procedimentos:
        # Contar entidades mais comuns
        entidades = {}
        for proc in procedimentos:
            if 'titulo' in proc:
                # Extrair entidade do título
                titulo = proc['titulo']
                if ':' in titulo:
                    entidade = titulo.split(':', 1)[1].strip()
                    entidades[entidade] = entidades.get(entidade, 0) + 1
        
        if entidades:
            print(f"\nEntidades mais frequentes:")
            sorted_entidades = sorted(entidades.items(), key=lambda x: x[1], reverse=True)
            for entidade, count in sorted_entidades[:5]:
                print(f"  - {entidade}: {count} procedimentos")

def main():
    """
    Função principal do consultor
    """
    print("=== CONSULTOR DE FEED RSS - PROCEDIMENTOS DRE ===")
    print()
    
    # Tentar carregar feed local primeiro
    print("Carregando feed RSS...")
    procedimentos = carregar_feed_rss_local()
    
    if not procedimentos:
        print("Tentando carregar feed remoto...")
        procedimentos = carregar_feed_rss_remoto()
    
    if not procedimentos:
        print("❌ Não foi possível carregar o feed RSS!")
        return
    
    print(f"Feed RSS carregado com {len(procedimentos)} procedimentos!")
    
    while True:
        print("\nEscolha uma opção:")
        print("1. Mostrar todos os procedimentos")
        print("2. Buscar por entidade")
        print("3. Mostrar estatísticas")
        print("4. Sair")
        
        try:
            opcao = input("\nDigite sua opção (1-4): ").strip()
            
            if opcao == "1":
                print(f"\nMostrando todos os {len(procedimentos)} procedimentos:")
                for i, proc in enumerate(procedimentos, 1):
                    mostrar_procedimento(proc, i)
                    
            elif opcao == "2":
                termo = input("Digite o termo para buscar: ").strip()
                if termo:
                    resultados = buscar_por_entidade(procedimentos, termo)
                    if resultados:
                        print(f"\nEncontrados {len(resultados)} procedimentos:")
                        for i, proc in enumerate(resultados, 1):
                            mostrar_procedimento(proc, i)
                    else:
                        print("Nenhum procedimento encontrado com esse termo.")
                else:
                    print("Por favor, digite um termo para buscar.")
                    
            elif opcao == "3":
                mostrar_estatisticas(procedimentos)
                
            elif opcao == "4":
                print("👋 Até logo!")
                break
                
            else:
                print("❌ Opção inválida. Digite 1, 2, 3 ou 4.")
                
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main() 