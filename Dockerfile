FROM astrocrpublic.azurecr.io/runtime:3.0-10
# ---- Base: Astronomer Astro Runtime (Airflow bundled) ----
# Pick a recent runtime compatible with your Astro CLI
FROM quay.io/astronomer/astro-runtime:10.5.0

# We’ll switch to root to install OS/Python deps, then drop back to the airflow user.
USER root

# ---- (Optional) OS packages ----
# If you ever need system packages, list them in packages.txt (one per line).
# Build will skip this step if packages.txt is absent.
COPY packages.txt /tmp/packages.txt
RUN if [ -f /tmp/packages.txt ]; then \
      apt-get update && \
      xargs -a /tmp/packages.txt apt-get install -y --no-install-recommends && \
      rm -rf /var/lib/apt/lists/*; \
    fi

# ---- Python dependencies ----
# Make sure requirements.txt is at the project root.
COPY requirements.txt /requirements.txt
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

# ---- Project files ----
# NOTE: These directories must exist in your repo (even empty). Add a .gitkeep if needed.
WORKDIR /usr/local/airflow

# Copy DAGs, helper scripts, SQL and Soda configs, and any other includes (data, templates, etc.)
COPY dags/     /usr/local/airflow/dags/
COPY scripts/  /usr/local/airflow/scripts/
COPY sql/      /usr/local/airflow/sql/
COPY soda/     /usr/local/airflow/soda/
COPY include/  /usr/local/airflow/include/

# ---- Airflow / Runtime env ----
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False \
    PYTHONPATH="/usr/local/airflow:${PYTHONPATH}"

# ---- Permissions ----
# Runtime image uses user `astro`. Ensure your files are readable by it.
RUN chown -R astro:astro /usr/local/airflow
USER astro
