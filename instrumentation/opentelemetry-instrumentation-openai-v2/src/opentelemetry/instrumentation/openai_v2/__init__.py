# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
OpenAI client instrumentation supporting `openai`, it can be enabled by
using ``OpenAIInstrumentor``.

.. _openai: https://pypi.org/project/openai/

Usage
-----

.. code:: python

    from openai import OpenAI
    from opentelemetry.instrumentation.openai import OpenAIInstrumentor

    OpenAIInstrumentor().instrument()

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "Write a short poem on open telemetry."},
        ],
    )

API
---
"""

from typing import Collection

from wrapt import wrap_function_wrapper

from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.openai_v2.package import _instruments
from opentelemetry.instrumentation.utils import unwrap
from opentelemetry.semconv.schemas import Schemas
from opentelemetry.trace import get_tracer

from .patch import chat_completions_create


class OpenAIInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        """Enable OpenAI instrumentation."""
        tracer_provider = kwargs.get("tracer_provider")
        tracer = get_tracer(
            __name__,
            "",
            tracer_provider,
            schema_url=Schemas.V1_27_0.value,
        )
        wrap_function_wrapper(
            module="openai.resources.chat.completions",
            name="Completions.create",
            wrapper=chat_completions_create(tracer),
        )

    def _uninstrument(self, **kwargs):
        import openai

        unwrap(openai.resources.chat.completions.Completions, "create")