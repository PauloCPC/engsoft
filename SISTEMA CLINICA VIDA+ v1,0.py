import json
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta 

# Nome do arquivo de persistência
NOME_ARQUIVO_DADOS = 'dados_clinica.json'
CAPACIDADE_MAX = 5 # Capacidade máxima da fila de espera

# ==============================================================================
# 1. ESTRUTURAS DE DADOS GLOBAIS E CLASSE PACIENTE
# ==============================================================================

medicos = []
pacientes_cadastrados = {}
fila_atendimento = []
pacientes_atendidos = []
exames_disponiveis = ["Hemograma Completo", "Glicemia", "Colesterol Total"] 

class Paciente:
    """Representa um paciente, com histórico de atendimentos e prioridade baseada na idade."""
    def __init__(self, nome, cpf, idade, prioridade=None, atendido=False, historico_medico=None):
        self.nome = nome
        self.cpf = cpf
        self.idade = idade
        # Lógica de prioridade: >= 65 anos
        self.prioridade = self.idade >= 65 if prioridade is None else prioridade 
        self.atendido = atendido
        self.historico_medico = historico_medico if historico_medico is not None else [] 

    def __str__(self):
        status_atendimento = "ATENDIDO" if self.atendido else "AGUARDANDO"
        status_prioridade = "PRIORITÁRIO" if self.prioridade else "Normal"
        return f"Nome: {self.nome} (Idade: {self.idade}) | CPF: {self.cpf} | Status: {status_atendimento} ({status_prioridade})"

    def to_dict(self):
        """Converte a instância do Paciente em um dicionário para salvar em JSON."""
        return {
            'nome': self.nome,
            'cpf': self.cpf,
            'idade': self.idade,
            'prioridade': self.prioridade,
            'atendido': self.atendido,
            'historico_medico': self.historico_medico
        }

# ==============================================================================
# 2. FUNÇÕES DE PERSISTÊNCIA (JSON)
# ==============================================================================

def carregar_dados():
    """Tenta carregar os dados de médicos e pacientes do arquivo JSON."""
    global medicos, pacientes_cadastrados, fila_atendimento, pacientes_atendidos
    
    if not os.path.exists(NOME_ARQUIVO_DADOS):
        print("Arquivo de dados não encontrado. Iniciando com dados vazios.")
        return

    try:
        with open(NOME_ARQUIVO_DADOS, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
            medicos = dados.get('medicos', [])
            
            pacientes_data = dados.get('pacientes_cadastrados', {})
            pacientes_cadastrados = {
                cpf: Paciente(**p_data)
                for cpf, p_data in pacientes_data.items()
            }
            
            fila_atendimento = [
                pacientes_cadastrados[cpf] for cpf in dados.get('fila_atendimento', []) 
                if cpf in pacientes_cadastrados
            ]
            pacientes_atendidos = [
                pacientes_cadastrados[cpf] for cpf in dados.get('pacientes_atendidos', []) 
                if cpf in pacientes_cadastrados
            ]
            
            print(f"✅ Dados carregados com sucesso de {NOME_ARQUIVO_DADOS}!")

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"⚠️ Erro ao carregar dados ({e}). Iniciando com dados vazios.")
        medicos = []
        pacientes_cadastrados = {}
        fila_atendimento = []
        pacientes_atendidos = []


def salvar_dados():
    """Salva o estado atual de médicos e pacientes no arquivo JSON."""
    
    pacientes_data = {
        cpf: paciente.to_dict()
        for cpf, paciente in pacientes_cadastrados.items()
    }
    
    fila_atendimento_cpfs = [p.cpf for p in fila_atendimento]
    pacientes_atendidos_cpfs = [p.cpf for p in pacientes_atendidos]
    
    dados = {
        'medicos': medicos,
        'pacientes_cadastrados': pacientes_data,
        'fila_atendimento': fila_atendimento_cpfs,
        'pacientes_atendidos': pacientes_atendidos_cpfs
    }
    
    try:
        with open(NOME_ARQUIVO_DADOS, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        print(f"\n✅ Dados salvos com sucesso em {NOME_ARQUIVO_DADOS}.")
    except Exception as e:
        print(f"\n❌ Erro ao salvar dados: {e}")

# ==============================================================================
# 3. FUNÇÕES AUXILIARES E CADASTRO
# ==============================================================================

def calcular_idade(data_nascimento):
    """Calcula a idade exata em anos a partir da data de nascimento (datetime obj)."""
    hoje = datetime.now()
    diferenca = relativedelta(hoje, data_nascimento)
    return diferenca.years

def _encontrar_medico(termo_busca):
    """Função utilitária para buscar um médico pelo nome ou CRM."""
    termo_lower = termo_busca.lower()
    encontrados = [
        m for m in medicos
        if termo_lower in m['nome'].lower() or termo_lower in m['crm'].lower()
    ]
    return encontrados

def _exibir_medicos_para_escolha():
    """Exibe a lista de médicos cadastrados e permite a escolha por número. Retorna o objeto Médico ou None."""
    if not medicos:
        print("🚫 Nenhum médico cadastrado.")
        return None

    print("\n--- Médicos Cadastrados ---")
    for i, medico in enumerate(medicos):
        print(f"[{i + 1}] Dr(a). {medico['nome']} - CRM: {medico['crm']} - Especialidade: {medico['especialidade']}")

    while True:
        try:
            escolha = input("Escolha o número do médico desejado ou 0 para cancelar: ").strip()
            if escolha == '0':
                print("Operação cancelada.")
                return None
            
            indice_escolhido = int(escolha) - 1
            if 0 <= indice_escolhido < len(medicos):
                return medicos[indice_escolhido]
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")

def _exibir_pacientes_para_escolha():
    """Exibe opções de busca/listagem e retorna o objeto Paciente selecionado ou None."""
    
    if not pacientes_cadastrados:
        print("🚫 Nenhum paciente cadastrado.")
        return None

    pacientes_lista = list(pacientes_cadastrados.values())

    print("\n--- Opções de Seleção de Paciente ---")
    print("1. Listar todos e selecionar por número")
    print("2. Buscar paciente por CPF")
    print("0. Cancelar / Voltar")
    
    while True:
        escolha = input("Escolha uma opção (0-2): ").strip()

        if escolha == '0':
            return None
        
        # Opção 2: Buscar por CPF
        elif escolha == '2':
            cpf = input("Digite o CPF do paciente: ").strip()
            paciente_obj = pacientes_cadastrados.get(cpf)
            if paciente_obj:
                return paciente_obj
            else:
                print(f"🚫 Paciente com CPF {cpf} não encontrado.")
                continue

        # Opção 1: Listar todos e selecionar por número
        elif escolha == '1':
            print("\n--- Pacientes Cadastrados (Seleção) ---")
            
            # Ordena por nome para facilitar a visualização
            pacientes_ordenados = sorted(pacientes_lista, key=lambda p: p.nome)

            for i, p in enumerate(pacientes_ordenados):
                status_prioridade = "PRIORITÁRIO" if p.prioridade else "Normal"
                print(f"[{i + 1}] {p.nome} (CPF: {p.cpf}) - {status_prioridade}")

            while True:
                try:
                    selecao = input("Escolha o número do paciente desejado ou 0 para voltar: ").strip()
                    if selecao == '0':
                        break # Volta para o menu de opções (1, 2, 0)
                    
                    indice_escolhido = int(selecao) - 1
                    if 0 <= indice_escolhido < len(pacientes_ordenados):
                        return pacientes_ordenados[indice_escolhido]
                    else:
                        print("⚠️ Escolha inválida. Tente novamente.")
                except ValueError:
                    print("⚠️ Entrada inválida. Digite um número.")
            continue # Se saiu do loop de seleção, volta para o menu de opções (1, 2, 0)

        else:
            print("⚠️ Opção inválida.")
            
def cadastrar_medico():
    """Permite ao usuário cadastrar um novo médico."""
    print("\n--- Cadastro de Novo Médico ---")
    nome = input("Digite o nome completo do médico: ").strip()
    especialidade = input("Digite a especialidade do médico: ").strip()
    crm = input("Digite o CRM do médico: ").strip().upper()

    if any(m['crm'] == crm for m in medicos):
        print(f"Erro: CRM '{crm}' já cadastrado para outro médico.")
        return

    novo_medico = {
        'nome': nome,
        'especialidade': especialidade,
        'crm': crm,
        'agenda': {},     
        'consultas': {}   
    }

    medicos.append(novo_medico)
    print(f"\n✅ Médico(a) Dr(a). {nome} cadastrado(a) com sucesso!")

def cadastrar_paciente():
    """Função para cadastrar um novo paciente no sistema, calculando a idade pela DDN."""
    print("\n--- Cadastro de Paciente ---")
    
    # 1. Solicita e valida o CPF (APENAS UMA VEZ)
    cpf = ""
    while True:
        cpf_input = input("Digite o CPF do paciente (11 dígitos): ").strip()
        if len(cpf_input) == 11 and cpf_input.isdigit():
            cpf = cpf_input
            break
        print("CPF inválido. Deve conter 11 dígitos numéricos.")

    if cpf in pacientes_cadastrados:
        print(f"Paciente com CPF {cpf} já cadastrado: {pacientes_cadastrados[cpf].nome}")
        return

    nome = input("Nome do paciente: ").strip()
    
    # 2. Solicita e valida a Data de Nascimento
    data_nascimento_str = ""
    while True:
        data_nascimento_str = input("Data de Nascimento (DD/MM/AAAA): ").strip()
        try:
            data_nascimento = datetime.strptime(data_nascimento_str, "%d/%m/%Y")
            if data_nascimento > datetime.now():
                print("🚫 Data de Nascimento não pode ser futura. Tente novamente.")
                continue
            break 
        except ValueError:
            print("🚫 Formato de data inválido. Use DD/MM/AAAA.")
            
    # 3. Calcula a Idade
    idade_calculada = calcular_idade(data_nascimento)
    
    if idade_calculada < 0 or idade_calculada > 130:
        print(f"🚫 Erro no cálculo da idade ({idade_calculada}). Verifique a DDN.")
        return

    # 4. Cria o objeto Paciente
    novo_paciente = Paciente(nome, cpf, idade_calculada)
    pacientes_cadastrados[cpf] = novo_paciente
    
    print(f"\n✅ Paciente {nome} cadastrado com sucesso!")
    print(f"   Idade calculada: {idade_calculada} anos.")
    print(f"   Status: {'PRIORITÁRIO' if novo_paciente.prioridade else 'Normal'}.")
    
def marcar_consulta():
    """Permite à secretária agendar uma consulta, listando datas e horários disponíveis."""
    print("\n--- Agendamento de Consulta ---")

    cpf_busca = input("Digite o CPF do paciente para agendar: ").strip()
    paciente_obj = pacientes_cadastrados.get(cpf_busca)
    
    if not paciente_obj:
        print("🚫 Paciente não encontrado. Cadastre-o primeiro.")
        return
    
    medico = _exibir_medicos_para_escolha()
    
    if not medico:
        return 
    
    # 1. Escolha da Data
    datas_agendadas = sorted(medico['agenda'].keys())
    
    if not datas_agendadas:
        print(f"🚫 Dr(a). {medico['nome']} não tem datas de disponibilidade cadastradas na agenda.")
        return

    print("\nDatas com Disponibilidade:")
    for i, data in enumerate(datas_agendadas):
        print(f"[{i + 1}] {data}")
    
    while True:
        try:
            escolha_data = input("Escolha o número da data desejada: ").strip()
            if not escolha_data.isdigit():
                raise ValueError
            
            indice_data = int(escolha_data) - 1
            if 0 <= indice_data < len(datas_agendadas):
                data_consulta = datas_agendadas[indice_data]
                break
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")

    # 2. Listagem e Escolha do Horário Livre
    horarios_disponiveis = medico['agenda'].get(data_consulta, [])
    consultas_do_dia = medico['consultas'].get(data_consulta, {})
    horarios_agendados = set(consultas_do_dia.keys())
    horarios_livres = sorted(list(set(horarios_disponiveis) - horarios_agendados))
    
    if not horarios_livres:
        print(f"🚫 Não há horários livres para {medico['nome']} em {data_consulta}.")
        return

    print(f"\nHorários Livres para {data_consulta}:")
    for i, h in enumerate(horarios_livres):
        print(f"[{i + 1}] {h}")

    while True:
        try:
            escolha_horario = input("Escolha o número do horário (ou 0 para cancelar): ").strip()
            if escolha_horario == '0':
                return
            
            if not escolha_horario.isdigit():
                raise ValueError

            indice_horario = int(escolha_horario) - 1
            if 0 <= indice_horario < len(horarios_livres):
                horario_escolhido = horarios_livres[indice_horario]
                break
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")

    # 3. Finalização do Agendamento
    if data_consulta not in medico['consultas']:
        medico['consultas'][data_consulta] = {}

    medico['consultas'][data_consulta][horario_escolhido] = {
        'paciente_cpf': paciente_obj.cpf,
        'status': 'AGENDADO'
    }

    print(f"\n🎉 Consulta agendada: Dr(a). {medico['nome']} em {data_consulta} às {horario_escolhido}.")
    
def cancelar_consulta():
    """Permite buscar e cancelar uma consulta agendada, liberando o horário."""
    print("\n--- Cancelamento de Consulta ---")
    
    medico = _exibir_medicos_para_escolha()

    if not medico:
        return 
    
    # 1. Escolha da Data (Lista as datas que possuem consultas agendadas)
    datas_com_consultas = sorted(medico['consultas'].keys())

    if not datas_com_consultas:
        print(f"🚫 Dr(a). {medico['nome']} não possui consultas agendadas.")
        return
        
    print("\nDatas com Consultas Agendadas:")
    for i, data in enumerate(datas_com_consultas):
        print(f"[{i + 1}] {data}")
    
    while True:
        try:
            escolha_data = input("Escolha o número da data da consulta a ser cancelada: ").strip()
            if not escolha_data.isdigit():
                raise ValueError
            
            indice_data = int(escolha_data) - 1
            if 0 <= indice_data < len(datas_com_consultas):
                data_consulta = datas_com_consultas[indice_data]
                break
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")

    # 2. Escolha do Horário para Cancelamento
    consultas_do_dia = medico['consultas'].get(data_consulta, {})
    consultas_validas = {}

    print(f"\nConsultas Ativas para {data_consulta}:")
    i = 1
    horarios_agendados_ativos = []
    for h, info in sorted(consultas_do_dia.items()):
        if info['status'] == 'AGENDADO':
            paciente_cpf = info['paciente_cpf']
            paciente = pacientes_cadastrados.get(paciente_cpf)
            nome_paciente = paciente.nome if paciente else 'Paciente Não Cadastrado'
            print(f"[{i}] Horário {h}: Paciente {nome_paciente}")
            consultas_validas[i] = {'horario': h, 'cpf': paciente_cpf}
            horarios_agendados_ativos.append(h)
            i += 1

    if not consultas_validas:
        print("Não há consultas ativas para cancelamento neste dia.")
        return
        
    while True:
        try:
            escolha_cancelamento = input("Escolha o número da consulta para cancelar (ou 0 para voltar): ").strip()
            if escolha_cancelamento == '0':
                return
            
            if not escolha_cancelamento.isdigit():
                raise ValueError

            indice_cancelar = int(escolha_cancelamento)
            if indice_cancelar in consultas_validas:
                horario_cancelar = consultas_validas[indice_cancelar]['horario']
                break
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")


    # 3. Execução do Cancelamento
    try:
        del medico['consultas'][data_consulta][horario_cancelar]
        
        if not medico['consultas'][data_consulta]:
            del medico['consultas'][data_consulta]

        # Garante que o horário cancelado volte para a lista de horários disponíveis
        if data_consulta in medico['agenda'] and horario_cancelar not in medico['agenda'][data_consulta]:
             medico['agenda'][data_consulta].append(horario_cancelar)
             medico['agenda'][data_consulta].sort()
        
        print(f"\n✅ CANCELAMENTO EFETUADO:")
        print(f"   Consulta com Dr(a). {medico['nome']} às {horario_cancelar} em {data_consulta} cancelada.")
        
    except Exception as e:
        print(f"❌ Erro ao tentar cancelar: {e}")

# ==============================================================================
# 4. GESTÃO DE CADASTROS (MÉDICOS E PACIENTES)
# ==============================================================================

def gerenciar_medicos():
    """Permite listar, selecionar, editar e excluir médicos."""
    while True:
        print("\n--- Gerenciamento de Médicos ---")
        
        medico_selecionado = _exibir_medicos_para_escolha()
        
        if not medico_selecionado:
            return # Volta ao Menu Secretária
        
        print(f"\nMédico Selecionado: Dr(a). {medico_selecionado['nome']} - CRM: {medico_selecionado['crm']}")
        print("a. Editar Dados do Médico")
        print("b. Excluir Médico do Cadastro")
        print("c. Voltar à lista de Médicos")
        
        escolha = input("Escolha uma opção (a/b/c): ").lower().strip()
        
        if escolha == 'a':
            print("\n--- Edição de Dados ---")
            novo_nome = input(f"Novo Nome ({medico_selecionado['nome']}): ").strip() or medico_selecionado['nome']
            nova_especialidade = input(f"Nova Especialidade ({medico_selecionado['especialidade']}): ").strip() or medico_selecionado['especialidade']
            
            medico_selecionado['nome'] = novo_nome
            medico_selecionado['especialidade'] = nova_especialidade
            print(f"✅ Dados de Dr(a). {medico_selecionado['nome']} atualizados!")

        elif escolha == 'b':
            confirmacao = input(f"⚠️ **CONFIRMA EXCLUSÃO** de Dr(a). {medico_selecionado['nome']} (S/N)? ").upper().strip()
            if confirmacao == 'S':
                medicos.remove(medico_selecionado)
                print(f"🗑️ Médico {medico_selecionado['nome']} excluído do cadastro.")
                return # Volta ao Menu Secretária após a exclusão
            else:
                print("Operação de exclusão cancelada.")
        
        elif escolha == 'c':
            continue # Volta para _exibir_medicos_para_escolha()

        else:
            print("⚠️ Opção inválida.")


def gerenciar_pacientes():
    """Permite listar/buscar, selecionar, editar e excluir pacientes."""
    while True:
        print("\n--- Gerenciamento de Pacientes ---")
        print("1. Selecionar Paciente Cadastrado (Lista/Busca)")
        print("2. Cadastrar Novo Paciente")
        print("3. Voltar ao Menu Secretária")

        op = input("Escolha uma opção (1-3): ").strip()

        if op == '2':
            cadastrar_paciente()
            continue

        if op == '3':
            return

        if op == '1':
            # Usa a função que engloba a listagem e busca
            paciente_selecionado = _exibir_pacientes_para_escolha()
            
            if not paciente_selecionado:
                continue # Volta para o menu de gerenciamento de pacientes (1, 2, 3)
                
            print(f"\nPaciente Selecionado: {paciente_selecionado.nome} - CPF: {paciente_selecionado.cpf}")
            print("a. Editar Dados do Paciente")
            print("b. Excluir Paciente do Cadastro")
            print("c. Voltar")
            
            escolha = input("Escolha uma opção (a/b/c): ").lower().strip()
            
            if escolha == 'a':
                print("\n--- Edição de Dados ---")
                novo_nome = input(f"Novo Nome ({paciente_selecionado.nome}): ").strip() or paciente_selecionado.nome
                
                # Assume que a idade/DDN não será editada diretamente para simplificar
                paciente_selecionado.nome = novo_nome
                print(f"✅ Dados de {paciente_selecionado.nome} atualizados!")

            elif escolha == 'b':
                confirmacao = input(f"⚠️ **CONFIRMA EXCLUSÃO** de {paciente_selecionado.nome} (S/N)? ").upper().strip()
                if confirmacao == 'S':
                    cpf_excluir = paciente_selecionado.cpf
                    del pacientes_cadastrados[cpf_excluir]
                    # Também remove da fila, se estiver lá
                    global fila_atendimento
                    fila_atendimento = [p for p in fila_atendimento if p.cpf != cpf_excluir]
                    print(f"🗑️ Paciente {paciente_selecionado.nome} excluído do cadastro.")
                    return # Volta ao menu principal de gerenciamento de pacientes
                else:
                    print("Operação de exclusão cancelada.")
            
            elif escolha == 'c':
                continue # Volta para o menu de gerenciamento de pacientes (opção 1-3)

            else:
                print("⚠️ Opção inválida.")
        
        else:
            print("⚠️ Opção inválida.")


# ==============================================================================
# 5. GESTÃO DE AGENDA (OPÇÃO 7 SECRETÁRIA)
# ==============================================================================

def gerenciar_agenda():
    """Permite à secretária definir os horários de trabalho (agenda) de um médico para uma data."""
    print("\n--- Gerenciamento de Agenda de Médico ---")
    
    medico = _exibir_medicos_para_escolha()

    if not medico:
        return 
    
    datas_atuais = sorted(medico['agenda'].keys())
    
    print("\n--- Datas de Agenda Cadastradas ---")
    if not datas_atuais:
        print("Nenhuma data cadastrada. Você pode adicionar uma nova data.")
        
    for i, data in enumerate(datas_atuais):
        count_horarios = len(medico['agenda'][data])
        print(f"[{i + 1}] {data} (Total de {count_horarios} horários)")
        
    print(f"[0] Adicionar **Nova Data**")
    
    data_agenda = None
    
    while True:
        try:
            escolha_data = input("Escolha o número da data para editar/ver ou 0 para adicionar uma nova: ").strip()
            if not escolha_data.isdigit():
                raise ValueError

            indice_escolha = int(escolha_data)
            
            if indice_escolha == 0:
                # Adicionar Nova Data
                while True:
                    data_input = input("Digite a nova data para gerenciar (DD/MM/AAAA): ").strip()
                    try:
                        datetime.strptime(data_input, "%d/%m/%Y")
                        data_agenda = data_input
                        break
                    except ValueError:
                        print("🚫 Formato de data inválido. Use DD/MM/AAAA.")
                break
                
            elif 1 <= indice_escolha <= len(datas_atuais):
                # Editar Data Existente
                data_agenda = datas_atuais[indice_escolha - 1]
                break
            else:
                print("⚠️ Escolha inválida. Tente novamente.")
        except ValueError:
            print("⚠️ Entrada inválida. Digite um número.")

    if not data_agenda:
        return
    
    # 2. Inserir/Atualizar Horários
    print(f"\n--- Editando Agenda para {data_agenda} (Dr(a). {medico['nome']}) ---")
    
    horarios_atuais = medico['agenda'].get(data_agenda, [])
    
    if horarios_atuais:
        print(f"➡️ Horários atuais: {', '.join(horarios_atuais)}")
    else:
        print("Nenhum horário cadastrado para esta data.")
    
    horarios_str = input("\nDigite os **NOVOS** horários disponíveis (HH:MM) separados por vírgula (Ex: 08:00, 09:00, 10:00). Isso substituirá os anteriores. Digite 'NENHUM' para limpar: ").strip().upper()
    
    if horarios_str == "NENHUM":
        medico['agenda'][data_agenda] = []
        print(f"\n✅ Agenda para {data_agenda} limpa com sucesso.")
        return

    if not horarios_str:
        print("Nenhum horário fornecido. Operação cancelada.")
        return
        
    horarios_lista = [h.strip() for h in horarios_str.split(',')]
    horarios_validos = []
    
    for h in horarios_lista:
        try:
            datetime.strptime(h, "%H:%M")
            horarios_validos.append(h)
        except ValueError:
            print(f"⚠️ Aviso: O horário '{h}' está em formato inválido e foi ignorado.")
    
    if not horarios_validos:
        print("🚫 Nenhum horário válido para salvar.")
        return

    # Atualiza a Agenda (substitui os horários anteriores)
    medico['agenda'][data_agenda] = sorted(list(set(horarios_validos)))
    
    print(f"\n🎉 Agenda de Dr(a). {medico['nome']} atualizada para {data_agenda}.")
    print(f"   Novos horários disponíveis: {', '.join(medico['agenda'][data_agenda])}")


# ==============================================================================
# 6. SISTEMA DE FILA E OUTRAS FUNÇÕES
# ==============================================================================

def sistema_atendimento_ordem_chegada():
    """Simula a entrada de pacientes na fila de atendimento, respeitando a prioridade e a capacidade."""
    global fila_atendimento
    
    print("\n--- Entrada de Pacientes na Fila de Atendimento ---")
    
    if len(fila_atendimento) >= CAPACIDADE_MAX:
        print(f"🚫 Capacidade máxima ({CAPACIDADE_MAX}) da fila atingida. Aguarde liberação.")
        return

    # Utiliza a função de listagem/busca para garantir que o paciente exista
    paciente_obj = _exibir_pacientes_para_escolha()
    
    if not paciente_obj:
        print("Entrada cancelada ou paciente não encontrado.")
        return
        
    if paciente_obj in fila_atendimento:
        print(f"⚠️ Paciente {paciente_obj.nome} já está na fila de atendimento.")
        return

    if paciente_obj.atendido:
        print(f"⚠️ Paciente {paciente_obj.nome} já foi atendido hoje.")
        return
        
    fila_atendimento.append(paciente_obj)
    
    # Reordena a fila para garantir a Prioridade (True > False)
    fila_atendimento.sort(key=lambda p: p.prioridade, reverse=True) 
    
    print(f"\n✅ Paciente {paciente_obj.nome} adicionado à fila.")
    print(f"   Posição na fila: {fila_atendimento.index(paciente_obj) + 1}")
    
def chamar_proximo_paciente():
    """Chama o próximo paciente da fila (primeiro prioritário, depois os normais)."""
    global fila_atendimento
    
    print("\n--- Chamada de Próximo Paciente ---")
    
    if not fila_atendimento:
        print("✅ A fila de atendimento está vazia.")
        return
        
    paciente_a_chamar = fila_atendimento.pop(0) 
    
    print("\n🔔 CHAMANDO PACIENTE:")
    print(f"   Nome: {paciente_a_chamar.nome}")
    print(f"   CPF: {paciente_a_chamar.cpf}")
    print(f"   Status: {'PRIORITÁRIO' if paciente_a_chamar.prioridade else 'Normal'}")

def exibir_status_fila():
    """Exibe o status atual da fila de atendimento."""
    print("\n--- Status Atual da Fila ---")
    if not fila_atendimento:
        print("A fila está vazia.")
    else:
        for i, p in enumerate(fila_atendimento, 1):
            prioridade_str = "PRIORITÁRIO" if p.prioridade else "Normal"
            print(f"{i}. {p.nome} (Idade: {p.idade}) - Status: {prioridade_str}")

def registrar_atendimento():
    """Permite ao médico registrar um atendimento e adicionar notas ao histórico do paciente."""
    print("\n--- Registro de Atendimento e Histórico ---")

    crm_medico = input("Digite seu CRM para registrar o atendimento: ").strip().upper()
    medico_encontrado = _encontrar_medico(crm_medico)
    
    if len(medico_encontrado) != 1:
        print("🚫 CRM inválido ou não encontrado.")
        return
        
    medico = medico_encontrado[0]
    
    cpf_busca = input("Digite o CPF do paciente atendido: ").strip()
    paciente_obj = pacientes_cadastrados.get(cpf_busca)
    
    if not paciente_obj:
        print("🚫 Paciente não cadastrado no sistema.")
        return
        
    print(f"\n✅ Paciente selecionado: {paciente_obj.nome}")
    
    print("\n--- Histórico de Atendimentos ---")
    if not paciente_obj.historico_medico:
        print("Histórico vazio.")
    else:
        for i, registro in enumerate(paciente_obj.historico_medico, 1):
            print(f"[{i}] {registro['data']} | Dr(a). {registro['medico_nome']} | Diagnóstico: {registro['diagnostico']}")
    
    print("\n--- Novo Registro ---")
    diagnostico = input("Diagnóstico (Ex: Gripe Comum, Hipertensão): ").strip()
    procedimento = input("Procedimento/Evolução: ").strip()
    
    novo_registro = {
        'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'medico_crm': crm_medico,
        'medico_nome': medico['nome'],
        'diagnostico': diagnostico,
        'procedimento': procedimento,
    }
    
    paciente_obj.historico_medico.append(novo_registro)
    
    # Marca o paciente como atendido após o registro
    if paciente_obj.atendido == False:
        paciente_obj.atendido = True 
    
    print(f"\n🎉 Atendimento registrado para {paciente_obj.nome} com sucesso!")

def gerar_relatorio_mensal():
    """Gera um relatório do volume de atendimentos e produtividade mensal."""
    print("\n--- Relatório Mensal de Atendimentos ---")
    
    periodo_str = input("Digite o mês e ano para o relatório (MM/AAAA): ").strip()
    
    try:
        datetime.strptime(f"01/{periodo_str}", "%d/%m/%Y")
        mes_ano_filtro = periodo_str
    except ValueError:
        print("🚫 Formato inválido. Use MM/AAAA.")
        return

    total_atendimentos = 0
    atendimentos_por_medico = {}
    atendimentos_por_especialidade = {}
    
    for paciente in pacientes_cadastrados.values():
        for registro in paciente.historico_medico:
            data_atendimento = registro['data'] # Formato DD/MM/AAAA HH:MM
            
            if data_atendimento.endswith(mes_ano_filtro):
                total_atendimentos += 1
                
                crm = registro['medico_crm']
                medico = next((m for m in medicos if m['crm'] == crm), None)
                
                if medico:
                    nome_medico = medico['nome']
                    especialidade = medico['especialidade']
                    
                    atendimentos_por_medico[nome_medico] = atendimentos_por_medico.get(nome_medico, 0) + 1
                    atendimentos_por_especialidade[especialidade] = atendimentos_por_especialidade.get(especialidade, 0) + 1

    print("\n" + "="*50)
    print(f"RELATÓRIO DE ATENDIMENTOS - {mes_ano_filtro}")
    print("="*50)
    print(f"TOTAL DE ATENDIMENTOS REGISTRADOS: {total_atendimentos}")
    print("-" * 50)
    
    if total_atendimentos == 0:
        print("Nenhum atendimento encontrado para o período.")
        return

    print("\nPRODUTIVIDADE POR MÉDICO:")
    for nome, count in sorted(atendimentos_por_medico.items(), key=lambda item: item[1], reverse=True):
        print(f"  - Dr(a). {nome}: {count} atendimentos")

    print("\nDISTRIBUIÇÃO POR ESPECIALIDADE:")
    for especialidade, count in sorted(atendimentos_por_especialidade.items(), key=lambda item: item[1], reverse=True):
        print(f"  - {especialidade}: {count} atendimentos")
    print("="*50)

# ==============================================================================
# 7. MENUS DE NAVEGAÇÃO
# ==============================================================================

def menu_secretaria():
    """Menu de acesso para a Secretária (Opções Reorganizadas)."""
    while True:
        print("\n--- MENU SECRETÁRIA (Clínica Vida+) ---")
        print("1. Cadastrar Novo Paciente")
        print("2. Gerenciar **Pacientes** (Editar/Excluir)")
        print("3. Cadastro de Médicos")
        print("4. Gerenciar **Médicos** (Editar/Excluir)")
        print("5. Marcar Consulta")
        print("6. Cancelar Consulta")
        print("7. Gerenciar Agenda dos Médicos (Disponibilidade)")
        print("8. Gerenciar Fila (Entrada/Chamada)")
        print("9. Exibir status da Fila") 
        print("10. Gerar Relatório Mensal")
        print("11. Voltar ao Menu Principal") 

        escolha = input("Escolha uma opção (1-11): ").strip()

        if escolha == '1':
            cadastrar_paciente()
        elif escolha == '2':
            gerenciar_pacientes()
        elif escolha == '3':
            cadastrar_medico()
        elif escolha == '4':
            gerenciar_medicos()
        elif escolha == '5':
            marcar_consulta()
        elif escolha == '6':
            cancelar_consulta()
        elif escolha == '7':
            gerenciar_agenda()
        elif escolha == '8':
            print("\n--- Gerenciamento de Fila ---")
            print("a. Receber paciente e adicionar à fila")
            print("b. Chamar próximo paciente para atendimento")
            
            sub_escolha = input("Escolha uma opção (a/b/c): ").lower().strip()
            
            if sub_escolha == 'a':
                sistema_atendimento_ordem_chegada()
            elif sub_escolha == 'b':
                chamar_proximo_paciente()
            else:
                print("⚠️ Opção inválida.")
        
        elif escolha == '9':
            exibir_status_fila()
        
        elif escolha == '10':
            gerar_relatorio_mensal()
        elif escolha == '11':
            break
        else:
            print("⚠️ Opção inválida.")

def menu_medico():
    """Menu de acesso para o Médico."""
    while True:
        print("\n--- MENU MÉDICO (Clínica Vida+) ---")
        print("1. Gerenciar Minha Agenda (Visualizar/Adicionar Horários)")
        print("2. Registrar Atendimento e Acessar Histórico")
        print("3. Gerar Receita Médica")
        print("4. Voltar ao Menu Principal")
        
        escolha = input("Escolha uma opção (1-4): ").strip()
        
        if escolha == '1':
            # Nota: Idealmente, o médico só veria/gerenciaria a sua própria agenda,
            # mas mantemos a chamada à função genérica por enquanto.
            gerenciar_agenda() 
        elif escolha == '2':
            registrar_atendimento()
        elif escolha == '3':
            print("Acessando Geração de Receita... [Implementação Pendente]") 
        elif escolha == '4':
            break
        else:
            print("⚠️ Opção inválida.")

def menu_principal():
    """Menu principal de acesso."""
    carregar_dados() 
    
    print("\n" + "="*50)
    print("      SISTEMA DE GESTÃO INTEGRADA DA CLÍNICA")
    print("="*50)

    while True:
        print("\n--- ACESSO PRINCIPAL ---")
        print("1. Acessar como Secretária")
        print("2. Acessar como Médico")
        print("3. Sair do Sistema")

        escolha = input("Escolha uma opção (1-3): ").strip()
        
        if escolha == '1':
            menu_secretaria()
        elif escolha == '2':
            menu_medico()
        elif escolha == '3':
            salvar_dados() 
            print("\nEncerrando o sistema. Obrigado e até logo!")
            break
        else:
            print("⚠️ Opção inválida. Por favor, digite 1, 2 ou 3.")

if __name__ == "__main__":
    menu_principal()