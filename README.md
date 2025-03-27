<div align="center">
<a href="https://swe-rex.com"><img src="docs/assets/swe-rex-logo-bg.svg" alt="SWE-ReX" style="height: 10em"/></a>

# SWE-agent Remote Execution Framework

[👉 Read the documentation 👈](https://swe-rex.com)

[![Pytest](https://github.com/SWE-agent/swe-rex/actions/workflows/pytest.yaml/badge.svg)](https://github.com/SWE-agent/swe-rex/actions/workflows/pytest.yaml)
[![Check Markdown links](https://github.com/SWE-agent/swe-rex/actions/workflows/check-links.yaml/badge.svg)](https://github.com/SWE-agent/swe-rex/actions/workflows/check-links.yaml)
[![build-docs](https://github.com/SWE-agent/swe-rex/actions/workflows/build-docs.yaml/badge.svg)](https://github.com/SWE-agent/swe-rex/actions/workflows/build-docs.yaml)
</div>

SWE-ReX is a runtime interface for interacting with sandboxed shell environments, allowing you to effortlessly let your AI agent run *any command* on *any environment*.

Whether commands are executed locally or remotely in Docker containers, AWS remote machines, Modal, or something else, your agent code remains the same.
Running 100 agents in parallel? No problem either!

Specifically, SWE-ReX allows your agent to

* ✅ **Interact with running shell sessions**. SWE-ReX will recognize when commands are finished, extract the output and exit code and return them to your agent.
* ✅ Let your agent use **interactive command line tools** like `ipython`, `gdb` or more in the shell.
* ✅ Interact with **multiple such shell sessions in parallel**, similar to how humans can have a shell, ipython, gdb, etc. all running at the same time.

We built SWE-ReX to help you focus on developing and evaluating your agent, not on infrastructure.

SWE-ReX came out of our experiences with [SWE-agent][] and [SWE-agent enigma][enigma].
Using SWE-ReX, we

* 🦖 Support **fast, massively parallel** agent runs (which made evaluating on large benchmarks a breeze).
* 🦖 Support a **broad range of platforms**, including non-Linux machines without Docker.
* 🦖 **Disentangle agent logic from infrastructure concerns**, making SWE-agent more stable and easier to maintain.

This is [SWE-agent][] using SWE-ReX to run on 30 [SWE-bench][] instances in parallel:

<div align="center">
<img src="https://private-user-images.githubusercontent.com/13602468/416860062-2b207eb5-8593-46ec-b025-19c857c84933.gif?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDA1MTQ3MDIsIm5iZiI6MTc0MDUxNDQwMiwicGF0aCI6Ii8xMzYwMjQ2OC80MTY4NjAwNjItMmIyMDdlYjUtODU5My00NmVjLWIwMjUtMTljODU3Yzg0OTMzLmdpZj9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTAyMjUlMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwMjI1VDIwMTMyMlomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPTFjOGNmZDczZmM2YmQwN2EzZDQ1NjkwM2M5NDNhZmEzNzMwZTUxNDNkOTA2OGVmOGM1NTM3MWRhMDg3NTZmZDMmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.iVxw9VeB7DDK1YRTUP3NbGtAlp2PQuHiJ07eS44E31s" alt="SWE-ReX in action" width=600px>
</div>

## Get started

```bash
pip install swe-rex
# With modal support
pip install 'swe-rex[modal]'
# With fargate support
pip install 'swe-rex[fargate]'
# Development setup (all optional dependencies)
pip install 'swe-rex[dev]'
```

Then head over to [our documentation](https://swe-rex.com/) to learn more!


[SWE-agent]: https://swe-agent.com
[SWE-bench]: https://swebench.com
[enigma]: https://enigma-agent.com/
