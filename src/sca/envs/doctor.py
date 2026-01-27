"""Environment diagnostics for OSWorld setup validation."""

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class CheckResult:
    """Result of a single diagnostic check."""

    name: str
    passed: bool
    message: str


def check_docker() -> CheckResult:
    """Check if Docker is available and running."""
    if not shutil.which("docker"):
        return CheckResult("docker", False, "Docker not found in PATH")
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return CheckResult("docker", True, "Docker is running")
        return CheckResult("docker", False, "Docker daemon not running")
    except subprocess.TimeoutExpired:
        return CheckResult("docker", False, "Docker command timed out")
    except Exception as e:
        return CheckResult("docker", False, f"Docker check failed: {e}")


def check_vmware() -> CheckResult:
    """Check if VMware tools are available."""
    vmrun = shutil.which("vmrun")
    if vmrun:
        return CheckResult("vmware", True, f"vmrun found at {vmrun}")
    return CheckResult("vmware", False, "vmrun not found (VMware not installed)")


def check_virtualbox() -> CheckResult:
    """Check if VirtualBox is available."""
    vboxmanage = shutil.which("VBoxManage")
    if vboxmanage:
        return CheckResult("virtualbox", True, f"VBoxManage found at {vboxmanage}")
    return CheckResult("virtualbox", False, "VBoxManage not found")


def check_python_deps() -> CheckResult:
    """Check if OSWorld Python dependencies are importable."""
    try:
        import importlib.util

        if importlib.util.find_spec("desktop_env") is not None:
            return CheckResult("osworld_deps", True, "desktop_env module found")
        return CheckResult(
            "osworld_deps", False, "desktop_env not installed (pip install osworld)"
        )
    except Exception:
        return CheckResult(
            "osworld_deps", False, "desktop_env not installed (pip install osworld)"
        )


def run_doctor(check: str = "all") -> int:
    """Run environment diagnostics."""
    checks: list[CheckResult] = []

    if check in ("all", "docker"):
        checks.append(check_docker())

    if check in ("all", "osworld"):
        checks.append(check_vmware())
        checks.append(check_virtualbox())
        checks.append(check_python_deps())

    # Print results
    print("\n🔍 Environment Diagnostics\n")
    passed = 0
    failed = 0

    for result in checks:
        status = "✓" if result.passed else "✗"
        print(f"  {status} {result.name}: {result.message}")
        if result.passed:
            passed += 1
        else:
            failed += 1

    print(f"\n  {passed} passed, {failed} failed\n")

    # Return 0 if at least one virtualization option works
    has_vm = any(
        r.passed for r in checks if r.name in ("docker", "vmware", "virtualbox")
    )
    return 0 if has_vm else 1
