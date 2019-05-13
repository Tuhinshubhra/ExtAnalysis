FROM alpine:3.9
LABEL MAINTAINER furkan.sayim@yandex.com
LABEL name ExtAnalysis
LABEL src "https://github.com/Tuhinshubhra/ExtAnalysis"
LABEL creator Tuhinshubhra
LABEL desc "Browser Extension Analysis Framework"

RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

RUN apk add git
RUN git clone https://github.com/Tuhinshubhra/ExtAnalysis.git /tmp/extanalysis

WORKDIR /tmp/extanalysis
RUN pip3 install -r requirements.txt

EXPOSE 13337

ENTRYPOINT ["python3", "extanalysis.py"]
