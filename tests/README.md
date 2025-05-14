# MusicAI SDK Tests

This directory contains tests for the MusicAI Python SDK.

## Running Tests

### Setup

Before running tests, you need to set up your API. Create a `.env.local` file at the `/tests/docker` directory with the following content:

```
MUSIC_AI_TEST_HOST=your_test_host_here
MUSIC_AI_TEST_API_KEY=your_api_key_here
```

Replace the values with your actual test host and API key.

### Running the Tests

To run the tests, use `test.sh`:

```bash
# From the root directory of the project
./test.sh
```

## Test Coverage

Currently, the test suite includes:

- Tests for the `MusicAiClient` class against the real Music.ai API
- Custom API host and key are loaded from environment variables

## Troubleshooting

- If your API key is invalid, tests will fail with authorization errors
- If no API key is provided, tests will be skipped with a helpful message
- The host URL is optional - if not provided, the default production API endpoint will be used 
