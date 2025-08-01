#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerir seeds no ficheiro data/seeds.json
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class SeedManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.seeds_file = os.path.join(data_dir, "seeds.json")
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Garantir que o diretório data existe"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load_seeds(self) -> List[Dict]:
        """Carregar seeds do ficheiro JSON"""
        if not os.path.exists(self.seeds_file):
            return []
        
        try:
            with open(self.seeds_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def save_seeds(self, seeds: List[Dict]):
        """Guardar seeds no ficheiro JSON"""
        with open(self.seeds_file, 'w', encoding='utf-8') as f:
            json.dump(seeds, f, indent=2, ensure_ascii=False)
    
    def add_seed(self, code: str, tags: List[str], district: str = None, name: str = None) -> bool:
        """Adicionar uma nova seed"""
        seeds = self.load_seeds()
        
        # Verificar se o código já existe
        if any(seed['code'] == code for seed in seeds):
            print(f"Erro: Seed com código {code} já existe!")
            return False
        
        new_seed = {
            'code': code,
            'tags': tags,
            'district': district,
            'name': name or ', '.join(tags),
            'created': datetime.now().isoformat()
        }
        
        seeds.append(new_seed)
        self.save_seeds(seeds)
        print(f"Seed {code} adicionada com sucesso!")
        return True
    
    def remove_seed(self, code: str) -> bool:
        """Remover uma seed pelo código"""
        seeds = self.load_seeds()
        original_count = len(seeds)
        
        seeds = [seed for seed in seeds if seed['code'] != code]
        
        if len(seeds) == original_count:
            print(f"Erro: Seed com código {code} não encontrada!")
            return False
        
        self.save_seeds(seeds)
        print(f"Seed {code} removida com sucesso!")
        return True
    
    def list_seeds(self):
        """Listar todas as seeds"""
        seeds = self.load_seeds()
        
        if not seeds:
            print("Nenhuma seed encontrada.")
            return
        
        print(f"\n{'='*70}")
        print("SEEDS DISPONÍVEIS")
        print(f"{'='*70}")
        
        for i, seed in enumerate(seeds, 1):
            district_info = f" ({seed.get('district', 'Todos os distritos')})" if seed.get('district') else " (Todos os distritos)"
            print(f"{i:2d}. Código: {seed['code']}")
            print(f"    Nome: {seed['name']}")
            print(f"    Distrito: {seed.get('district', 'Todos os distritos')}")
            print(f"    Tags: {', '.join(seed['tags'])}")
            print(f"    Criada: {seed['created']}")
            print("-" * 70)
    
    def search_seed(self, code: str) -> Optional[Dict]:
        """Procurar uma seed pelo código"""
        seeds = self.load_seeds()
        
        for seed in seeds:
            if seed['code'] == code:
                return seed
        
        return None
    
    def get_seed_by_code(self, code: str) -> Optional[Dict]:
        """Obter uma seed pelo código"""
        return self.search_seed(code)

def main():
    """Função principal para testes"""
    manager = SeedManager()
    
    print("=== GERENCIADOR DE SEEDS ===")
    print("1. Listar seeds")
    print("2. Adicionar seed")
    print("3. Remover seed")
    print("4. Procurar seed")
    print("5. Sair")
    
    while True:
        choice = input("\nEscolha uma opção (1-5): ").strip()
        
        if choice == '1':
            manager.list_seeds()
        
        elif choice == '2':
            code = input("Código da seed (ex: SEED123456): ").strip().upper()
            tags_input = input("Tags separadas por vírgula: ").strip()
            tags = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
            
            print("\nDistritos disponíveis:")
            districts = [
                "Aveiro", "Beja", "Braga", "Bragança", "Castelo Branco", "Coimbra",
                "Évora", "Faro", "Guarda", "Leiria", "Lisboa", "Portalegre",
                "Porto", "Santarém", "Setúbal", "Viana do Castelo", "Vila Real",
                "Viseu", "Açores", "Madeira"
            ]
            for i, district in enumerate(districts, 1):
                print(f"{i:2d}. {district}")
            
            district_choice = input("\nEscolha o distrito (número) ou Enter para todos: ").strip()
            district = None
            if district_choice.isdigit() and 1 <= int(district_choice) <= len(districts):
                district = districts[int(district_choice) - 1]
            
            name = input("Nome da seed (opcional): ").strip() or None
            
            if code and tags:
                manager.add_seed(code, tags, district, name)
            else:
                print("Erro: Código e tags são obrigatórios!")
        
        elif choice == '3':
            code = input("Código da seed a remover: ").strip().upper()
            if code:
                manager.remove_seed(code)
            else:
                print("Erro: Código é obrigatório!")
        
        elif choice == '4':
            code = input("Código da seed a procurar: ").strip().upper()
            if code:
                seed = manager.search_seed(code)
                if seed:
                    print(f"\nSeed encontrada:")
                    print(f"Código: {seed['code']}")
                    print(f"Nome: {seed['name']}")
                    print(f"Distrito: {seed.get('district', 'Todos os distritos')}")
                    print(f"Tags: {', '.join(seed['tags'])}")
                    print(f"Criada: {seed['created']}")
                else:
                    print(f"Seed com código {code} não encontrada!")
            else:
                print("Erro: Código é obrigatório!")
        
        elif choice == '5':
            print("Adeus!")
            break
        
        else:
            print("Opção inválida!")

if __name__ == "__main__":
    main() 