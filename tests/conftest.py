import os

import dotenv
import pytest

# Load environment variables from .env.local file if it exists
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), "../.env.local"))


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and conftest file after command line options have been parsed.
    """
    # Print a helpful message if no API key is found
    if not os.environ.get("MUSIC_AI_TEST_API_KEY"):
        print("\nWARNING: No MUSIC_AI_TEST_API_KEY environment variable found. Some tests will be skipped.")
        print("To run all tests, please create a .env.local file in the project root with your API key and host:")
        print("MUSIC_AI_TEST_HOST=your_test_host_here")
        print("MUSIC_AI_TEST_API_KEY=your_api_key_here\n") 