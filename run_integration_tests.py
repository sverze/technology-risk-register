#!/usr/bin/env python3
"""
Integration test runner for Technology Risk Register API.

This script helps run integration tests against a local or Docker deployment.
"""

import os
import subprocess
import sys
import time

import requests


def check_api_health(base_url: str, max_retries: int = 10, delay: int = 2) -> bool:
    """Check if the API is healthy and responding."""
    health_url = f"{base_url}/health"

    for attempt in range(max_retries):
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    print(f"✅ API is healthy at {base_url}")
                    return True
        except requests.RequestException:
            pass

        if attempt < max_retries - 1:
            print(f"⏳ Waiting for API to be ready... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)

    return False


def run_integration_tests(api_url: str) -> int:
    """Run the integration tests."""
    print(f"🚀 Running integration tests against {api_url}")

    # Set environment variable for tests
    env = os.environ.copy()
    env["API_BASE_URL"] = api_url

    # Run pytest with integration tests
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
    ]

    try:
        result = subprocess.run(cmd, env=env, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\n❌ Tests interrupted by user")
        return 1


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Run integration tests for Technology Risk Register API")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--no-health-check",
        action="store_true",
        help="Skip health check before running tests",
    )
    parser.add_argument(
        "--wait-timeout",
        type=int,
        default=30,
        help="Maximum seconds to wait for API to be healthy (default: 30)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("🧪 Technology Risk Register - Integration Tests")
    print("=" * 60)
    print(f"API URL: {args.url}")
    print()

    # Check if API is healthy (unless skipped)
    if not args.no_health_check:
        max_retries = args.wait_timeout // 2
        if not check_api_health(args.url, max_retries=max_retries):
            print(f"❌ API at {args.url} is not responding or unhealthy")
            print()
            print("💡 Make sure the API is running:")
            print("   Local:  uvicorn app.main:app --host 0.0.0.0 --port 8000")
            print("   Docker: docker-compose up")
            return 1
        print()

    # Run the tests
    exit_code = run_integration_tests(args.url)

    if exit_code == 0:
        print("\n✅ All integration tests passed!")
    else:
        print(f"\n❌ Integration tests failed (exit code: {exit_code})")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
