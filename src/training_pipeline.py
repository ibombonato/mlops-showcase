from prefect import flow, get_run_logger


@flow(name="Testing")
def basic_flow():
    """Dummy flow for setup testing"""
    logger = get_run_logger()
    logger.warning("The fun is about to begin")


if __name__ == "__main__":
    basic_flow()
