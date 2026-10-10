"""SACL V1 Legacy Compatibility Subsystem.

Provides adapters, state bridging, wave packaging, and operator experience
coordination preserving proven Stable-Ecommerce-Orchestrator behavior.
"""

from sacl.legacy.adapter import LegacyPackageAdapter
from sacl.legacy.compatibility import (
    check_dirty_root,
    extract_legacy_result,
    generate_governance_header,
    verify_legacy_process,
)
from sacl.legacy.operator import LegacyOperatorExperience, OperatorRunResult
from sacl.legacy.packager import WaveZipPackager
from sacl.legacy.state_bridge import LegacyStateBridge

__all__ = [
    "LegacyPackageAdapter",
    "LegacyStateBridge",
    "WaveZipPackager",
    "LegacyOperatorExperience",
    "OperatorRunResult",
    "extract_legacy_result",
    "generate_governance_header",
    "verify_legacy_process",
    "check_dirty_root",
]
