#!/usr/bin/env python
import inspect
import sys
from types import GenericAlias
from types import UnionType
from typing import Any
from typing import get_args
from typing import get_origin

import app
from apispec import APISpec
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
        plugins=[PydanticPlugin()],
    )

    for model in [getattr(types, e) for e in dir(types)]:
        if not inspect.isclass(model):
            continue
        if (
            issubclass(model, BaseModel)
            and model is not BaseModel
            and not model.__name__.startswith("_")
        ):
            spec.components.schema(model.__name__, schema=model)
            Registry.register(model)
        elif (
            issubclass(model, types.KnownResponse) and model is not types.KnownResponse
        ):
            schema: dict[str, Any] = {"description": model.__doc__}
            if model._response_model is not None:
                schema["content"] = {
                    "application/json": {"schema": model._response_model.__name__}
                }
            spec.components.response(model.__name__, schema)

    for path in sorted(app.app.routes.keys()):
        ops: dict[str, Any] = {}
        params: list[dict[str, Any]] | None = None
        for method in app.app.routes[path]:
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

            operation_id = route.view_name
            func_mod = inspect.getmodule(func)
            if func_mod and func_mod is not app:
                operation_id = (
                    func_mod.__name__.removeprefix("chalicelib.blueprints.")
                    + "."
                    + operation_id
                )

            responses: dict[str, Any] = {"500": "error"}

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

            op = {"operationId": operation_id, "responses": responses}

            if "request_body" in sig.parameters:
                op["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": sig.parameters["request_body"].annotation.__name__
                        }
                    }
                }

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
