##
## Copyright 2024 Ocean Protocol Foundation
## SPDX-License-Identifier: Apache-2.0
##
FROM python:3.13.0rc2-slim
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["/app/entrypoint.sh"]
