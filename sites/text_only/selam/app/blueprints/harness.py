from __future__ import annotations

from flask import Blueprint, current_app, jsonify

from .. import db as database
from ..routes_map import SLUGS

bp = Blueprint("harness", __name__)


@bp.post(SLUGS["reset"])
def reset():
    config = current_app.config["SELAM"]
    digest = database.reset(config.seed_db, config.db_path, config.generated_dir)
    return jsonify(status="ok", seed_hash=digest)


@bp.get(SLUGS["reset_status"])
def reset_status():
    config = current_app.config["SELAM"]
    return jsonify(
        seed_hash=database.seed_hash(config.seed_db),
        live_hash=database.seed_hash(config.db_path),
        clean=database.seed_hash(config.seed_db) == database.seed_hash(config.db_path),
    )
