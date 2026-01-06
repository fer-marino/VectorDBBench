from abc import ABC
from typing import Mapping, Any

from ..api import IndexType, MetricType
from ..pgvector.config import (
    PgVectorConfig,
    PgVectorIndexConfig,
    PgVectorIVFFlatConfig,
)


class VectorChordConfig(PgVectorConfig):
    pass


class VectorChordIndexConfig(PgVectorIndexConfig, ABC):
    residual_quantization: bool = True
    spherical_centroids: bool = True

    def parse_metric(self) -> str:
        if self.metric_type == MetricType.L2:
            return "vector_l2_ops"
        if self.metric_type == MetricType.IP:
            return "vector_ip_ops"
        return "vector_cosine_ops"


class VectorChordIVFFlatConfig(PgVectorIVFFlatConfig, VectorChordIndexConfig):
    index: IndexType = IndexType.IVFFlat
    lists: int = 1024
    probes: int = 64

    def index_param(self) -> Mapping[str, Any]:
        # Construct the TOML configuration string
        # We ensure no leading/trailing whitespace and a clean structure
        toml_parts = [
            f"residual_quantization = {str(self.residual_quantization).lower()}",
            f"build.internal.spherical_centroids = {str(self.spherical_centroids).lower()}",
            f"build.internal.build_threads = {self.max_parallel_workers if self.max_parallel_workers else 4}",
            f"build.internal.lists = [{self.lists if self.lists else 1024}]",
        ]
        toml_config = "\n".join(toml_parts)

        return {
            "metric": self.parse_metric(),
            "index_type": "vchord", 
            "options": toml_config,
        }

    def session_param(self) -> Mapping[str, Any]:
        session_parameters = {}
        if self.probes is not None:
            session_parameters["vchordrq.probes"] = str(self.probes)
        return session_parameters


_vectorchord_case_config = {
    IndexType.IVFFlat: VectorChordIVFFlatConfig,
}
