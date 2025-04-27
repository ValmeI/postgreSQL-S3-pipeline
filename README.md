# postgreSQL-S3-pipeline


DMS, Kinesis and RDS are chosen for this task for simplicity and faster implementation. For idea that first test simpler solution and if needed, we can move to more complex solution.

As a sidenote, i would prefer to save RDS WAL messages to S3, so that we can use them for point-in-time recovery etc. But this is out of scope for this task.

S3 use parequa not json
lamda use docker not regular to avoid layers size limits


all files are non root of the project but as the project grows we should seperate to different directories for better organization
