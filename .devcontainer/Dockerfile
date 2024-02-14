FROM python:3.11.8

ARG USER_ID
ARG USER_NAME
ARG USER_GID
ARG USER_GNAME


ARG QUARTO_VERSION=1.4.549

# Install Package dependencies
RUN apt-get update && apt-get install -y \
    sudo git-lfs \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libxkbcommon0 libatspi2.0-0 \
    libxdamage1 libasound2 libdrm2 \
    libxcomposite1 libxfixes3 libxrandr2 \
    libgbm1 && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Download and install Quarto
RUN mkdir -p /opt/quarto/${QUARTO_VERSION}
RUN curl -o quarto.tar.gz -L \
    "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz"
RUN tar -zxvf quarto.tar.gz \
    -C "/opt/quarto/${QUARTO_VERSION}" \
    --strip-components=1
RUN rm quarto.tar.gz
RUN ln -s /opt/quarto/${QUARTO_VERSION}/bin/quarto /usr/local/bin/quarto

# Create user and group
RUN groupadd -g ${USER_GID} ${USER_GNAME}
RUN useradd ${USER_NAME} -u ${USER_ID} -g ${USER_GNAME} -m -s /bin/bash
# Add permission to sudo
RUN echo "${USER_NAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# INSTALL THE REST AS A USER
USER ${USER_NAME}

# Global dev settings
RUN git config --global pull.rebase false
RUN git config --global core.editor "code --wait"
