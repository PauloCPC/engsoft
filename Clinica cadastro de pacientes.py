# -*- coding: utf-8 -*-
from datetime import date, datetime

# Lista principal para armazenar os pacientes.
# Cada paciente é um dicionário: {'nome': str, 'data_nascimento': str, 'idade': int, 'telefone': str, 'cpf': str, 'prioritario': bool, 'status_pagamento': str}
pacientes = []

def calcular_idade(data_nasc_str):
    """
    Calcula a idade atual com base na data de nascimento (DD/MM/AAAA).
    Retorna a idade (int) ou None se o formato for inválido.
    """
    # Espera o formato DD/MM/AAAA
    try:
        data_nasc = datetime.strptime(data_nasc_str, "%d/%m/%Y").date()
    except ValueError:
        return None # Indica formato inválido
    
    today = date.today()
    
    # Verifica se a data de nascimento é futura
    if data_nasc > today:
        return -1 # Indica uma data futura ou inválida
        
    # Cálculo da idade: ano atual - ano de nascimento - (1 se o aniversário ainda não ocorreu este ano)
    idade = today.year - data_nasc.year - ((today.month, today.day) < (data_nasc.month, data_nasc.day))
    return idade

def cadastrar_paciente():
    """Permite ao usuário cadastrar um novo paciente, solicitando data de nascimento, CPF, telefone e status de pagamento."""
    print("\n--- Cadastro de Novo Paciente ---")
    nome = input("Digite o nome completo do paciente: ").strip()
    
    if not nome:
        print("Erro: O nome do paciente não pode ser vazio.")
        return

    # Loop para garantir que a Data de Nascimento seja válida e calcule a idade
    while True:
        data_nascimento_input = input("Digite a data de nascimento (DD/MM/AAAA): ").strip()
        idade = calcular_idade(data_nascimento_input)
        
        if idade is None:
            print("Erro: Formato de data inválido. Use DD/MM/AAAA (ex: 31/12/1990). Tente novamente.")
        elif idade < 0 or idade > 150:
            print("Erro: Data de nascimento inválida. A idade calculada é irrealista.")
        else:
            break
            
    # Loop para garantir que o CPF seja fornecido e não esteja duplicado
    while True:
        cpf = input("Digite o CPF do paciente (apenas números, se possível): ").strip()
        if not cpf:
            print("Erro: O CPF não pode ser vazio.")
            continue
        # Verifica se o CPF já está cadastrado
        if any(p['cpf'] == cpf for p in pacientes):
            print(f"Erro: CPF '{cpf}' já cadastrado. Por favor, verifique.")
            continue
        break
    
    telefone = input("Digite o telefone do paciente: ").strip()

    # NOVO REQUISITO: Status de Pagamento
    while True:
        print("Status de Pagamento Inicial:")
        print("1. Em Dia")
        print("2. Pendente")
        status_input = input("Escolha o status (1 ou 2): ").strip()
        if status_input == '1':
            status_pagamento = "Em Dia"
            break
        elif status_input == '2':
            status_pagamento = "Pendente"
            break
        else:
            print("Erro: Opção inválida. Digite '1' para Em Dia ou '2' para Pendente.")
            
    # Determina se o paciente tem 60 anos ou mais (Atendimento Prioritário)
    prioritario = idade >= 60

    novo_paciente = {
        'nome': nome,
        'data_nascimento': data_nascimento_input,
        'idade': idade, # Armazena a idade calculada
        'telefone': telefone,
        'cpf': cpf,
        'prioritario': prioritario, # Status de prioridade
        'status_pagamento': status_pagamento # Status de pagamento
    }
    
    pacientes.append(novo_paciente)
    print(f"\n✅ Paciente '{nome}' ({idade} anos, CPF: {cpf}) cadastrado com sucesso!")
    print(f"   Status de Pagamento: {status_pagamento}")
    if prioritario:
        print("   Status de Atendimento: PRIORITÁRIO (Idade >= 60 anos)")


def exibir_estatisticas():
    """Calcula e exibe o número total de pacientes, idade média, e o mais novo/velho."""
    print("\n--- Estatísticas da Clínica Vida+ ---")
    
    total = len(pacientes)
    print(f"1. Número total de pacientes cadastrados: {total}")

    if total == 0:
        print("Não há pacientes cadastrados para calcular estatísticas.")
        return

    # Cálculo da Idade Média
    idades = [p['idade'] for p in pacientes]
    idade_media = sum(idades) / total
    print(f"2. Idade média dos pacientes: {idade_media:.2f} anos")

    # Encontrando o mais novo e o mais velho
    paciente_mais_novo = min(pacientes, key=lambda p: p['idade'])
    paciente_mais_velho = max(pacientes, key=lambda p: p['idade'])
            
    # Exibe os resultados
    print("\n3. Paciente Mais Novo:")
    print(f"   Nome: {paciente_mais_novo['nome']}, Idade: {paciente_mais_novo['idade']} anos")

    print("4. Paciente Mais Velho:")
    print(f"   Nome: {paciente_mais_velho['nome']}, Idade: {paciente_mais_velho['idade']} anos")


def buscar_paciente():
    """Permite buscar pacientes por nome (parcial) ou CPF (exato), exibindo o status de prioridade e pagamento."""
    print("\n--- Busca de Paciente por Nome ou CPF ---")
    if not pacientes:
        print("Não há pacientes cadastrados para buscar.")
        return
        
    termo_busca = input("Digite o nome (ou parte dele) ou o CPF do paciente: ").strip().lower()
    
    if not termo_busca:
        print("O termo de busca não pode ser vazio.")
        return
        
    encontrados = []
    for p in pacientes:
        # Busca por nome (parcial e insensível a maiúsculas/minúsculas)
        if termo_busca in p['nome'].lower():
            encontrados.append(p)
        # Busca por CPF (exato)
        elif termo_busca == p['cpf'].lower():
            encontrados.append(p)

    # Remove duplicatas caso o mesmo paciente seja encontrado por nome e CPF (melhor experiência)
    encontrados = list({id(p):p for p in encontrados}.values())
    
    if encontrados:
        print(f"\n--- {len(encontrados)} Paciente(s) Encontrado(s) ---")
        # Exibe os pacientes encontrados com todas as informações
        for i, p in enumerate(encontrados, 1):
            prioridade_msg = " [PRIORITÁRIO]" if p['prioritario'] else ""
            status_pagamento_msg = f" | Pgto: {p['status_pagamento']}"
            print(f"{i}. Nome: {p['nome']} | Idade: {p['idade']} | CPF: {p['cpf']} | Tel: {p['telefone']}{status_pagamento_msg}{prioridade_msg}")
    else:
        print(f"🚫 Nenhum paciente encontrado com o termo '{termo_busca}'.")


def exibir_pacientes():
    """Exibe todos os pacientes cadastrados de forma organizada, incluindo o status de prioridade e pagamento."""
    print("\n--- Lista Completa de Pacientes ---")
    
    if not pacientes:
        print("Não há pacientes cadastrados.")
        return
        
    # Exibe cabeçalho com todas as colunas
    # Ajuste para incluir a coluna de Pagamento
    print(f"{'Nº':<4} | {'Nome':<30} | {'Nasc.':<12} | {'Idade':<6} | {'CPF':<15} | {'Tel.':<15} | {'Pagamento':<13} | {'Status':<13}")
    print("-" * 110)
    
    # Exibe cada paciente
    for i, p in enumerate(pacientes, 1):
        status_atendimento = "PRIORITÁRIO" if p['prioritario'] else "NORMAL"
        print(
            f"{i:<4} | {p['nome']:<30} | {p['data_nascimento']:<12} | "
            f"{p['idade']:<6} | {p['cpf']:<15} | {p['telefone']:<15} | "
            f"{p['status_pagamento']:<13} | {status_atendimento:<13}"
        )


def menu():
    """Exibe o menu principal e gerencia a navegação."""
    
    print("\n" + "="*55)
    print(" Sistema de Gestão - Clínica Vida+ (v2.2)")
    print("= CPF, Idade Calculada, Prioridade e Pagamento =")
    print("="*55)
    
    while True:
        print("\n--- Menu Principal ---")
        print("1. Cadastrar Novo Paciente (Data Nasc., CPF e Pagamento)")
        print("2. Exibir Estatísticas da Clínica")
        print("3. Buscar Paciente (Nome ou CPF)")
        print("4. Exibir Todos os Pacientes")
        print("5. Sair do Sistema")
        
        escolha = input("Escolha uma opção (1-5): ").strip()
        
        # Tratamento de Erro para a escolha do menu
        try:
            escolha = int(escolha)
            
            if escolha == 1:
                cadastrar_paciente()
            elif escolha == 2:
                exibir_estatisticas()
            elif escolha == 3:
                buscar_paciente()
            elif escolha == 4:
                exibir_pacientes()
            elif escolha == 5:
                print("\nEncerrando o sistema. Obrigado e até logo!")
                break
            else:
                print("⚠️ Opção inválida. Por favor, digite um número entre 1 e 5.")
                
        except ValueError:
            print("⚠️ Entrada inválida. Por favor, digite o número da opção desejada.")


if __name__ == "__main__":
    menu()