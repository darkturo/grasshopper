# tracker
This is a coding exercise in Python3 featuring a simple service to track test times 
of an application called grasshopper. The grasshopper is a simple python script that 
reports on a time interval the cpu usage of the system. 

The API for the tracker service is as follows:

POST /api/v1/auth
Request:
{
    "username": "admin",
    "password": "admin"
}
Response:
{
    "token": "... jwt token ..."
}

POST /api/v1/test
Request:
{
    "name": "my test run ",
    "description": "running on a sunny day",
    "threshold": 0.5,
}
Response:
{
    "id": 1,
    "start_time": "2021-01-01T00:00:00"
}

POST /api/v1/test/:id/usage
Request:
{
    "cpu_usage": 0.5,
    "timestamp": "2021-01-01T00:00:00",
}
Response:
{
    "id": 1,
    "above_threshold": false,
}

POST /api/v1/test/:id/stop
Request:
{
    "end_time": "2021-01-01T00:00:00",
}

GET /api/v1/test/:id
Response:
{
    "id": 1,
    "time_above_threshold": 0,"
    "active": false,
    "start_time": "2021-01-01T00:00:00",
    "end_time": "2021-01-01T00:00:00",
    "duration": 0, // seconds
}

## How to run
Startup the service with flask from the root of the repo:

```bash
flask --app tracker run
```


Then on another console, run the grasshopper script:

```bash
python3 grasshopper.py --jwt $TOKEN --threshold 2 --no-command
```

This will run grasshopper without wrapping any command reporting to the tracker service every .5 seconds (configurable) the cpu usage of the system.
It is possible to run the script with a command to wrap, for example:

```bash
python3 grasshopper.py --jwt $TOKEN --threshold 2 transcode-video-tool -i input.avi -o ouput.avi -fps 30 -q 5 -s 1024x768
```
