FROM python:3.12-slim

LABEL org.opencontainers.image.title="id-tamper-check" \
      org.opencontainers.image.description="Detect and visualize tampering in ID card and document images with OpenCV and SSIM" \
      org.opencontainers.image.source="https://github.com/saineshnakra/Identification-Card-Fraud-Detection" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install . && useradd --create-home app

USER app
WORKDIR /data
ENTRYPOINT ["id-tamper-check"]
CMD ["--help"]
