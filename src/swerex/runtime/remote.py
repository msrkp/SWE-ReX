import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import requests

from swerex.runtime.abstract import (
    AbstractRuntime,
    Action,
    CloseSessionRequest,
    CloseSessionResponse,
    Command,
    CommandResponse,
    CreateSessionRequest,
    CreateSessionResponse,
    IsAliveResponse,
    Observation,
    ReadFileRequest,
    ReadFileResponse,
    SweRexception,
    UploadRequest,
    UploadResponse,
    WriteFileRequest,
    WriteFileResponse,
    _ExceptionTransfer,
)
from swerex.utils.log import get_logger
from swerex.utils.wait import _wait_until_alive

__all__ = ["RemoteRuntime"]


class RemoteRuntime(AbstractRuntime):
    def __init__(self, *, host: str = "http://127.0.0.1", port: int = 8000):
        self.logger = get_logger("RR")
        if not host.startswith("http"):
            self.logger.warning("Host %s does not start with http, adding http://", host)
            host = f"http://{host}"
        self.host = host
        self.port = port

    @property
    def _api_url(self) -> str:
        return f"{self.host}:{self.port}"

    def _handle_transfer_exception(self, exc_transfer: _ExceptionTransfer):
        if exc_transfer.traceback:
            self.logger.debug("Traceback: %s", exc_transfer.traceback)
        try:
            module, _, exc_name = exc_transfer.class_path.rpartition(".")
            exception = getattr(sys.modules[module], exc_name)
        except AttributeError:
            self.logger.error(f"Unknown exception class: {exc_transfer.class_path!r}")
            raise SweRexception(exc_transfer.message) from None
        raise exception(exc_transfer.message) from None

    def _handle_response_errors(self, response: requests.Response):
        if response.status_code == 511:
            exc_transfer = _ExceptionTransfer(**response.json()["swerexception"])
            self._handle_transfer_exception(exc_transfer)
        response.raise_for_status()

    async def is_alive(self, *, timeout: float | None = None) -> IsAliveResponse:
        """Checks if the runtime is alive.

        Internal server errors are thrown, everything else just has us return False
        together with the message.
        """
        try:
            response = requests.get(f"{self._api_url}/is_alive", timeout=timeout)
            if response.status_code == 200:
                return IsAliveResponse(**response.json())
            elif response.status_code == 511:
                exc_transfer = _ExceptionTransfer(**response.json()["swerexception"])
                self._handle_transfer_exception(exc_transfer)
            msg = (
                f"Status code {response.status_code} from {self._api_url}/is_alive. "
                f"Message: {response.json().get('message')}"
            )
            return IsAliveResponse(is_alive=False, message=msg)
        except requests.RequestException:
            msg = f"Failed to connect to {self.host}\n"
            msg += traceback.format_exc()
            self.logger.debug(msg)
            return IsAliveResponse(is_alive=False, message=msg)
        except Exception:
            msg = f"Failed to connect to {self.host}\n"
            msg += traceback.format_exc()
            self.logger.debug(msg)
            return IsAliveResponse(is_alive=False, message=msg)

    async def wait_until_alive(self, *, timeout: float | None = None):
        return await _wait_until_alive(self.is_alive, timeout=timeout)

    async def create_session(self, request: CreateSessionRequest) -> CreateSessionResponse:
        response = requests.post(f"{self._api_url}/create_session", json=request.model_dump())
        response.raise_for_status()
        return CreateSessionResponse(**response.json())

    async def run_in_session(self, action: Action) -> Observation:
        self.logger.debug("Running action: %s", action)
        response = requests.post(f"{self._api_url}/run_in_session", json=action.model_dump())
        self._handle_response_errors(response)
        return Observation(**response.json())

    async def close_session(self, request: CloseSessionRequest) -> CloseSessionResponse:
        response = requests.post(f"{self._api_url}/close_session", json=request.model_dump())
        self._handle_response_errors(response)
        return CloseSessionResponse(**response.json())

    async def execute(self, command: Command) -> CommandResponse:
        response = requests.post(f"{self._api_url}/execute", json=command.model_dump())
        self._handle_response_errors(response)
        return CommandResponse(**response.json())

    async def read_file(self, request: ReadFileRequest) -> ReadFileResponse:
        response = requests.post(f"{self._api_url}/read_file", json=request.model_dump())
        self._handle_response_errors(response)
        return ReadFileResponse(**response.json())

    async def write_file(self, request: WriteFileRequest) -> WriteFileResponse:
        response = requests.post(f"{self._api_url}/write_file", json=request.model_dump())
        self._handle_response_errors(response)
        return WriteFileResponse(**response.json())

    async def upload(self, request: UploadRequest) -> UploadResponse:
        source = Path(request.source_path)
        if source.is_dir():
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = Path(temp_dir) / f"{source.name}.zip"
                shutil.make_archive(str(zip_path.with_suffix("")), "zip", source)
                files = {"file": zip_path.open("rb")}
                data = {"target_path": request.target_path, "unzip": "true"}
                response = requests.post(f"{self._api_url}/upload", files=files, data=data)
                self._handle_response_errors(response)
                return UploadResponse(**response.json())
        else:
            files = {"file": source.open("rb")}
            data = {"target_path": request.target_path, "unzip": "false"}
            response = requests.post(f"{self._api_url}/upload", files=files, data=data)
            self._handle_response_errors(response)
            return UploadResponse(**response.json())

    async def close(self):
        response = requests.post(f"{self._api_url}/close")
        self._handle_response_errors(response)
