# ビルドには公式のPythonイメージslim版を使用
FROM python:3.13.4-slim-bookworm AS base
WORKDIR /usr/src/app
ENV PATH=/root/.local/bin:$PATH

RUN apt-get -y update && \
    apt-get -y dist-upgrade && \
    apt-get -y install --no-install-recommends ffmpeg && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM base AS build

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
    curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    poetry config virtualenvs.create false

# キャッシュを効かせるためにpyproject.tomlだけ先にコピー
COPY ./app/pyproject.toml ./app/poetry.lock /usr/src/app/

RUN poetry install --without dev

FROM base AS develop

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends \
    git && \
    apt-get autoclean -y && apt-get clean && rm -rf /var/cache/apt/* /var/lib/apt/lists/*

COPY --from=build /root/.local /root/.local
COPY --from=build /root/.config /root/.config
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# キャッシュを効かせるためにpyproject.tomlだけ先にコピー
COPY ./app/pyproject.toml ./app/poetry.lock /usr/src/app/
RUN poetry install

COPY ./ /usr/src/

# 実行はpythonのdistrolessイメージを使用
FROM base AS production
WORKDIR /usr/src/app

COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY ./ /usr/src/

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
