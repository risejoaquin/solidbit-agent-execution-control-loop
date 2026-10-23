"""SACL V1 UI Backend Modules.

Modular providers for Dashboard, Gates, Campaigns, Connections,
Recovery, Evidence, Contracts, and Database Inspector.
"""

from sacl.ui.modules.campaign_designer import CampaignDesignerModule
from sacl.ui.modules.campaigns import CampaignsModule
from sacl.ui.modules.connections import ConnectionsModule
from sacl.ui.modules.contracts import ContractsModule
from sacl.ui.modules.db_inspector import DBInspectorModule
from sacl.ui.modules.email_gateway import EmailGatewayModule
from sacl.ui.modules.evidence import EvidenceModule
from sacl.ui.modules.gates import GatesModule
from sacl.ui.modules.models import ModelsModule
from sacl.ui.modules.projects import ProjectsModule
from sacl.ui.modules.recovery import RecoveryModule
from sacl.ui.modules.roadmap import RoadmapModule
from sacl.ui.modules.telemetry import TelemetryModule

__all__ = [
    "CampaignDesignerModule",
    "CampaignsModule",
    "ConnectionsModule",
    "ContractsModule",
    "DBInspectorModule",
    "EmailGatewayModule",
    "EvidenceModule",
    "GatesModule",
    "ModelsModule",
    "ProjectsModule",
    "RecoveryModule",
    "RoadmapModule",
    "TelemetryModule",
]
