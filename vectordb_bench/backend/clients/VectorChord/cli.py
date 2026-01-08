import os
from typing import Annotated, Unpack

import click
from pydantic import SecretStr

from vectordb_bench.backend.clients import DB
from ..pgvector.cli import PgVectorTypedDict

from ....cli.cli import (
    CommonTypedDict,
    IVFFlatTypedDict,
    cli,
    click_parameter_decorators_from_typed_dict,
    run,
    get_custom_case_config,
)


class VectorChordTypedDict(PgVectorTypedDict):
    index_method: Annotated[
        str,
        click.option(
            "--index-method",
            type=click.Choice(["vchordrq", "vchordg"]),
            help="Index method to use",
            default="vchordrq",
        ),
    ]
    m: Annotated[
        int,
        click.option(
            "-m",
            "--m",
            type=int,
            help="Max number of connections per layer",
            default=16,
        ),
    ]
    ef_construction: Annotated[
        int,
        click.option(
            "--ef-construction",
            type=int,
            help="Size of the dynamic candidate list for constructing the graph",
            default=256,
        ),
    ]
    residual_quantization: Annotated[
        str,
        click.option(
            "--residual-quantization",
            type=click.Choice(["True", "False"]),
            help="Enable residual quantization",
            required=False,
        ),
    ]
    spherical_centroids: Annotated[
        str,
        click.option(
            "--spherical-centroids",
            type=click.Choice(["True", "False"]),
            help="his option determines whether to perform spherical K-means -- the centroids are L2 normalized after each iteration",
            required=False,
        ),
    ]
    lists: Annotated[
        int,
        click.option(
            "--lists",
            type=int,
            help="Number of inverted lists (clusters) for IVF index",
            default=1024,
        ),
    ]
    probes: Annotated[
        int,
        click.option(
            "--probes",
            type=int,
            help="Number of lists to probe during search",
            default=64,
        ),
    ]
    epsilon: Annotated[
        float,
        click.option(
            "--epsilon",
            type=float,
            help="Epsilon parameter for search",
            default=0.1,
        ),
    ]
    ef_search: Annotated[
        int,
        click.option(
            "--ef-search",
            type=int,
            help="Number of candidates to track during search",
            default=64,
        ),
    ]
    create_index_before_load: Annotated[
        bool,
        click.option(
            "--create-index-before-load/--no-create-index-before-load",
            default=False,
            help="Whether to create index before loading data",
        ),
    ]


class VectorChordIVFFlatTypedDict(VectorChordTypedDict, IVFFlatTypedDict): ...


@cli.command()
@click_parameter_decorators_from_typed_dict(VectorChordIVFFlatTypedDict)
def VectorChordIVF(
    **parameters: Unpack[VectorChordIVFFlatTypedDict],
):
    from .config import VectorChordConfig, VectorChordIVFFlatConfig

    parameters["custom_case"] = get_custom_case_config(parameters)

    run(
        db=DB.VectorChord,
        db_config=VectorChordConfig(
            db_label=parameters["db_label"],
            user_name=parameters["user_name"],
            password=SecretStr(parameters["password"]),
            host=parameters["host"],
            port=parameters["port"],
            db_name=parameters["db_name"],
            connect_timeout=parameters["connect_timeout"],
        ),
        db_case_config=VectorChordIVFFlatConfig(
            max_parallel_workers=parameters.get("max_parallel_workers", 2),
            index_method=parameters.get("index_method", "vchordrq"),
            residual_quantization=parameters.get("residual_quantization") == "True",
            spherical_centroids=parameters.get("spherical_centroids") == "True",
            create_index_before_load=parameters.get("create_index_before_load", False),
            probes=parameters.get("probes") or 64,
            epsilon=parameters.get("epsilon", 0.1),
            ef_search=parameters.get("ef_search", 64),
            m=parameters.get("m", 16),
            ef_construction=parameters.get("ef_construction", 256),
            lists=parameters.get("lists") or 1024,
        ),
        **parameters,
    )
