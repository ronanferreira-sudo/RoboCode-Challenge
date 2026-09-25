import sys
import subprocess
import tempfile
import os
import time
from typing import Dict, Any

def execute_python_code(code: str, input_data: str = "", timeout: float = 3.0) -> Dict[str, Any]:
    """
    Executa o código Python fornecido pelo aluno em um processo isolado,
    passando os dados de entrada (stdin) e capturando a saída (stdout / stderr).
    """
    start_time = time.time()
    
    # Injeta um código na primeira linha para ignorar os textos do input()
    injected_code = "import builtins; _orig = builtins.input; builtins.input = lambda prompt='': _orig()\n"
    
    # Cria um arquivo temporário com o código do aluno
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(injected_code + code)
        temp_file_path = temp_file.name

    try:
        # Executa o script Python usando o próprio executável do ambiente
        process = subprocess.Popen(
            [sys.executable, temp_file_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        try:
            stdout_data, stderr_data = process.communicate(input=input_data, timeout=timeout)
            execution_time = (time.time() - start_time) * 1000  # em ms

            err_msg = stderr_data.strip() if stderr_data else None
            if not err_msg:
                err_msg = None
            elif "EOFError" in err_msg:
                err_msg = "EOFError: Nenhuma entrada foi fornecida (stdin vazio). Preencha o campo de Entrada Personalizada antes de executar um código que usa input()."
            else:
                # Corrige as linhas do erro subtraindo 1 devido à linha injetada
                import re
                err_msg = re.sub(
                    r'line (\d+)',
                    lambda m: f'line {int(m.group(1)) - 1}',
                    err_msg
                )

            return {
                "output": stdout_data.strip(),
                "error": err_msg,
                "execution_time_ms": round(execution_time, 2)
            }
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            return {
                "output": "",
                "error": f" Tempo limite de execução excedido ({timeout}s). Verifique se o código possui um loop infinito!",
                "execution_time_ms": round(timeout * 1000, 2)
            }
    except Exception as e:
        return {
            "output": "",
            "error": f"Erro interno de execução: {str(e)}",
            "execution_time_ms": 0.0
        }
    finally:
        # Garante a remoção do arquivo temporário
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
