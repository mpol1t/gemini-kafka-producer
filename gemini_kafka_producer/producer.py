import asyncio
import logging
from asyncio import Task
from typing import Set, Any, Dict, Optional

from async_websocket_pool.websocket import connect
from gemini_public_api.api import GeminiPublicAPI


async def on_message(message: str) -> None:
    try:
        pass
    except Exception as e:
        logging.error(f"Error processing message: {e}")


async def manage_listener(symbol: str, listener: Optional[Task]) -> Optional[Task]:
    loop = asyncio.get_event_loop()

    # Run the blocking method in executor
    blocking_details_future = loop.run_in_executor(None, GeminiPublicAPI.get_symbol_details, symbol)
    # Convert concurrent.futures.Future to asyncio.Future
    details: Dict[str, Any] = await asyncio.ensure_future(blocking_details_future)

    if 'status' in details:
        if details['status'] != 'closed' and not listener:
            logging.info(f'{symbol:20} is open, starting listener')
            listener = loop.create_task(
                connect(
                    url=f'wss://api.gemini.com/v1/marketdata/{symbol}?top_of_book=true&heartbeat=true',
                    on_message=on_message,
                    on_connect=None,
                    timeout=10
                )
            )
        elif details['status'] == 'closed' and listener:
            logging.info(f'{symbol} is closed, stopping listener')
            listener.cancel()
            await asyncio.wait_for(listener, timeout=10)
            listener = None
    else:
        logging.error(f'Invalid message format: {details}')

    return listener


async def run_listener(symbol: str, status_check_interval: int) -> None:
    listener: Optional[Task] = None
    while True:
        try:
            listener = await manage_listener(symbol, listener)
        except Exception as e:
            logging.error(f"Caught {type(e).__name__}: {str(e)}")
        finally:
            await asyncio.sleep(status_check_interval)


async def run(symbol_check_interval: int, status_check_interval: int) -> None:
    known_symbols: Set[str] = set()
    loop = asyncio.get_event_loop()

    while True:
        try:
            blocking_symbols_future = loop.run_in_executor(None, GeminiPublicAPI.get_symbols)
            symbols = await asyncio.ensure_future(blocking_symbols_future)

            for symbol in set(symbols) - known_symbols:
                loop.create_task(run_listener(symbol, status_check_interval))
                known_symbols.add(symbol)
        except Exception as e:
            logging.error(e)
        finally:
            await asyncio.sleep(symbol_check_interval)
