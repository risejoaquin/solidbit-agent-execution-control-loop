"""SACL V1 UI Backend Modules.

Modular providers for Dashboard, Gates, Campaigns, Connections,
Recovery, Evidence, Contracts, and Database Inspector.
"""

from sacl.ui.modules.campaigns import CampaignsModule
from sacl.ui.modules.connections import ConnectionsModule
from sacl.ui.modules.contracts import ContractsModule
from sacl.ui.modules.db_inspector import DBInspectorModule
from sacl.ui.modules.evidence import EvidenceModule
from sacl.ui.modules.gates import GatesModule
from sacl.ui.modules.recovery import RecoveryModule

__all__ = [
    "CampaignsModule",
    "ConnectionsModule",
    "ContractsModule",
    "DBInspectorModule",
    "EvidenceModule",
    "GatesModule",
    "RecoveryModule",
]
