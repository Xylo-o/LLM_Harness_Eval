from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from harness.db import Run, TestCase, Result, Score, engine

def save_run(suite_name, model_name, model_version, results):
    with Session(engine) as session:
        run = Run(suite_name=suite_name, model_name=model_name, model_version=model_version,)
        session.add(run)
        session.flush()

        for result in results:
            pass

        run.finished_at = datetime.now()
        session.commit()
        return run.id
