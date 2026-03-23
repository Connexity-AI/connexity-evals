from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app import crud
from app.core.config import settings
from app.models import (
    AgentCreate,
    Difficulty,
    RunCreate,
    RunStatus,
    RunUpdate,
    ScenarioCreate,
    ScenarioResultCreate,
    ScenarioResultUpdate,
    ScenarioSetCreate,
    ScenarioStatus,
    SimulationMode,
    UserCreate,
)

if not settings.SQLALCHEMY_DATABASE_URI:
    raise RuntimeError("DATABASE_URL or POSTGRES_* env vars must be configured")
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # Wipe everything
    truncate_all_tables(session)

    # Seed one superuser
    # Credentials come from .env — defaults: admin@example.com / password
    user_in = UserCreate(
        email=settings.FIRST_SUPERUSER,
        password=settings.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
        full_name="Admin",
    )
    crud.create_user(session=session, user_create=user_in)

    # Seed eval-domain entities
    _seed_eval_data(session)

    session.commit()


def _seed_eval_data(session: Session) -> None:
    """Seed eval-domain entities for dev/testing."""
    # Agents
    agent_cs = crud.create_agent(
        session=session,
        agent_in=AgentCreate(
            name="Customer Support Bot",
            description="Handles billing inquiries and account issues",
            endpoint_url="http://localhost:8081/agent",
            agent_metadata={"model": "claude-3-5-sonnet", "version": "1.0"},
        ),
    )
    agent_sales = crud.create_agent(
        session=session,
        agent_in=AgentCreate(
            name="Sales Assistant",
            description="Qualifies leads and answers product questions",
            endpoint_url="http://localhost:8082/agent",
            agent_metadata={"model": "gpt-4o", "version": "2.1"},
        ),
    )

    # Scenarios
    s_refund = crud.create_scenario(
        session=session,
        scenario_in=ScenarioCreate(
            name="Refund Request — Valid",
            description="Customer requests refund within 30-day window",
            difficulty=Difficulty.NORMAL,
            tags=["billing", "refund", "happy-path"],
            status=ScenarioStatus.ACTIVE,
            simulation_mode=SimulationMode.LLM_DRIVEN,
            user_persona="Polite customer, purchased 5 days ago",
            user_goal="Get a full refund on recent purchase",
            max_turns=10,
        ),
    )
    s_escalation = crud.create_scenario(
        session=session,
        scenario_in=ScenarioCreate(
            name="Angry Escalation",
            description="Customer is frustrated after multiple failed attempts",
            difficulty=Difficulty.HARD,
            tags=["billing", "escalation", "edge-case"],
            status=ScenarioStatus.ACTIVE,
            simulation_mode=SimulationMode.LLM_DRIVEN,
            user_persona="Frustrated customer, 3 prior contacts",
            user_goal="Speak to a supervisor and get compensation",
            max_turns=15,
        ),
    )
    s_product = crud.create_scenario(
        session=session,
        scenario_in=ScenarioCreate(
            name="Product Comparison",
            description="Customer asks for a comparison between two products",
            difficulty=Difficulty.NORMAL,
            tags=["sales", "product-info"],
            status=ScenarioStatus.ACTIVE,
            simulation_mode=SimulationMode.LLM_DRIVEN,
            user_persona="Budget-conscious shopper",
            user_goal="Decide between Plan A and Plan B",
            max_turns=10,
        ),
    )
    crud.create_scenario(
        session=session,
        scenario_in=ScenarioCreate(
            name="Draft Scenario — WIP",
            description="Not yet ready for evaluation",
            difficulty=Difficulty.NORMAL,
            tags=["draft"],
            status=ScenarioStatus.DRAFT,
        ),
    )
    crud.create_scenario(
        session=session,
        scenario_in=ScenarioCreate(
            name="Archived Legacy Scenario",
            description="Deprecated scenario from v0",
            difficulty=Difficulty.HARD,
            tags=["legacy", "archived"],
            status=ScenarioStatus.ARCHIVED,
        ),
    )

    # Scenario Sets
    billing_set = crud.create_scenario_set(
        session=session,
        scenario_set_in=ScenarioSetCreate(
            name="Billing Scenarios v1",
            description="Core billing test suite",
            scenario_ids=[s_refund.id, s_escalation.id],
        ),
    )
    sales_set = crud.create_scenario_set(
        session=session,
        scenario_set_in=ScenarioSetCreate(
            name="Sales Scenarios v1",
            description="Sales qualification test suite",
            scenario_ids=[s_product.id],
        ),
    )

    # Runs
    run_completed = crud.create_run(
        session=session,
        run_in=RunCreate(
            name="Billing Eval — Completed",
            agent_id=agent_cs.id,
            agent_endpoint_url=agent_cs.endpoint_url,
            scenario_set_id=billing_set.id,
        ),
    )
    crud.update_run(
        session=session,
        db_run=run_completed,
        run_in=RunUpdate(status=RunStatus.COMPLETED),
    )

    _run_pending = crud.create_run(
        session=session,
        run_in=RunCreate(
            name="Sales Eval — Pending",
            agent_id=agent_sales.id,
            agent_endpoint_url=agent_sales.endpoint_url,
            scenario_set_id=sales_set.id,
        ),
    )

    run_failed = crud.create_run(
        session=session,
        run_in=RunCreate(
            name="Billing Eval — Failed",
            agent_id=agent_cs.id,
            agent_endpoint_url=agent_cs.endpoint_url,
            scenario_set_id=billing_set.id,
        ),
    )
    crud.update_run(
        session=session,
        db_run=run_failed,
        run_in=RunUpdate(status=RunStatus.FAILED),
    )

    # Scenario Results for the completed run
    result_refund = crud.create_scenario_result(
        session=session,
        result_in=ScenarioResultCreate(
            run_id=run_completed.id,
            scenario_id=s_refund.id,
        ),
    )
    crud.update_scenario_result(
        session=session,
        db_result=result_refund,
        result_in=ScenarioResultUpdate(
            passed=True,
            turn_count=6,
            total_latency_ms=4500,
        ),
    )

    result_escalation = crud.create_scenario_result(
        session=session,
        result_in=ScenarioResultCreate(
            run_id=run_completed.id,
            scenario_id=s_escalation.id,
        ),
    )
    crud.update_scenario_result(
        session=session,
        db_result=result_escalation,
        result_in=ScenarioResultUpdate(
            passed=False,
            turn_count=12,
            total_latency_ms=9800,
            error_message="Agent failed to transfer to supervisor",
        ),
    )


def truncate_all_tables(session: Session) -> None:
    """
    Truncate all SQLModel tables dynamically.
    """
    table_names = ", ".join(
        f'"{table.name}"' for table in SQLModel.metadata.sorted_tables
    )

    session.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE;"))
    session.commit()
