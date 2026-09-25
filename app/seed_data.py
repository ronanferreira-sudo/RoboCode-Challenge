from sqlalchemy.orm import Session
from app.models import Activity, TestCase

DEFAULT_ACTIVITIES = [
    {
        "phase": 1,
        "title": "Fase 1: Menagem de Boas Vindas",
        "description": "Bem-vindo à arena RoboCode! Seu primeiro desafio é fazer o robô emitir a mensagem clássica de boas-vindas.\n\n**Objetivo:** Imprima no console a frase `Hello, RoboCode!`",
        "difficulty": "EASY",
        "xp_reward": 50,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'print("Hello, RoboCode!")\n',
        "test_cases": [
            {"input_data": "", "expected_output": "Hello, RoboCode!", "is_hidden": False}
        ]
    },
    {
        "phase": 2,
        "title": "Fase 2: Calculo de Valores",
        "description": "Uma loja deseja calcular o valor total de dois produtos. Crie um programa que leia dois números inteiros (um por linha) e exiba a soma dos valores.\n\nEntrada: Dois números inteiros.\nSaída: Valor total: X onde X é a soma dos dois números.",
        "difficulty": "EASY",
        "xp_reward": 100,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'n1 = int(input())\nn2 = int(input())\nsoma = n1 + n2\nprint("Energia total:", soma)\n',
        "test_cases": [
            {"input_data": "10\n20", "expected_output": "Energia total: 30", "is_hidden": False},
            {"input_data": "50\n50", "expected_output": "Energia total: 100", "is_hidden": True}
        ]
    },
    {
        "phase": 3,
        "title": "Inserir Nome e valor",
        "description": "Crie um programa que solicite o nome de uma pessoa e leia dois números inteiros. O programa deve realizar a soma dos dois números e, ao final, exibir o nome informado e o resultado da soma.\n\nEntrada:\nNome da pessoa.\nPrimeiro número inteiro.\nSegundo número inteiro.\n\nSaída:\nNome: NOME\nTotal: X",
        "difficulty": "EASY",
        "xp_reward": 100,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'nome = input()\nn1 = int(input())\nn2 = int(input())\nsoma = n1 + n2\nprint("Nome:", nome)\nprint("Total:", soma)\n',
        "test_cases": [
            {"input_data": "Joao\n10\n20", "expected_output": "Nome: Joao\nTotal: 30", "is_hidden": False}
        ]
    },
    {
        "phase": 4,
        "title": "Inserir Nome Nota e Media",
        "description": "Crie um programa que solicite o nome de um aluno e leia suas quatro notas. O programa deve calcular a média final das quatro notas e, ao final, exibir o nome do aluno e sua média.\n\nEntrada:\nNome do aluno.\nPrimeira nota.\nSegunda nota.\nTerceira nota.\nQuarta nota.\n\nSaída:\nNome: NOME\nValor da Media: X",
        "difficulty": "EASY",
        "xp_reward": 100,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'nome = input()\nn1 = float(input())\nn2 = float(input())\nn3 = float(input())\nn4 = float(input())\nmedia = (n1 + n2 + n3 + n4) / 4\nprint("Nome:", nome)\nprint("Valor da Media:", media)\n',
        "test_cases": [
            {"input_data": "Joao\n8\n7\n9\n6", "expected_output": "Nome: Joao\nValor da Media: 7.5", "is_hidden": False}
        ]
    },
    {
        "phase": 5,
        "title": "Cadastro de Pessoas",
        "description": "Crie um programa que realize o cadastro de uma pessoa. O programa deve solicitar as seguintes informações:\nNome\nCPF\nTelefone\nNome do pai\nNome da MAE\n\nApós receber todas as informações, o programa deve exibir na tela os dados cadastrados, organizados de forma clara.\n\nEntrada:\nNome\nCPF\nTelefone\nNome do pai\nNome da MAE\n\nSaída:\nNome: NOME\nCPF: CPF\nTelefone: TELEFONE\nNome do PAI: NOME\nNome da MAE: NOME",
        "difficulty": "MEDIUM",
        "xp_reward": 120,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'nome = input()\ncpf = int(input())\ntelefone = int(input())\npai = input()\nmae = input()\nprint("Nome:", nome)\nprint("CPF:", cpf)\nprint("Telefone:", telefone)\nprint("Nome do PAI:", pai)\nprint("Nome da MAE:", mae)\n',
        "test_cases": [
            {"input_data": "Joao\n123456789\n99999999\nPai\nMae", "expected_output": "Nome: Joao\nCPF: 123456789\nTelefone: 99999999\nNome do PAI: Pai\nNome da MAE: Mae", "is_hidden": False}
        ]
    },
    {
        "phase": 6,
        "title": "Utilizar IF e ELSE",
        "description": "Crie um programa que solicite o nome de um aluno e sua nota final. O programa deve utilizar uma estrutura if e else para verificar a situação do aluno.\n\nSe a nota for maior ou igual a 6, o aluno será considerado Aprovado.\nCaso contrário, será considerado Reprovado.\n\nAo final, o programa deve exibir o nome do aluno e sua situação.\n\nEntrada:\nNome do aluno.\nNota final.\n\nSaída:\nNome: NOME\nAprovado\n\nou\n\nNome: NOME\nReprovado",
        "difficulty": "MEDIUM",
        "xp_reward": 150,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'nome = input()\nnota = float(input())\nif nota >= 6:\n    print("Nome:", nome)\n    print("Aprovado")\nelse:\n    print("Nome:", nome)\n    print("Reprovado")\n',
        "test_cases": [
            {"input_data": "Joao\n7.5", "expected_output": "Nome: Joao\nAprovado", "is_hidden": False},
            {"input_data": "Maria\n5.5", "expected_output": "Nome: Maria\nReprovado", "is_hidden": True}
        ]
    },
    {
        "phase": 7,
        "title": "Media e Situacao do Aluno",
        "description": "Crie um programa que solicite o nome de um aluno e leia suas quatro notas. O programa deve calcular a média das quatro notas e utilizar if e else para verificar a situação do aluno.\n\nSe a média for maior ou igual a 6, exiba Situacao: Aprovado.\nCaso contrário, exiba Situacao: Reprovado.\n\nAo final, o programa deve mostrar o nome do aluno, a média calculada e sua situação.\n\nEntrada:\nNome do aluno.\nQuatro notas.\n\nSaída:\nNome: NOME\nSituacao: Aprovado\n\nou\n\nNome: NOME\nSituacao: Reprovado",
        "difficulty": "MEDIUM",
        "xp_reward": 150,
        "initial_code": "# Escreva seu código em Python aqui\n",
        "solution_code": 'nome = input()\nn1 = float(input())\nn2 = float(input())\nn3 = float(input())\nn4 = float(input())\nmedia = (n1 + n2 + n3 + n4) / 4\nif media >= 6:\n    print("Nome:", nome)\n    print("Situacao: Aprovado")\nelse:\n    print("Nome:", nome)\n    print("Situacao: Reprovado")\n',
        "test_cases": [
            {"input_data": "Joao\n8\n7\n9\n6", "expected_output": "Nome: Joao\nSituacao: Aprovado", "is_hidden": False}
        ]
    }
]

def seed_initial_activities(db: Session):
    existing_count = db.query(Activity).count()
    if existing_count == 0:
        print("[INFO] Semeando atividades e casos de teste iniciais no banco de dados...")
        for act_data in DEFAULT_ACTIVITIES:
            act_copy = dict(act_data)
            test_cases_data = act_copy.pop("test_cases")
            activity = Activity(**act_copy)
            db.add(activity)
            db.flush()

            for tc in test_cases_data:
                test_case = TestCase(activity_id=activity.id, **tc)
                db.add(test_case)

        db.commit()
        print("[OK] Atividades semeadas com sucesso!")
    else:
        for act_data in DEFAULT_ACTIVITIES:
            existing = db.query(Activity).filter(Activity.phase == act_data["phase"]).first()
            if existing and not existing.solution_code:
                existing.solution_code = act_data.get("solution_code")
        db.commit()
