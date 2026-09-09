# Production Multi-Stage Dockerfile for WhatnotElse Frappe App
FROM frappe/erpnext:version-16

USER frappe
WORKDIR /home/frappe/frappe-bench

# Copy custom app into bench apps folder
COPY --chown=frappe:frappe whatnot_else /home/frappe/frappe-bench/apps/whatnot_else

# Install custom app and Python dependencies into Frappe env
RUN /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir -e /home/frappe/frappe-bench/apps/whatnot_else && \
    /home/frappe/frappe-bench/env/bin/pip install --no-cache-dir google-generativeai requests

# Build assets
RUN cd /home/frappe/frappe-bench && \
    bench build --app whatnot_else || true

USER frappe
