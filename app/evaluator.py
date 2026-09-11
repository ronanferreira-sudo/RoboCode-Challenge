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
    
    # Cria um arquivo temporário com o código do aluno
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(code)
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

            return {
                "output": stdout_data.strip(),
                "error": stderr_data.strip() if stderr_data else None,
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
