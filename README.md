# Music.ai Python Client Library

This is a Python client library for the Music.AI API. For more information on the API and its capabilities, see the [API documentation](https://music.ai/docs/getting-started/introduction/).

## Installation

You can install the library via pip:

```bash
pip install musicai_sdk
```

## Usage

Here's an example of how you can use the client to upload a local file, create a job and more:

```python
from musicai_sdk import MusicAiClient

client = MusicAiClient(api_key='your-api-key')

# Get application info
app_info = client.get_application_info()
print('Application Info:', app_info)

# Upload local file
file_url = client.upload_file(file_path='your-file-path')
print('File Url:', file_url)

# Create Job
workflow_params = {
    'inputUrl': file_url,
}
add_job_info = client.add_job(job_name='your-job-name', workflow_slug='your-workflow-slug', params=workflow_params)
job_id = add_job_info['id']
print('Job Created:', job_id)

# Get job info
job_info = client.get_job(job_id=job_id)
print('Job Status:', job_info['status'])
print('Job Result:', job_info['result'])

# Delete job
client.delete_job(job_id=job_id)

# Get all jobs
jobs = client.get_jobs()
print('Jobs:', jobs)

# Get all workflows
workflows = client.list_workflows()
print('Workflows:', workflows)
```
