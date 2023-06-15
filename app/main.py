import mlflow
from mlflow import MlflowClient
import traceback
import logging
from collections import defaultdict
import sys
import os
import re


def get_root_run(active_run_id=None, experiment_names=None):
    runs = mlflow.search_runs(experiment_names=experiment_names, filter_string="tags.runlevel='root'", max_results=1,
                              output_format='list')
    if len(runs):
        parent_run_id = runs[0].info.run_id
        mlflow.set_tags({'mlflow.parentRunId': parent_run_id})
        return parent_run_id
    else:
        mlflow.set_tags({'runlevel': 'root'})
        return active_run_id


def get_cmd_arg(name):
    d = defaultdict(list)
    for cmd_args in sys.argv[1:]:
        cmd_arg = cmd_args.split('=')
        if len(cmd_arg) == 2:
            d[cmd_arg[0].lstrip('-')].append(cmd_arg[1].replace('"', ''))

    if name in d:
        return str(d[name][0])
    else:
        logging.info('Unknown command line arg requested: {}'.format(name))


def get_env_var(name):
    if name in os.environ:
        value = os.environ[name]
        return int(value) if re.match("\d+$", value) else value
    else:
        logging.info('Unknown environment variable requested: {}'.format(name))


def get_cmd_arg_or_env_var(name):
    return get_cmd_arg(name) or get_env_var(name)


try:
    logging.getLogger().setLevel(logging.INFO)
    client = MlflowClient()
    git_repo = get_cmd_arg_or_env_var("git_repo")
    entry_point = get_cmd_arg_or_env_var("mlflow_entry")
    stage = get_cmd_arg_or_env_var("mlflow_stage")
    environment_name = get_cmd_arg_or_env_var("environment_name")
    experiment_name = get_cmd_arg_or_env_var('experiment_name')
    os.environ['MLFLOW_EXPERIMENT_NAME'] = experiment_name
    os.environ['MLFLOW_S3_ENDPOINT_URL'] = get_cmd_arg('mlflow_s3_uri') or get_env_var('MLFLOW_S3_ENDPOINT_URL')
    os.environ['MLFLOW_TRACKING_URI'] = get_cmd_arg('mlflow_tracking_uri') or get_env_var('MLFLOW_TRACKING_URI')

    logging.info(
        f"Printing the arguments...git_repo={git_repo},experiment_name={experiment_name},entry_point={entry_point},stage={stage}")

    with mlflow.start_run(nested=True) as active_run:
        os.environ['MLFLOW_RUN_ID'] = get_root_run(active_run_id=active_run.info.run_id, experiment_names=[experiment_name])
        submitted_run = mlflow.run(git_repo,
                                   entry_point,
                                   version=environment_name,
                                   env_manager='local',
                                   parameters={'model-stage': stage})

        submitted_run_metadata = MlflowClient().get_run(submitted_run.run_id)

        logging.info(f"Submitted Run: {submitted_run}\nSubmitted Run Metadata: {submitted_run_metadata}")

except mlflow.exceptions.RestException as e:
    logging.info('REST exception occurred (platform will retry based on pre-configured retry policy): ', exc_info=True)
    logging.info(''.join(traceback.TracebackException.from_exception(e).format()))

except mlflow.exceptions.ExecutionException as ee:
    logging.info("An ExecutionException occurred...", exc_info=True)
    logging.info(str(ee))
    logging.info(''.join(traceback.TracebackException.from_exception(ee).format()))

except BaseException as be:
    logging.info("An unexpected error occurred...", exc_info=True)
    logging.info(str(be))
    logging.info(traceback.format_exc())
    logging.info(''.join(traceback.TracebackException.from_exception(be).format()))

logging.info("End script.")
