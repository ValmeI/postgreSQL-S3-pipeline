FROM public.ecr.aws/lambda/python:3.12

COPY *.py ${LAMBDA_TASK_ROOT}
COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN python3 -m pip install -r requirements.txt

CMD [ "app.handler" ]
