from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from flask import Flask, current_app, g
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .services.references import AllocatingSession

EXT_KEY = "selam_db"


_ENGINES: dict[str, object] = {}


def init_app(app: Flask) -> None:
    config = app.config["SELAM"]

    stale = _ENGINES.pop(str(config.db_path), None)
    if stale is not None:
        stale.dispose()

    refresh_live_db(config.seed_db, config.db_path)
    engine = create_engine(f"sqlite:///{config.db_path}", future=True)
    _ENGINES[str(config.db_path)] = engine
    assert_schema_matches(engine, config.seed_db)
    app.extensions[EXT_KEY] = {
        "engine": engine,
        "sessionmaker": sessionmaker(bind=engine, expire_on_commit=False,
                                     class_=AllocatingSession),
    }

    app.teardown_appcontext(_close_session)


def refresh_live_db(seed_db: Path, live_db: Path) -> None:
    if not seed_db.exists():
        raise FileNotFoundError(
            f"{seed_db} is missing -- run `python seed.py` before starting the app"
        )
    live_db.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(seed_db, live_db)


def reset(seed_db: Path, live_db: Path, generated_dir: Path) -> str:
    store = current_app.extensions[EXT_KEY]
    store["engine"].dispose()

    shutil.copyfile(seed_db, live_db)

    if generated_dir.exists():
        for path in sorted(generated_dir.iterdir()):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)

    engine = create_engine(f"sqlite:///{live_db}", future=True)
    store["engine"] = engine
    store["sessionmaker"] = sessionmaker(bind=engine, expire_on_commit=False)
    return seed_hash(seed_db)


def seed_hash(seed_db: Path) -> str:
    return hashlib.sha256(seed_db.read_bytes()).hexdigest()


def session() -> Session:
    if "db_session" not in g:
        store = current_app.extensions.get(EXT_KEY)
        assert store is not None, "app.db.init_app() was not called"
        g.db_session = store["sessionmaker"]()
    return g.db_session


def _close_session(exception=None) -> None:
    db_session = g.pop("db_session", None)
    if db_session is not None:
        db_session.close()


def assert_schema_matches(engine, seed_db: Path) -> None:
    from sqlalchemy import inspect

    from .models import Base

    inspector = inspect(engine)
    present = set(inspector.get_table_names())
    expected = set(Base.metadata.tables)

    missing_tables = sorted(expected - present)
    missing_columns = []
    for name in sorted(expected & present):
        have = {c["name"] for c in inspector.get_columns(name)}
        want = {c.name for c in Base.metadata.tables[name].columns}
        for column in sorted(want - have):
            missing_columns.append(f"{name}.{column}")

    if missing_tables or missing_columns:
        detail = []
        if missing_tables:
            detail.append(f"missing tables: {missing_tables[:6]}")
        if missing_columns:
            detail.append(f"missing columns: {missing_columns[:6]}")
        raise RuntimeError(
            f"{seed_db} does not match the models in this checkout -- "
            + "; ".join(detail)
            + ". Run `python seed.py` to rebuild it, then start the server again."
        )
