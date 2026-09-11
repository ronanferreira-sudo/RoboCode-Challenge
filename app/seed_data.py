from sqlalchemy.orm import Session
from app.models import Activity, TestCase

DEFAULT_ACTIVITIES = [
    {
        "phase": 1,
        "title": "Fase 1: O Despertar do Robô",
        "description": "Bem-vindo à arena RoboCode! Seu primeiro desafio é fazer o robô emitir a mensagem clássica de boas-vindas.\n\n**Objetivo:** Imprima no console a frase `Hello, RoboCode!`",
        "difficulty": "EASY",
        "xp_reward": 50,
        "initial_code": "# Fase 1: Escreva abaixo o comando para imprimir a mensagem de boas-vindas\nprint(\"\")\n",
        "test_cases": [
            {"input_data": "", "expected_output": "Hello, RoboCode!", "is_hidden": False}
        ]
    },
    {
        "phase": 2,
        "title": "Fase 2: Calculadora de Energia",
        "description": "Os motores do seu robô precisam de energia! Crie um programa que leia dois números inteiros (um por linha) e exiba a soma da energia total.\n\n**Entrada:** Dois números inteiros.\n**Saída:** `Energia total: X` onde X é a soma dos dois números.",
        "difficulty": "EASY",
        "xp_reward": 100,
        "initial_code": "# Leia dois inteiros e exiba a soma\nn1 = int(input())\nn2 = int(input())\n\n# COMPLETE O CÓDIGO AQUI:\n",
        "test_cases": [
            {"input_data": "10\n20", "expected_output": "Energia total: 30", "is_hidden": False},
            {"input_data": "50\n50", "expected_output": "Energia total: 100", "is_hidden": False},
            {"input_data": "123\n456", "expected_output": "Energia total: 579", "is_hidden": True}
        ]
    },
    {
        "phase": 3,
        "title": "Fase 3: Detector de Intrusos",
        "description": "O sistema de segurança precisa validar o nível de acesso do robô. Se o nível de acesso (número inteiro lido) for igual ou maior que 50, exiba `Acesso Concedido`. Caso contrário, exiba `Acesso Negado`.\n\n**Entrada:** Um número inteiro.\n**Saída:** `Acesso Concedido` ou `Acesso Negado`.",
        "difficulty": "MEDIUM",
        "xp_reward": 150,
        "initial_code": "# Leia o nível de acesso do robô\nnivel = int(input())\n\n# Escreva a estrutura condicional aqui:\n",
        "test_cases": [
            {"input_data": "75", "expected_output": "Acesso Concedido", "is_hidden": False},
            {"input_data": "30", "expected_output": "Acesso Negado", "is_hidden": False},
            {"input_data": "50", "expected_output": "Acesso Concedido", "is_hidden": True}
        ]
    },
    {
        "phase": 4,
        "title": "Fase 4: Contagem Regressiva para Decolagem",
        "description": "Seu foguete robótico precisa de uma contagem regressiva antes de lançar! Dado um número inteiro `N` lido da entrada, exiba a contagem de `N` até `1` (um número por linha) e, ao final, a mensagem `DECOLAR!`.\n\n**Exemplo:** Se N = 3, deve imprimir:\n3\n2\n1\nDECOLAR!",
        "difficulty": "MEDIUM",
        "xp_reward": 200,
        "initial_code": "n = int(input())\n\n# Escreva o laço de repetição aqui:\n",
        "test_cases": [
            {"input_data": "3", "expected_output": "3\n2\n1\nDECOLAR!", "is_hidden": False},
            {"input_data": "5", "expected_output": "5\n4\n3\n2\n1\nDECOLAR!", "is_hidden": False}
        ]
    },
    {
        "phase": 5,
        "title": "Fase 5: O Chefão Final - Validador de CyberSenha",
        "description": "🏆 **DESAFIO BOSS!** O banco de dados do sistema precisa validar se uma senha cadastrada é segura. Uma senha é considerada **FORTE** se:\n1. Tiver no mínimo 8 caracteres.\n2. Contiver pelo menos 1 número.\n\nCaso atenda a todos os critérios, imprima `SENHA FORTE`. Caso contrário, imprima `SENHA FRACA`.\n\n**Dica:** Use `len(senha)` e o método `.isdigit()` ou `any(c.isdigit() for c in senha)`.",
        "difficulty": "BOSS",
        "xp_reward": 350,
        "initial_code": "senha = input()\n\n# Implemente a verificação de segurança da senha:\n",
        "test_cases": [
            {"input_data": "RoboCode2026", "expected_output": "SENHA FORTE", "is_hidden": False},
            {"input_data": "curta1", "expected_output": "SENHA FRACA", "is_hidden": False},
            {"input_data": "senhasemnumero", "expected_output": "SENHA FRACA", "is_hidden": False},
            {"input_data": "CyberSec99", "expected_output": "SENHA FORTE", "is_hidden": True}
        ]
    }
]

def seed_initial_activities(db: Session):
    existing_count = db.query(Activity).count()
    if existing_count == 0:
        print("[INFO] Semeando atividades e casos de teste iniciais no banco de dados...")
        for act_data in DEFAULT_ACTIVITIES:
            test_cases_data = act_data.pop("test_cases")
            activity = Activity(**act_data)
            db.add(activity)
            db.flush()

            for tc in test_cases_data:
                test_case = TestCase(activity_id=activity.id, **tc)
                db.add(test_case)

        db.commit()
        print("[OK] Atividades semeadas com sucesso!")
