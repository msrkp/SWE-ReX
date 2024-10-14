import time

import pexpect

from local import AbstractRuntime
from models import Action, CloseRequest, CloseResponse, CreateShellRequest, CreateShellResponse, Observation


class Session:
    def __init__(self):
        """This basically represents one REPL that we control.

        It's pretty similar to a `pexpect.REPLWrapper`.
        """
        self._ps1 = "SHELLPS1PREFIX"
        self.shell: pexpect.spawn | None = None

    def start(self) -> CreateShellResponse:
        self.shell = pexpect.spawn(
            "/bin/bash",
            encoding="utf-8",
            echo=False,
        )
        time.sleep(0.1)
        self.shell.sendline("echo 'fully_initialized'")
        try:
            self.shell.expect("fully_initialized", timeout=1)
        except pexpect.TIMEOUT:
            return CreateShellResponse(success=False, failure_reason="timeout while initializing shell")
        output = self.shell.before
        self.shell.sendline(f"umask 002; export PS1='{self._ps1}'; export PS2=''")
        try:
            self.shell.expect(self._ps1, timeout=1)
        except pexpect.TIMEOUT:
            return CreateShellResponse(success=False, failure_reason="timeout while setting PS1")
        output += "\n---\n" + self.shell.before  # type: ignore
        return CreateShellResponse(output=output)

    def run(self, action: Action) -> Observation:
        if self.shell is None:
            return Observation(output="", exit_code_raw="-300", failure_reason="shell not initialized")
        self.shell.sendline(action.command)
        try:
            expect_strings = action.expect + [self._ps1]
            expect_index = self.shell.expect(expect_strings, timeout=action.timeout)  # type: ignore
            expect_string = expect_strings[expect_index]
        except pexpect.TIMEOUT:
            expect_string = ""
            return Observation(output="", exit_code_raw="-100", failure_reason="timeout while running command")
        output: str = self.shell.before  # type: ignore
        if not action.is_interactive_command and not action.is_interactive_quit:
            self.shell.sendline("\necho $?")
            try:
                self.shell.expect(self._ps1, timeout=1)
            except pexpect.TIMEOUT:
                return Observation(output="", exit_code_raw="-200", failure_reason="timeout while getting exit code")
            exit_code_raw: str = self.shell.before.strip()  # type: ignore
            # After quitting an interactive session, for some reason we oftentimes get double
            # PS1 for all following commands. So we might need to call expect again.
            # Alternatively we could have probably called `echo <<<$?>>>` or something.
            if not exit_code_raw.strip():
                print("exit_code_raw was empty, trying again")
                self.shell.expect(self._ps1, timeout=1)
                exit_code_raw = self.shell.before.strip()  # type: ignore
        elif action.is_interactive_quit:
            assert not action.is_interactive_command
            exit_code_raw = "0"
            self.shell.setecho(False)
            self.shell.waitnoecho()
            self.shell.sendline("stty -echo; echo 'doneremovingecho'; echo 'doneremovingecho'")
            # Might need two expects for some reason
            print(self.shell.expect("doneremovingecho", timeout=1))
            print(self.shell.expect(self._ps1, timeout=1))
        else:
            # Trouble with echo mode within an interactive session that we
            output = output.lstrip().removeprefix(action.command).strip()
            exit_code_raw = "0"
        return Observation(output=output, exit_code_raw=exit_code_raw, expect_string=expect_string)

    def close(self) -> CloseResponse:
        if self.shell is None:
            return CloseResponse()
        self.shell.close()
        self.shell = None
        return CloseResponse()


class Runtime(AbstractRuntime):
    def __init__(self):
        """This is the main entry point for the runtime.

        It keeps track of all the sessions (individual repls) that are currently open.
        """
        self.sessions: dict[str, Session] = {}

    def create_shell(self, request: CreateShellRequest) -> CreateShellResponse:
        assert request.name not in self.sessions
        shell = Session()
        self.sessions[request.name] = shell
        return shell.start()

    def run(self, action: Action) -> Observation:
        return self.sessions[action.session].run(action)

    def close(self, request: CloseRequest) -> CloseResponse:
        out = self.sessions[request.session].close()
        del self.sessions[request.session]
        return out
