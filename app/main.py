import mlflow
import logging
from mlflow import MlflowClient
import traceback
import utils
import os

try:
    logging.getLogger().setLevel(logging.INFO)
    git_repo = utils.get_cmd_arg("git_repo")
    experiment_name = utils.get_cmd_arg("experiment_name")
    entry_point = utils.get_cmd_arg("mlflow_entry")
    stage = utils.get_cmd_arg("mlflow_stage")

    os.environ['MLFLOW_EXPERIMENT_NAME'] = experiment_name

    logging.info(f"Printing arguments...git_repo={git_repo},experiment_name={experiment_name},entry_point={entry_point},stage={stage}")

    with mlflow.start_run(run_name='start', nested=True) as active_run:

        submitted_run = mlflow.run(git_repo,
                                   entry_point,
                                   version='main' if stage == 'None' else stage.lower(),
                                   env_manager='local',
                                   parameters={'model-stage': stage})

        submitted_run_metadata = MlflowClient().get_run(submitted_run.run_id)

        logging.info(f"Submitted Run: {submitted_run}\nSubmitted Run Metadata: {submitted_run_metadata}")

except mlflow.exceptions.RestException as e:
    logging.info('REST exception occurred (platform will retry based on pre-configured retry policy): ', exc_info=True)
    traceback.print_exc()

except mlflow.exceptions.ExecutionException as ee:
    logging.info("An ExecutionException occurred...", exc_info=True)
    logging.info(str(ee))
    traceback.print_exc()

except BaseException as be:
    logging.info("An unexpected error occurred...", exc_info=True)
    logging.info(str(be))
    traceback.print_exc()

logging.info("End script.")
