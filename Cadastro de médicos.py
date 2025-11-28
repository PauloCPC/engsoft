import sqlite3

# -*- coding: utf-8 -*-
from datetime import datetime
import json

# Lista principal para armazenar os médicos.
# Cada médico é um dicionário. A chave 'agenda' é um dicionário que mapeia
# datas (string 'DD/MM/AAAA') para listas de horários disponíveis (strings 'HH:MM').
medicos = []

def cadastrar_medico():
    """Permite ao usuário cadastrar um novo médico (nome, especialidade, CRM)."""
    print("\n--- Cadastro de Novo Médico ---")
    nome = input("Digite o nome completo do médico: ").strip()

    if not nome:
        print("Erro: O nome do médico não pode ser vazio.")
        return

    especialidade = input("Digite a especialidade do médico: ").strip()
    if not especialidade:
        print("Erro: A especialidade não pode ser vazia.")
        return

    crm = input("Digite o CRM do médico (Ex: CRM/SP 123456): ").strip().upper()
    if not crm:
        print("Erro: O CRM não pode ser vazio.")
        return

    # Verifica se já existe um médico com o mesmo CRM
    if any(m['crm'] == crm for m in medicos):
        print(f"Erro: CRM '{crm}' já cadastrado para outro médico.")
        return

    novo_medico = {
        'nome': nome,
        'especialidade': especialidade,
        'crm': crm,
        'agenda': {} # Inicializa a agenda como um dicionário vazio
    }

    medicos.append(novo_medico)
    print(f"\n✅ Médico(a) Dr(a). {nome} ({especialidade}) cadastrado(a) com sucesso!")


def _encontrar_medico(termo_busca):
    """Função utilitária para buscar um médico pelo nome ou CRM (busca parcial e case-insensitive)."""
    termo_lower = termo_busca.lower()
    encontrados = [
        m for m in medicos
        if termo_lower in m['nome'].lower() or termo_lower in m['crm'].lower()
    ]
    return encontrados

def gerenciar_agenda():
    """Permite adicionar horários de disponibilidade na agenda de um médico."""
    print("\n--- Gerenciamento de Agenda ---")
    if not medicos:
        print("Não há médicos cadastrados. Cadastre um médico primeiro.")
        return

    termo_busca = input("Digite o nome ou CRM do médico que deseja gerenciar a agenda: ").strip()
    encontrados = _encontrar_medico(termo_busca)

    if not encontrados:
        print(f"🚫 Médico não encontrado com o termo '{termo_busca}'.")
        return

    # Se múltiplos médicos forem encontrados, lista para seleção
    if len(encontrados) > 1:
        print("\nMultiplos médicos encontrados. Selecione pelo número:")
        for i, m in enumerate(encontrados, 1):
            print(f"{i}. {m['nome']} ({m['especialidade']} - {m['crm']})")

        while True:
            try:
                escolha = int(input("Número do médico: ")) - 1
                if 0 <= escolha < len(encontrados):
                    medico_selecionado = encontrados[escolha]
                    break
                else:
                    print("Escolha inválida.")
            except ValueError:
                print("Entrada inválida. Digite o número.")
    else:
        medico_selecionado = encontrados[0]
        print(f"✅ Gerenciando agenda de: Dr(a). {medico_selecionado['nome']}")

    # Início da gestão da agenda

    print("\nOpções de Agenda:")
    print("1. Adicionar Horários Disponíveis")
    print("2. Visualizar Agenda")

    opcao_agenda = input("Escolha a opção (1 ou 2): ").strip()

    if opcao_agenda == '1':
        # Adicionar Horários
        while True:
            data_agenda = input("Digite a data (DD/MM/AAAA) para adicionar horários: ").strip()
            # Validação simples do formato da data
            try:
                datetime.strptime(data_agenda, "%d/%m/%Y")
                break
            except ValueError:
                print("Formato de data inválido. Use DD/MM/AAAA. Tente novamente.")

        horarios_input = input("Digite os horários disponíveis separados por vírgula (Ex: 09:00, 10:30, 14:00): ").strip()
        if not horarios_input:
            print("Nenhum horário fornecido. Operação cancelada.")
            return

        novos_horarios = [h.strip() for h in horarios_input.split(',') if h.strip()]

        # Adiciona (ou atualiza) os horários na agenda
        if data_agenda not in medico_selecionado['agenda']:
            medico_selecionado['agenda'][data_agenda] = []

        # Garante que não haja duplicatas
        horarios_atuais = set(medico_selecionado['agenda'][data_agenda])
        horarios_atuais.update(novos_horarios)

        # Reordena para melhor visualização (opcional)
        medico_selecionado['agenda'][data_agenda] = sorted(list(horarios_atuais))

        print(f"\n✅ Horários adicionados/atualizados para Dr(a). {medico_selecionado['nome']} em {data_agenda}.")

    elif opcao_agenda == '2':
        # Visualizar Agenda
        agenda = medico_selecionado['agenda']
        if not agenda:
            print("Agenda vazia. Nenhuma disponibilidade cadastrada.")
            return

        print(f"\n--- Agenda de {medico_selecionado['nome']} ---")
        # Itera sobre as datas ordenadamente
        for data in sorted(agenda.keys()):
            horarios = ", ".join(agenda[data])
            print(f"🗓️ {data}: {horarios}")

    else:
        print("Opção inválida.")


def exibir_medicos():
    """Exibe todos os médicos cadastrados de forma organizada."""
    print("\n--- Lista Completa de Médicos ---")

    if not medicos:
        print("Não há médicos cadastrados.")
        return

    # Exibe cabeçalho
    print(f"{'Nº':<4} | {'Nome Completo':<30} | {'Especialidade':<25} | {'CRM':<15}")
    print("-" * 78)

    # Exibe cada médico
    for i, m in enumerate(medicos, 1):
        print(
            f"{i:<4} | {m['nome']:<30} | {m['especialidade']:<25} | {m['crm']:<15}"
        )


def menu():
    """Exibe o menu principal e gerencia a navegação."""

    print("\n" + "="*40)
    print(" Sistema de Gestão de Médicos e Agenda")
    print("="*40)

    while True:
        print("\n--- Menu Principal ---")
        print("1. Cadastrar Novo Médico")
        print("2. Gerenciar Agenda do Médico")
        print("3. Exibir Todos os Médicos")
        print("4. Sair do Sistema")

        escolha = input("Escolha uma opção (1-4): ").strip()

        # Tratamento de Erro para a escolha do menu
        try:
            escolha = int(escolha)

            if escolha == 1:
                cadastrar_medico()
            elif escolha == 2:
                gerenciar_agenda()
            elif escolha == 3:
                exibir_medicos()
            elif escolha == 4:
                print("\nEncerrando o sistema. Obrigado e até logo!")
                break
            else:
                print("⚠️ Opção inválida. Por favor, digite um número entre 1 e 4.")

        except ValueError:
            print("⚠️ Entrada inválida. Por favor, digite o número da opção desejada.")


if __name__ == "__main__":
    menu()