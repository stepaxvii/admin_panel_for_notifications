import logging


def disable_aiogram_logs() -> None:
    for name in ["aiogram.middlewares", "aiogram.event", "aiohttp.access"]:
        logging.getLogger(name).setLevel(logging.WARNING)


def setup_logger(level: int = logging.INFO, log_file: str = "logs.log") -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s | %(name)s: %(message)s",
        datefmt="[%H:%M:%S]",
        level=level,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
