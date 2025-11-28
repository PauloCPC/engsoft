# ==============================================================================
# 1. ESTRUTURA DE DADOS: Classe Paciente
# ==============================================================================
class Paciente:
    """Representa um paciente, com atributos e status de atendimento."""
    def __init__(self, nome, cpf, idade):
        self.nome = nome
        self.cpf = cpf
        self.idade = idade
        self.prioridade = self.idade >= 65 
        self.atendido = False 

    def __str__(self):
        status_atendimento = "ATENDIDO" if self.atendido else "AGUARDANDO"
        status_prioridade = "PRIORITÁRIO" if self.prioridade else "Normal"
        return f"Nome: {self.nome} (Idade: {self.idade}) | Status: {status_atendimento} ({status_prioridade})"

# ==============================================================================
# 2. FILAS GLOBAIS
# ==============================================================================
CAPACIDADE_MAX = 5 
fila_atendimento = []     # Pacientes AGUARDANDO (ordenada por prioridade)
pacientes_atendidos = []  # Pacientes que JÁ FORAM ATENDIDOS

# ==============================================================================
# 3. FUNÇÕES DE MANIPULAÇÃO DA FILA
# ==============================================================================

def inserir_paciente(nome, cpf, idade):
    """Insere um paciente na fila, ordenando-o por prioridade."""
    
    if len(fila_atendimento) >= CAPACIDADE_MAX:
        print(f"\n[❌ ERRO] A fila de espera está lotada ({CAPACIDADE_MAX} pacientes).")
        return

    novo_paciente = Paciente(nome, cpf, idade)
    
    # Lógica de Inserção Ordenada (Prioridade)
    posicao_insercao = len(fila_atendimento) 

    if novo_paciente.prioridade:
        for i, paciente_existente in enumerate(fila_atendimento):
            if not paciente_existente.prioridade:
                posicao_insercao = i 
                break
    
    fila_atendimento.insert(posicao_insercao, novo_paciente)
    
    print(f"\n[✅ INSERIDO] {novo_paciente.nome}. Status: {'PRIORITÁRIO' if novo_paciente.prioridade else 'Normal'}")
    print(f"   Posição de espera: {posicao_insercao + 1}º.")


def remover_paciente():
    """Remove o primeiro paciente da fila e o marca como atendido."""
    
    if not fila_atendimento:
        # Retorna False para indicar que a operação não pôde ser completada (fila vazia)
        return False

    # Remove o primeiro paciente
    paciente_atendido = fila_atendimento.pop(0) 
    
    # Rastreamento de atendimento
    paciente_atendido.atendido = True 
    pacientes_atendidos.append(paciente_atendido)
    
    print("\n=============================================")
    print(f"[✅ ATENDIMENTO] Paciente chamado: {paciente_atendido.nome}")
    print(f"Status: {'PRIORITÁRIO' if paciente_atendido.prioridade else 'Normal'}")
    print("=============================================")
    return True # Retorna True para indicar que a operação foi bem-sucedida


def mostrar_status_completo():
    """Exibe o estado de todas as filas."""
    
    print("\n" + "=" * 50)
    print("            RELATÓRIO DE STATUS DA CLÍNICA")
    print("=" * 50)
    
    # --- FILA DE ESPERA (NÃO ATENDIDOS) ---
    print(f"\n### 🪑 FILA DE ESPERA ({len(fila_atendimento)} pacientes) ###")
    if not fila_atendimento:
        print(">> Ninguém aguardando.")
    else:
        for i, paciente in enumerate(fila_atendimento):
            status = "Prioridade" if paciente.prioridade else "Normal"
            print(f"  {i + 1}º ({status}): {paciente.nome} (Idade: {paciente.idade})")
    
    # --- PACIENTES ATENDIDOS ---
    print(f"\n### 👩‍⚕️ PACIENTES JÁ ATENDIDOS ({len(pacientes_atendidos)} pacientes) ###")
    if not pacientes_atendidos:
        print(">> Nenhum paciente foi atendido até o momento.")
    else:
        for paciente in pacientes_atendidos:
            status_prioridade = "Prioridade" if paciente.prioridade else "Normal"
            print(f"  [ATENDIDO]: {paciente.nome} (Idade: {paciente.idade}) - {status_prioridade}")

    print("\n" + "=" * 50)


# ==============================================================================
# 4. LOOP PRINCIPAL COM CONDIÇÕES DE SAÍDA (Novo Requisito)
# ==============================================================================
if __name__ == '__main__':
    
    print("=====================================================")
    print(" BEM-VINDO AO SISTEMA DE FILA DE PRIORIDADES (Clínica)")
    print(f" Capacidade máxima da fila de espera: {CAPACIDADE_MAX}")
    print("=====================================================")

    while True: 
        # ----------------------------------------------------
        # 1. Ponto de Verificação de Parada Automática
        # ----------------------------------------------------
        if not fila_atendimento and pacientes_atendidos:
            print("\n[🚨 ALERTA] A fila de espera está vazia. Todos os pacientes que entraram já foram atendidos!")
            parar = input("Deseja (C)ontinuar (aguardando novos pacientes) ou (E)ncerrar o sistema? ").upper().strip()
            
            if parar == 'E':
                print("\n[👋 SAINDO] Encerrando o sistema a pedido do usuário.")
                break
            elif parar == 'C':
                print("[▶️ CONTINUANDO] Voltando ao menu principal para receber novos pacientes.")
            else:
                print("[⚠️ AVISO] Opção inválida. Continuando no menu.")

        # ----------------------------------------------------
        # 2. Menu Principal
        # ----------------------------------------------------
        print("\nEscolha uma opção:")
        print("1. [➕] Inserir Novo Paciente na Fila")
        print("2. [➡️] Chamar Próximo Paciente (Atendimento)")
        print("3. [📊] Mostrar Status Completo das Filas")
        print("4. [❌] Sair do Sistema")
        
        escolha = input("Opção: ").strip()

        if escolha == '1':
            try:
                print("\n--- INSERÇÃO DE DADOS ---")
                nome = input("   Nome: ")
                cpf = input("   CPF: ")
                idade = int(input("   Idade: "))
                
                if not nome or not cpf or idade <= 0:
                    print("\n[❌ ERRO] Dados inválidos. Tente novamente.")
                    continue

                inserir_paciente(nome, cpf, idade)
                
            except ValueError:
                print("\n[❌ ERRO] A idade deve ser um número inteiro válido. Tente novamente.")
            
        elif escolha == '2':
            remover_paciente()
            
        elif escolha == '3':
            mostrar_status_completo()
            
        elif escolha == '4':
            print("\n[👋 SAINDO] Encerrando o sistema a pedido do usuário.")
            break # Parada manual
            
        else:
            print("\n[⚠️ AVISO] Opção inválida. Digite 1, 2, 3 ou 4.")