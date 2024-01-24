# Music.ai Python Client Library

This is a Python client library for the Music.AI API. For more information on the API and its capabilities, see the [API documentation](https://music.ai/docs/getting-started/introduction/).

## Installation

You can install the library via pip:

```bash
pip install musicai_sdk
```

## Usage

```python
from musicai_sdk import MusicAiClient

client = MusicAiClient(api_key='your-api-key')

# Get application info
app_info = client.get_application_info()
print('Application Info:', app_info)

# Upload local ile
file_url = client.upload_file(file_path='your-file-path')
print('File Url:', file_url)

# Create Job
workflow_params = {
    'inputUrl': file_url,
}
create_job_info = client.create_job(job_name='your-job-name', workflow_id='your-workflow-id',params=workflow_params)
job_id = create_job_info['id']
print('Job Created:', job_id)

# Wait for job to complete
job_info = client.wait_for_job_completion(job_id)
print('Job Status:', job_info['status'])
print('Job Result:', job_info['result'])

# Get job info
job_info = client.get_job(job_id=job_id)
print('Job Status:', job_info['status'])
print('Job Result:', job_info['result'])

# Delete job
client.delete_job(job_id=job_id)

# Get all jobs
jobs = client.get_jobs()
print('Jobs:', jobs)

```


# Development


Install [poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)


You can run it in development mode:

```bash
poetry install
```

To releae a new version, bump the package and create a Github release with that version:

```bash
poetry version (major|minor|patch)
```
