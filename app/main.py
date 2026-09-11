import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import engine, Base, get_db, DATABASE_URL
from app.models import User, Activity, TestCase, Submission, UserProgress
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
            conn.close()
    except Exception as e:
        print(f"[AVISO] Migração SQLite: {e}")

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

# -------------------------------------------------------------------
# ROTAS DE AUTENTICAÇÃO
# -------------------------------------------------------------------
@app.post("/api/auth/register", response_model=dict)
def register(user_in: schemas.UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Este e-mail já está cadastrado no RoboCode!")

    # Se for o primeiro usuário cadastrado no banco, define como Administrador automaticamente
    is_first_user = db.query(User).count() == 0

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=auth.hash_password(user_in.password),
        avatar=user_in.avatar or "robot-cyber",
        xp=0,
        level=1,
        is_admin=is_first_user
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = auth.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.from_orm(user)
    }

@app.post("/api/auth/login", response_model=dict)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not auth.verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos!")

    access_token = auth.create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.UserResponse.from_orm(user)
    }

@app.get("/api/auth/me", response_model=schemas.UserResponse)
def get_me(current_user: User = Depends(auth.get_current_user)):
    return current_user

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
# ROTAS DE ADMINISTRAÇÃO (GERENCIAMENTO DE ATIVIDADES E PONTUAÇÃO)
# -------------------------------------------------------------------
@app.post("/api/admin/activities", response_model=schemas.ActivityDetailResponse)
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
        initial_code=act_in.initial_code or "# Escreva seu código em Python aqui\n"
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    return schemas.ActivityDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        completed=False,
        test_cases=[]
    )

@app.get("/api/admin/activities/{activity_id}/full", response_model=schemas.ActivityDetailResponse)
def get_activity_admin_detail(
    activity_id: int,
    admin: User = Depends(auth.get_current_admin),
    db: Session = Depends(get_db)
):
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Atividade não encontrada!")

    return schemas.ActivityDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
        completed=False,
        test_cases=[schemas.TestCaseSchema.from_orm(tc) for tc in activity.test_cases]
    )

@app.put("/api/admin/activities/{activity_id}", response_model=schemas.ActivityDetailResponse)
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

    db.commit()
    db.refresh(activity)

    return schemas.ActivityDetailResponse(
        id=activity.id,
        phase=activity.phase,
        title=activity.title,
        description=activity.description,
        difficulty=activity.difficulty,
        xp_reward=activity.xp_reward,
        initial_code=activity.initial_code,
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
        raise HTTPException(status_code=400, detail="Esta atividade não possui casos de teste cadastrados pelo Administrador!")

    all_passed = True
    test_results = []
    total_exec_time = 0.0

    for tc in test_cases:
        eval_res = evaluator.execute_python_code(req.code, tc.input_data or "")
        total_exec_time += eval_res["execution_time_ms"]
        
        actual_output = eval_res["output"].strip()
        expected_output = tc.expected_output.strip()
        passed = (actual_output == expected_output) and (eval_res["error"] is None)

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

    if all_passed:
        already_completed = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.activity_id == activity.id,
            UserProgress.completed == True
        ).first()

        if not already_completed:
            progress = UserProgress(
                user_id=current_user.id,
                activity_id=activity.id,
                completed=True
            )
            db.add(progress)

            xp_gained = activity.xp_reward
            current_user.xp += xp_gained
            new_calc_level = (current_user.xp // 100) + 1
            
            if new_calc_level > current_user.level:
                current_user.level = new_calc_level
                leveled_up = True

            db.commit()
            db.refresh(current_user)

    db.commit()

    message = "⚡ PARABÉNS! Todos os casos de teste passaram!" if all_passed else "❌ Alguns testes falharam. Revise seu código e tente novamente!"

    return schemas.CodeSubmissionResponse(
        passed=all_passed,
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
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_admin.isnot(True)).order_by(User.xp.desc(), User.level.desc(), User.id.asc()).all()
    
    leaderboard = []
    for index, user in enumerate(users):
        completed_count = db.query(UserProgress).filter(
            UserProgress.user_id == user.id,
            UserProgress.completed == True
        ).count()

        leaderboard.append(schemas.LeaderboardEntry(
            rank=index + 1,
            user_id=user.id,
            name=user.name,
            avatar=user.avatar,
            level=user.level,
            xp=user.xp,
            activities_completed=completed_count
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
