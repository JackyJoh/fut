FROM public.ecr.aws/lambda/python:3.12

# Copy requirements and install
COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (no ML models needed - predictions cached in DB)
COPY *.py ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD ["main.handler"]
