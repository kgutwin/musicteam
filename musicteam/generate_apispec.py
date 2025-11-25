#!/usr/bin/env python
import inspect
import re
import sys
from types import GenericAlias
from types import UnionType
from typing import Any
from typing import get_args
from typing import get_origin

import app
from apispec import APISpec
from apispec.exceptions import DuplicateComponentNameError
from apispec_pydantic_plugin import PydanticPlugin
from apispec_pydantic_plugin import Registry
from chalicelib import types
from pydantic import BaseModel


def generate() -> str:
    spec = APISpec(
        title="MusicTeam",
        version="0.1.0",
        openapi_version="3.0.2",
        info={"description": "a music management tool"},
        servers=[{"url": "/api"}],
        plugins=[PydanticPlugin()],
        security=[{"cookie": []}, {"api_key": []}],
    )
    spec.components.security_scheme(
        "cookie",
        {
            "type": "apiKey",
            "in": "cookie",
            "name": "session",
            "description": "A cookie as issued by a valid login process",
        },
    )
    spec.components.security_scheme(
        "api_key",
        {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "An API key associated with a user",
        },
    )

    for model in [getattr(types, e) for e in dir(types)]:
        if not inspect.isclass(model):
            continue
        if (
            issubclass(model, BaseModel)
            and model is not BaseModel
            and not model.__name__.startswith("_")
        ):
            try:
                spec.components.schema(model.__name__, schema=model)
            except DuplicateComponentNameError:
                # currently assuming that we are getting this error
                # because the component came in as a dependency of
                # another component.
                pass

            Registry.register(model)
        elif (
            issubclass(model, types.KnownResponse) and model is not types.KnownResponse
        ):
            schema: dict[str, Any] = {"description": model.__doc__}
            if model._response_model is not None:
                schema.setdefault("content", {})["application/json"] = {
                    "schema": model._response_model.__name__
                }
            if model._response_bytes:
                schema.setdefault("content", {})["application/octet-stream"] = {
                    "schema": {"type": "string", "format": "binary"}
                }
            spec.components.response(model.__name__, schema)

    for path in sorted(app.app.routes.keys()):
        ops: dict[str, Any] = {}
        params: list[dict[str, Any]] | None = None
        for method in app.app.routes[path]:
            if method == "HEAD":
                continue

            route = app.app.routes[path][method]
            func = route.view_function
            sig = inspect.signature(func)

            # get the path-level parameters
            if not params:
                for name in route.view_args:
                    assert (
                        sig.parameters[name].annotation is str
                    ), f"{route.view_name} param {name} is not string"

                params = [
                    {
                        "name": name,
                        "in": "path",
                        "required": "true",
                        "schema": {"type": "string"},
                    }
                    for name in route.view_args
                ]

            # set the operation ID
            operation_id = route.view_name
            func_mod = inspect.getmodule(func)
            if func_mod and func_mod is not app:
                operation_id = (
                    func_mod.__name__.removeprefix("chalicelib.blueprints.")
                    + "."
                    + operation_id
                )

            # determine the expected responses from the return annotation
            responses: dict[str, Any] = {"500": "Error"}

            return_types = (
                get_args(sig.return_annotation)
                if isinstance(sig.return_annotation, UnionType)
                else (sig.return_annotation,)
            )

            for return_type in return_types:
                if isinstance(return_type, GenericAlias):
                    return_type = get_origin(return_type)

                if return_type is dict:
                    responses["200"] = {
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    }
                elif inspect.isclass(return_type) and issubclass(
                    return_type, BaseModel
                ):
                    responses["200"] = {
                        "content": {
                            "application/json": {"schema": return_type.__name__}
                        }
                    }
                elif inspect.isclass(return_type) and issubclass(
                    return_type, types.KnownResponse
                ):
                    responses[str(return_type._code)] = return_type.__name__
                else:
                    raise Exception(f"unhandled return type: {return_type}")

            op: dict[str, Any] = {
                "operationId": operation_id,
                "responses": responses,
                "tags": [operation_id.split(".")[0].title()],
            }

            # add summary and description if present
            if func.__doc__:
                op["summary"] = func.__doc__.splitlines()[0]
                description = func.__doc__.removeprefix(op["summary"]).strip()
                if description:
                    op["description"] = re.sub(r"(\w)\n(\w)", r"\1 \2", description)

            # add the request body if present
            if "request_body" in sig.parameters:
                ann = sig.parameters["request_body"].annotation
                if ann is bytes:
                    op["requestBody"] = {
                        "content": {"text/plain": {"schema": {"type": "string"}}}
                    }
                else:
                    op["requestBody"] = {
                        "content": {"application/json": {"schema": ann.__name__}}
                    }

            # add the query params if present
            if "query_params" in sig.parameters:
                ann = sig.parameters["query_params"].annotation
                schema = ann.model_json_schema()["properties"]
                op["parameters"] = [
                    {
                        "name": field,
                        "in": "query",
                        "required": info.is_required(),
                        "schema": schema[field],
                    }
                    for field, info in ann.model_fields.items()
                ]

            ops[method.lower()] = op

        spec.path(path=path, operations=ops, parameters=params)

    return spec.to_yaml()


if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            with open(sys.argv[1], "r") as fp:
                existing_content = fp.read()
        except FileNotFoundError:
            existing_content = ""

        new_content = generate()

        with open(sys.argv[1], "w") as fp:
            fp.write(new_content)

        sys.exit(0 if new_content == existing_content else 1)
    else:
        print(generate())
