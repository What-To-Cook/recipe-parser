import socket
import time
from enum import Enum
from typing import (
    Any,
    Generator,
    List,
    Optional,
)

import requests
import socks
from loguru import logger
from stem import Signal
from stem.control import Controller


class StepResult(Enum):
    OK = 0
    ERROR = 1


def _setup(
    controller: Controller,
    proxy_port: int,
) -> None:
    controller.authenticate()
    socks.setdefaultproxy(
        socks.PROXY_TYPE_SOCKS5,
        '127.0.0.1',
        proxy_port,
    )
    socket.socket = socks.socksocket  # type: ignore


def run_with_proxy(  # noqa: WPS231
    gen: Generator[Any, Optional[StepResult], None],
    controller_port: int = 9151,
    proxy_port: int = 9150,
) -> List[Any]:
    n_errors = 0
    gen_results = []

    with Controller.from_port(port=controller_port) as controller:
        _setup(
            controller,
            proxy_port,
        )

        step_res = None

        while True:
            try:
                gen_results.append(gen.send(step_res))  # TODO: do we really need to send certain values?
            except requests.HTTPError:
                logger.error('could not reach specified URL')
                step_res = StepResult.ERROR
                n_errors += 1
            except StopIteration:
                break
            else:
                step_res = StepResult.OK
                controller.signal(Signal.NEWNYM)
                time.sleep(controller.get_newnym_wait())

    logger.debug(f'got {n_errors} errors')

    return gen_results
