# Entrada de dados
tipo = int(input("Tipo de consulta (1 = normal | 2 = emergencial): "))
nome = input("Nome do paciente: ")

rg = input("RG (9 dígitos ou deixe vazio se não tiver): ").strip()
cpf = input("CPF (11 dígitos ou deixe vazio se não tiver): ").strip()

tem_consulta = int(input("O paciente tem consulta agendada hoje? (1 = sim | 2 = não): "))
tem_medico = int(input("Há médico disponível no dia? (1 = sim | 2 = não): "))
pagamento = int(input("O pagamento está em dia? (1 = sim | 2 = não): "))

# Validação dos documentos
rg_valido = len(rg) == 9
cpf_valido = len(cpf) == 11

tem_documento = rg_valido or cpf_valido
pagamento_em_dia = pagamento == 1
medico_disponivel = tem_medico == 1

print("\n=== RESULTADO DA ANÁLISE ===")
print(f"Paciente: {nome}")

print(f"RG: {rg} ({'Válido' if rg_valido else 'Inválido ou ausente'})")
print(f"CPF: {cpf} ({'Válido' if cpf_valido else 'Inválido ou ausente'})")

# ============================================
#        REGRAS DE AUTORIZAÇÃO CORRIGIDAS
# ============================================

if tipo == 1:
    print("Tipo: CONSULTA NORMAL")

    if not tem_documento:
        print("→ CONSULTA BLOQUEADA: Documento inválido ou ausente.")
    elif not pagamento_em_dia:
        print("→ CONSULTA BLOQUEADA: Pagamento em atraso.")
    elif not medico_disponivel:
        print("→ CONSULTA BLOQUEADA: Não há médico disponível.")
    else:
        print("→ ATENDIMENTO LIBERADO (Consulta Normal)")

else:
    print("Tipo: CONSULTA EMERGÊNCIA")

    # Regra corrigida:
    # Emergência = Há médico disponível E (tem documento OU pagamento em dia)
    if not medico_disponivel:
        print("→ EMERGÊNCIA BLOQUEADA: Não há médico disponível.")
    elif tem_documento or pagamento_em_dia:
        print("→ ATENDIMENTO LIBERADO (Emergência)")
    else:
        print("→ EMERGÊNCIA BLOQUEADA: Sem documentos e pagamento atrasado simultaneamente.")

