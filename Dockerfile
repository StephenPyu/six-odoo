FROM python:3.12.2-slim

RUN apt-get update && apt-get install -y \
    g++ \
    postgresql-client \
    libpq-dev \
    git \
    gcc \
    python3-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    wkhtmltopdf

# Set environment variables
ENV ODOO_VERSION=18.0 \
    ODOO_HOME=/opt/odoo \
    ODOO_USER=odoo \
    ODOO_CONFIG=/etc/odoo/odoo.conf \
    ODOO_EXTRA_ADDONS=/etc/addons

# Create Odoo user and directories
RUN useradd -m -d $ODOO_HOME -U -r -s /bin/bash $ODOO_USER
RUN mkdir -p /var/lib/odoo /etc/odoo $ODOO_EXTRA_ADDONS && chown -R $ODOO_USER:$ODOO_USER /var/lib/odoo /etc/odoo $ODOO_EXTRA_ADDONS

# Copy Odoo source code
COPY --chown=$ODOO_USER:$ODOO_USER . $ODOO_HOME
COPY --chown=$ODOO_USER:$ODOO_USER odoo-docker.conf $ODOO_CONFIG

# Install Python dependencies
WORKDIR $ODOO_HOME
RUN pip install --upgrade pip setuptools wheel Cython
RUN pip install psycopg2-binary
RUN pip install -r requirements.txt

# Expose Odoo port
EXPOSE 8069

# Define entrypoint
USER $ODOO_USER
CMD ["python3", "odoo-bin", "--config", "/etc/odoo/odoo.conf"]

#docker run -d --name six-odoo -p 8069:8069 -v /Users/yuping/Work/odoo/addons-external/oca/tutorials:/etc/addons six-odoo:18.0
#docker exec -it six-odoo /bin/bash