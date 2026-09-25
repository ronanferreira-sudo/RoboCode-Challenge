import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import engine, Base, get_db, DATABASE_URL
from app.models import User, Activity, TestCase, Submission, UserProgress, Classroom
from app import schemas, auth, evaluator, seed_data

# Validação e migração automática de colunas para SQLite local
if DATABASE_URL.startswith("sqlite"):
    try:
        db_file = DATABASE_URL.replace("sqlite:///", "")
        if os.path.exists(db_file):
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(users)")
            columns = [c[1] for c in cursor.fetchall()]
            if "is_admin" not in columns and len(columns) > 0:
                cursor.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                conn.commit()
            if "username" not in columns and len(columns) > 0:
                cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR(100)")
                if "email" in columns:
                    cursor.execute("UPDATE users SET username = email WHERE username IS NULL")
                else:
                    cursor.execute("UPDATE users SET username = 'admin' WHERE username IS NULL")
                conn.commit()
            if "classroom_id" not in columns and len(columns) > 0:
                cursor.execute("ALTER TABLE users ADD COLUMN classroom_id INTEGER REFERENCES classrooms(id)")
                conn.commit()
            
            cursor.execute("PRAGMA table_info(activities)")
            act_columns = [c[1] for c in cursor.fetchall()]
            if "solution_code" not in act_columns and len(act_columns) > 0:
                cursor.execute("ALTER TABLE activities ADD COLUMN solution_code TEXT")
                conn.commit()

            conn.close()
    except Exception as e:
        print(f"[AVISO] Migração SQLite: {e}")


import difflib
import re

def normalize_output(text: str) -> str:
    if not text:
        return ""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").strip().split("\n")]
    return "\n".join(lines)

def is_lenient_match(actual: str, expected: str) -> bool:
    if not actual and not expected: return True
    if not actual or not expected: return False
    
    actual_norm = re.sub(r'[^\w\s]', '', actual).strip().lower()
    expected_norm = re.sub(r'[^\w\s]', '', expected).strip().lower()
    
    actual_norm = re.sub(r'\s+', ' ', actual_norm)
    expected_norm = re.sub(r'\s+', ' ', expected_norm)
    
    if actual_norm == expected_norm: return True
    
    nums_actual = re.findall(r'\d+', actual)
    nums_expected = re.findall(r'\d+', expected)
    if nums_actual != nums_expected: return False
    
    critical_words = ['aprovado', 'reprovado', 'true', 'false']
    for word in critical_words:
        if (word in expected_norm) != (word in actual_norm): return False
        
    actual_clean = re.sub(r'\s+', '', actual_norm)
    expected_clean = re.sub(r'\s+', '', expected_norm)
    
    if actual_clean == expected_clean: return True
    
    return difflib.SequenceMatcher(None, actual_clean, expected_clean).ratio() >= 0.80

# Criação das tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Inicia semente de atividades
with next(get_db()) as db:
    seed_data.seed_initial_activities(db)

app = FastAPI(
    title="RoboCode Challenge API",
    description="Plataforma Gamificada de Aprendizado de Python com Painel de Administrador",
    version="1.1.0"
)

# Habilita CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios estáticos
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)

def build_user_response(user: User) -> schemas.UserResponse:
    """Monta UserResponse incluindo nome/código da turma, se houver."""
    return schemas.UserResponse(
        id=user.id,
        username=user.username,
        name=user.name,
        email=user.email,
        avatar=user.avatar,
        xp=user.xp,
        level=user.level,
        is_admin=user.is_admin,
        classroom_id=user.classroom_id,
        classroom_name=user.classroom.name if user.classroom else None,
        classroom_code=user.classroom.code if user.classroom else None,
        created_at=user.created_at,
    )

# -------------------------------------------------------------------
# ROTAS DE AUTENTICAÇÃO
# -------------------------------------------------------------------
@app.post("/api/auth/register", response_model=dict)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Este nome de usuário já está cadastrado no RoboCode!")

    # Valida turma, se fornecida
    classroom = None
    if user_in.classroom_id:
        classroom = db.query(Classroom).filter(Classroom.id == user_in.classroom_id).first()
        if not classroom:
            raise HTTPException(status_code=400, detail="Turma não encontrada!")

    # Se for o primeiro usuário cadastrado no banco, define como Administrador automaticamente
    is_first_user = db.query(User).count() == 0

    user = User(
        username=user_in.username,
        name=user_in.username,
        email=f"{user_in.username}@robocode.local",
        password_hash=auth.hash_password(user_in.password),
        avatar=user_in.avatar or "robot-cyber",
        xp=0,
        level=1,
        is_admin=is_first_user,
        classroom_id=user_in.classroom_id if not is_first_user else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user)
    }

@app.post("/api/auth/login", response_model=dict)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.username)
    ).first()
    if not user or not auth.verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos!")

    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user)
    }

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(auth.get_current_user)):
    return build_user_response(current_user)

@app.put("/api/auth/update", response_model=dict)
def update_user_data(user_in: schemas.UserUpdate, db: Session = Depends(get_db)):
    """Permite ao usuário alterar sua senha, avatar e/ou turma usando as credenciais atuais."""
    user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.username)
    ).first()
    if not user or not auth.verify_password(user_in.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha atual incorretos!")

    if user_in.new_password:
        user.password_hash = auth.hash_password(user_in.new_password)

    if user_in.avatar:
        user.avatar = user_in.avatar

    if user_in.classroom_id is not None:
        classroom = db.query(Classroom).filter(Classroom.id == user_in.classroom_id).first()
        if not classroom:
            raise HTTPException(status_code=400, detail="Turma não encontrada!")
        user.classroom_id = user_in.classroom_id

    db.commit()
    db.refresh(user)

    access_token = auth.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": build_user_response(user)
    }


# -------------------------------------------------------------------
# ROTAS DE ATIVIDADES / FASES (ALUNO)
# -------------------------------------------------------------------
@app.get("/api/activities", response_model=List[schemas.ActivityResponse])
def get_activities(current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    activities = db.query(Activity).order_by(Activity.phase.asc(), Activity.id.asc()).all()
    
    completed_ids = set(
        up.activity_id for up in db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.completed == True
        ).all()
    )

    result = []
    for act in activities:
        act_dict = schemas.ActivityResponse.from_orm(act)
        act_dict.completed = act.id in completed_ids
        result.append(act_dict)

    return result

@app.get("/api/activities/{activity_id}", response_model=schemas.ActivityDetailResponse)
def get_activity_detail(activity_id: int, current_user: User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    public_test_cases = [tc for tc in activity.test_cases if not tc.is_hidden]

    completed = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.activity_id == activity_id,
        UserProgress.completed == True
    ).first() is not None

    response = schemas.ActivityDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        completed=completed,
        test_cases=[schemas.TestCaseSchema.from_orm(tc) for tc in public_test_cases]
    )
    return response

# -------------------------------------------------------------------
# ROTAS DE TURMAS (CLASSROOMS)
# -------------------------------------------------------------------
@app.get("/api/classrooms", response_model=List[schemas.ClassroomResponse])
def list_classrooms(db: Session = Depends(get_db)):
    """Lista pública de turmas — usada no formulário de cadastro do aluno."""
    classrooms = db.query(Classroom).order_by(Classroom.name.asc()).all()
    result = []
    for c in classrooms:
        student_count = db.query(User).filter(User.classroom_id == c.id, User.is_admin == False).count()
        result.append(schemas.ClassroomResponse(
            id=c.id,
            name=c.name,
            code=c.code,
            description=c.description,
            student_count=student_count,
        ))
    return result

@app.post("/api/admin/classrooms", response_model=schemas.ClassroomResponse)
def create_classroom(
    cls_in: schemas.ClassroomCreate,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    existing = db.query(Classroom).filter(Classroom.code == cls_in.code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe uma turma com este código!")
    classroom = Classroom(name=cls_in.name, code=cls_in.code, description=cls_in.description)
    db.add(classroom)
    db.commit()
    db.refresh(classroom)
    return schemas.ClassroomResponse(id=classroom.id, name=classroom.name, code=classroom.code, description=classroom.description, student_count=0)

@app.put("/api/admin/classrooms/{classroom_id}", response_model=schemas.ClassroomResponse)
def update_classroom(
    classroom_id: int,
    cls_in: schemas.ClassroomUpdate,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Turma não encontrada!")
    if cls_in.name is not None:
        classroom.name = cls_in.name
    if cls_in.code is not None:
        existing = db.query(Classroom).filter(Classroom.code == cls_in.code, Classroom.id != classroom_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Já existe uma turma com este código!")
        classroom.code = cls_in.code
    if cls_in.description is not None:
        classroom.description = cls_in.description
    db.commit()
    db.refresh(classroom)
    student_count = db.query(User).filter(User.classroom_id == classroom.id, User.is_admin == False).count()
    return schemas.ClassroomResponse(id=classroom.id, name=classroom.name, code=classroom.code, description=classroom.description, student_count=student_count)

@app.delete("/api/admin/classrooms/{classroom_id}")
def delete_classroom(
    classroom_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    classroom = db.query(Classroom).filter(Classroom.id == classroom_id).first()
    if not classroom:
        raise HTTPException(status_code=404, detail="Turma não encontrada!")
    # Desvincula alunos da turma antes de excluir
    db.query(User).filter(User.classroom_id == classroom_id).update({"classroom_id": None})
    db.delete(classroom)
    db.commit()
    return {"message": "Turma removida com sucesso! Os alunos vinculados foram desvinculados."}

# -------------------------------------------------------------------
# ROTAS DE ADMINISTRAÇÃO (GERENCIAMENTO DE ATIVIDADES E PONTUAÇÃO)
# -------------------------------------------------------------------
@app.get("/api/admin/network-info")
def get_network_info(admin: User = Depends(auth.get_current_admin)):
    import socket
    local_ip = "127.0.0.1"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass
    return {
        "local_ip": local_ip,
        "port": 8000,
        "student_url": f"http://{local_ip}:8000",
        "localhost_url": "http://127.0.0.1:8000"
    }
@app.post("/api/admin/activities", response_model=schemas.ActivityAdminDetailResponse)
def create_activity(
    act_in: schemas.ActivityCreate,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = Activity(
        phase=act_in.phase,
        title=act_in.title,
        description=act_in.description,
        difficulty=act_in.difficulty,
        xp_reward=act_in.xp_reward,
        initial_code=act_in.initial_code or "# Escreva seu código em Python aqui\n",
        solution_code=act_in.solution_code
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    if activity.solution_code:
        sol_eval = evaluator.execute_python_code(activity.solution_code, "")
        if not sol_eval["error"]:
            tc = TestCase(
                activity_id=activity.id,
                input_data="",
                expected_output=sol_eval["output"],
                is_hidden=False
            )
            db.add(tc)
            db.commit()
            db.refresh(activity)

    return schemas.ActivityAdminDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        solution_code=activity.solution_code,
        completed=False,
        test_cases=[schemas.TestCaseSchema.from_orm(tc) for tc in activity.test_cases]
    )

@app.get("/api/admin/activities/{activity_id}/full", response_model=schemas.ActivityAdminDetailResponse)
def get_activity_admin_detail(
    activity_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    return schemas.ActivityAdminDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        solution_code=activity.solution_code,
        completed=False,
        test_cases=[schemas.TestCaseSchema.from_orm(tc) for tc in activity.test_cases]
    )

@app.put("/api/admin/activities/{activity_id}", response_model=schemas.ActivityAdminDetailResponse)
def update_activity(
    activity_id: int,
    act_in: schemas.ActivityUpdate,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    if act_in.phase is not None:
        activity.phase = act_in.phase
    if act_in.title is not None:
        activity.title = act_in.title
    if act_in.description is not None:
        activity.description = act_in.description
    if act_in.difficulty is not None:
        activity.difficulty = act_in.difficulty
    if act_in.xp_reward is not None:
        activity.xp_reward = act_in.xp_reward
    if act_in.initial_code is not None:
        activity.initial_code = act_in.initial_code
    if act_in.solution_code is not None:
        activity.solution_code = act_in.solution_code

    if activity.solution_code and len(activity.test_cases) == 0:
        sol_eval = evaluator.execute_python_code(activity.solution_code, "")
        if not sol_eval["error"]:
            tc = TestCase(
                activity_id=activity.id,
                input_data="",
                expected_output=sol_eval["output"],
                is_hidden=False
            )
            db.add(tc)
            db.commit()
            db.refresh(activity)

    return schemas.ActivityAdminDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        solution_code=activity.solution_code,
        completed=False,
        test_cases=[schemas.TestCaseSchema.from_orm(tc) for tc in activity.test_cases]
    )

@app.delete("/api/admin/activities/{activity_id}")
def delete_activity(
    activity_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    db.delete(activity)
    db.commit()
    return {"message": "Atividade removida com sucesso!"}

@app.post("/api/admin/activities/{activity_id}/test-cases", response_model=schemas.TestCaseSchema)
def add_test_case(
    activity_id: int,
    tc_in: schemas.TestCaseCreate,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    tc = TestCase(
        activity_id=activity.id,
        input_data=tc_in.input_data or "",
        expected_output=tc_in.expected_output,
        is_hidden=tc_in.is_hidden or False
    )
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc

@app.delete("/api/admin/test-cases/{test_case_id}")
def delete_test_case(
    test_case_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    tc = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not tc:
        raise HTTPException(status_code=404, detail="Caso de teste não encontrado!")

    db.delete(tc)
    db.commit()
    return {"message": "Caso de teste removido com sucesso!"}

@app.post("/api/admin/activities/{activity_id}/test-solution")
def test_activity_solution(
    activity_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")
    if not activity.solution_code:
        raise HTTPException(status_code=400, detail="Esta atividade não possui um Código Gabarito de referência cadastrado!")

    test_cases = db.query(TestCase).filter(TestCase.activity_id == activity_id).all()
    if not test_cases:
        eval_res = evaluator.execute_python_code(activity.solution_code, "")
        passed = not eval_res["error"]
        return {
            "passed": passed,
            "message": "⚡ Código Gabarito executado com SUCESSO sem erros!" if passed else f"❌ Erro ao executar Código Gabarito: {eval_res['error']}",
            "results": [{
                "test_case_id": 0,
                "passed": passed,
                "input_data": "",
                "expected_output": eval_res["output"],
                "actual_output": eval_res["output"],
                "error": eval_res["error"]
            }]
        }

    all_passed = True
    results = []
    for tc in test_cases:
        eval_res = evaluator.execute_python_code(activity.solution_code, tc.input_data or "")
        actual_output = normalize_output(eval_res["output"])
        expected_output = normalize_output(tc.expected_output)
        passed = is_lenient_match(actual_output, expected_output) and not eval_res["error"]
        if not passed:
            all_passed = False
        results.append({
            "test_case_id": tc.id,
            "passed": passed,
            "input_data": tc.input_data,
            "expected_output": expected_output,
            "actual_output": actual_output,
            "error": eval_res["error"]
        })

    msg = "⚡ Gabarito APROVADO! O código de solução passou em todos os casos de teste." if all_passed else "❌ Gabarito REPROVADO! O código de solução falhou em alguns testes."
    return {
        "passed": all_passed,
        "message": msg,
        "results": results
    }

@app.post("/api/admin/generate-output")
def generate_output_from_code(
    req: schemas.GenerateOutputRequest,
    admin: User = Depends(auth.get_current_admin)
):
    if not req.code:
        raise HTTPException(status_code=400, detail="Código não fornecido!")
    res = evaluator.execute_python_code(req.code, req.input_data or "")
    if res["error"]:
        raise HTTPException(status_code=400, detail=f"Erro ao executar código gabarito: {res['error']}")
    return {"output": res["output"]}

# -------------------------------------------------------------------
# EXECUÇÃO E TESTE DE CÓDIGO (SANDBOX)
# -------------------------------------------------------------------
@app.post("/api/activities/run", response_model=schemas.CodeRunResult)
def run_code(req: schemas.CodeRunRequest, current_user: User = Depends(auth.get_current_user)):
    res = evaluator.execute_python_code(req.code, req.input_data or "")
    return schemas.CodeRunResult(
        output=res["output"],
        error=res["error"],
        execution_time_ms=res["execution_time_ms"]
    )

@app.post("/api/activities/submit", response_model=schemas.CodeSubmissionResponse)
def submit_activity(
    req: schemas.CodeSubmissionRequest,
    current_user: User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == req.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    test_cases = db.query(TestCase).filter(TestCase.activity_id == req.activity_id).all()
    if not test_cases:
        if activity.solution_code:
            sol_eval = evaluator.execute_python_code(activity.solution_code, "")
            if not sol_eval["error"]:
                tc_auto = TestCase(
                    activity_id=activity.id,
                    input_data="",
                    expected_output=sol_eval["output"],
                    is_hidden=False
                )
                db.add(tc_auto)
                db.commit()
                test_cases = [tc_auto]
            else:
                raise HTTPException(status_code=400, detail=f"Erro ao executar o código gabarito da atividade: {sol_eval['error']}")
        else:
            raise HTTPException(status_code=400, detail="Esta atividade não possui casos de teste nem Código Gabarito cadastrados!")

    all_passed = True
    test_results = []
    total_exec_time = 0.0

    for tc in test_cases:
        eval_res = evaluator.execute_python_code(req.code, tc.input_data or "")
        total_exec_time += eval_res["execution_time_ms"]
        
        actual_output = normalize_output(eval_res["output"])
        expected_output = normalize_output(tc.expected_output)
        passed = is_lenient_match(actual_output, expected_output) and not eval_res["error"]

        if not passed:
            all_passed = False

        test_results.append(schemas.TestResultDetail(
            test_case_id=tc.id,
            passed=passed,
            input_data=tc.input_data if not tc.is_hidden else "[Teste Oculto]",
            expected_output=expected_output if not tc.is_hidden else "[Teste Oculto]",
            actual_output=actual_output if not tc.is_hidden or passed else "[Saída Incorreta]",
            error=eval_res["error"]
        ))

    submission_status = "PASSED" if all_passed else "FAILED"
    submission = Submission(
        user_id=current_user.id,
        activity_id=activity.id,
        code=req.code,
        status=submission_status,
        execution_time_ms=round(total_exec_time, 2)
    )
    db.add(submission)

    xp_gained = 0
    leveled_up = False
    is_auto_passed = False

    already_completed = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.activity_id == activity.id,
        UserProgress.completed == True
    ).first()

    if not already_completed:
        if all_passed:
            progress = UserProgress(
                user_id=current_user.id,
                activity_id=activity.id,
                completed=True
            )
            db.add(progress)

            xp_gained = activity.xp_reward
            current_user.xp += xp_gained
        else:
            current_user.xp = max(0, current_user.xp - 10)
            xp_gained = -10
            
            failed_count = db.query(Submission).filter(
                Submission.user_id == current_user.id,
                Submission.activity_id == activity.id,
                Submission.status == "FAILED"
            ).count() + 1
            
            if failed_count >= 3:
                progress = UserProgress(
                    user_id=current_user.id,
                    activity_id=activity.id,
                    completed=True
                )
                db.add(progress)
                is_auto_passed = True
                xp_gained = 0

        new_calc_level = (current_user.xp // 100) + 1
        if new_calc_level > current_user.level:
            current_user.level = new_calc_level
            leveled_up = True
        elif new_calc_level < current_user.level:
            current_user.level = max(1, new_calc_level)

        db.commit()
        db.refresh(current_user)
    else:
        db.commit()

    if is_auto_passed:
        message = "⚠️ Você errou 3 vezes. A fase foi liberada automaticamente, mas você não ganhou pontos!"
        submission_passed = True
    elif all_passed:
        message = "⚡ PARABÉNS! Todos os casos de teste passaram!"
        submission_passed = True
    else:
        message = "❌ Alguns testes falharam. Você perdeu 10 XP. Revise e tente novamente!"
        submission_passed = False

    return schemas.CodeSubmissionResponse(
        passed=submission_passed,
        message=message,
        xp_gained=xp_gained,
        leveled_up=leveled_up,
        new_level=current_user.level,
        new_xp=current_user.xp,
        results=test_results
    )

# -------------------------------------------------------------------
# RANKING / LEADERBOARD
# -------------------------------------------------------------------
@app.get("/api/leaderboard", response_model=List[schemas.LeaderboardEntry])
def get_leaderboard(
    classroom_id: Optional[int] = Query(None), 
    db: Session = Depends(get_db),
    current_user: User = Depends(auth.get_current_user)
):
    query = db.query(User).filter(User.is_admin == False)
    
    # Se o usuário NÃO for admin, forçamos o filtro para a turma dele.
    # Se ele for admin, permitimos usar o filtro 'classroom_id' passado na requisição.
    if not current_user.is_admin:
        query = query.filter(User.classroom_id == current_user.classroom_id)
    elif classroom_id is not None:
        query = query.filter(User.classroom_id == classroom_id)
        
    students = query.order_by(User.xp.desc(), User.level.desc(), User.id.asc()).all()
    
    leaderboard = []
    for index, user in enumerate(students):
        completed_count = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.completed == True
        ).count()

        leaderboard.append(schemas.LeaderboardEntry(
            rank=index + 1,
            user_id=user.id,
            name=user.username or user.name or f"User #{user.id}",
            avatar=user.avatar,
            level=user.level,
            xp=user.xp,
            activities_completed=completed_count,
            classroom_id=user.classroom_id,
            classroom_name=user.classroom.name if user.classroom else None,
            classroom_code=user.classroom.code if user.classroom else None,
        ))

    return leaderboard

# -------------------------------------------------------------------
# ROTA PRINCIPAL DA SPA (FRONTEND)
# -------------------------------------------------------------------
@app.get("/{full_path:path}", response_class=HTMLResponse)
def serve_spa(full_path: str):
    index_path = os.path.join(templates_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>RoboCode Challenge Iniciado! Frontend carregando...</h1>")
