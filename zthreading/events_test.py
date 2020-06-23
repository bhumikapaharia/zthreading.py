import pytest
import asyncio
import threading
import time
from src.operations import events
from src.operations.tasks import Task


def test_event_handler_event():
    hndl = events.EventHandler()
    hndl.on("test_event", lambda: print("ok"))
    hndl.emit("test_event")


def test_event_handler_args():
    hndl = events.EventHandler()

    rslt = {
        "arg": None,
        "named_arg": None,
    }

    def handler_method(arg, named_arg=None):
        rslt["arg"] = arg
        rslt["named_arg"] = named_arg

    hndl.on("test_event", handler_method)
    hndl.emit("test_event", True, named_arg=True)

    assert rslt["arg"] is True, "Arg list not passed to event"
    assert rslt["named_arg"] is True, "Named arg list not passed to event"


def test_event_handler_event_invalid_arg_list():
    hndl = events.EventHandler()
    hndl.on("test_event", lambda: print("ok"))
    with pytest.raises(Exception):
        hndl.emit("test_event", True)
    with pytest.raises(Exception):
        hndl.emit("test_event", named_arg=True)


@pytest.mark.asyncio
async def test_event_handler_event_async():
    hndl = events.AsyncEventHandler()
    hndl.on("test_event", lambda: print("ok"))
    await hndl.emit("test_event")


@pytest.mark.asyncio
async def test_event_handler_args_async():
    hndl = events.AsyncEventHandler()

    rslt = {
        "arg": None,
        "named_arg": None,
    }

    def handler_method(arg, named_arg=None):
        rslt["arg"] = arg
        rslt["named_arg"] = named_arg

    hndl.on("test_event", handler_method)
    await hndl.emit("test_event", True, named_arg=True)

    assert rslt["arg"] is True, "Arg list not passed to event"
    assert rslt["named_arg"] is True, "Named arg list not passed to event"


@pytest.mark.asyncio
async def test_event_handler_event_invalid_arg_list_async():
    hndl = events.AsyncEventHandler()
    hndl.on("test_event", lambda: print("ok"))
    with pytest.raises(Exception):
        await hndl.emit("test_event", True)
    with pytest.raises(Exception):
        await hndl.emit("test_event", named_arg=True)


def test_evennt_stream_preload():
    hndl = events.EventHandler()
    strm = hndl.stream(timeout=0.1)
    hndl.emit("test_event")
    assert strm.__next__() is not None


def test_evennt_stream_in_thread():
    hndl = events.EventHandler()

    def send_event():
        time.sleep(0.01)
        hndl.emit("test_event")

    threading.Thread(target=send_event).start()
    strm = hndl.stream(timeout=0.1)

    assert strm.__next__() is not None


@pytest.mark.asyncio
async def test_evennt_stream_preload_asyncio():
    hndl = events.EventHandler()
    strm = hndl.stream(timeout=0.1, use_async_loop=True)
    hndl.emit("test_event")
    assert await strm.__anext__() is not None


@pytest.mark.asyncio
async def test_evennt_stream_in_corutine():
    hndl = events.EventHandler()

    async def send_event():
        hndl.emit("test_event")

    asyncio.create_task(send_event())
    strm = hndl.stream(timeout=0.1, use_async_loop=True)
    await asyncio.sleep(0.01)  # allow the other task to execute.
    assert await strm.__anext__() is not None


def test_events_streams_using_threads():
    hndl = events.EventHandler()

    def do_emit():
        for i in range(0, 4):
            hndl.emit("test")
            time.sleep(0.001)
        hndl.stop_all_streams()

    event_stream = hndl.stream("test")
    Task(do_emit).start()
    col = []
    for ev in event_stream:
        col.append(ev)
    assert len(col) == 4


@pytest.mark.asyncio
async def test_evennt_stream_stop():
    hndl = events.EventHandler()

    async def send_event():
        await asyncio.sleep(0.01)
        hndl.stop_all_streams()

    # asyncio will not work here :)
    Task(send_event).start()
    strm = hndl.stream(timeout=1)

    for v in strm:
        pass


if __name__ == "__main__":
    pytest.main(["-x", __file__])
