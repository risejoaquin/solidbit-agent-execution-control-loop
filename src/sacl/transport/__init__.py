"""SACL V1 Transport Subsystem.

Provides:
- Gmail API OAuth2 adapter interfaces and implementations (IOAuth2CredentialProvider, InMemoryOAuth2CredentialProvider, WindowsCredentialManagerProvider)
- Low-level Gmail REST API adapter and deterministic mocks (IGmailApiAdapter, GmailApiAdapter, MockGmailApiAdapter)
- Google Cloud Pub/Sub Pull subscriber and untrusted wake signal parser (IPubSubSubscriber, PubSubPullSubscriber, MockPubSubSubscriber, WakeSignal, PubSubMessage)
- users.watch lifecycle management and automated renewal (WatchLifecycleManager)
- Anti-Zip Slip, resource quota, and path sanitization pipeline (ZipDefenseExtractor)
- Envelope framing, routing hint parsing, and MIME building (create_mail_envelope, parse_routing_hint, format_outbound_subject, build_outbound_mime)
- History API cursor reconciliation and deduplication matrix (HistoryReconciliationManager, ReconciliationResult)
- Degraded-mode fallback polling and 404 stale cursor recovery (FallbackPoller, PollingResult)
- Outbound results dispatch via Gmail REST API with thread continuity (OutboxDispatcher)
- Unified MailGateway daemon implementing ITransportGateway
"""

from sacl.transport.envelope import (
    build_outbound_mime,
    compute_attachment_metadata,
    create_mail_envelope,
    format_outbound_subject,
    generate_nonce,
    parse_routing_hint,
)
from sacl.transport.exceptions import (
    DuplicateDeliveryError,
    InvalidFilenameError,
    InvalidRoutingHintError,
    PayloadConflictError,
    RateLimitExceededError,
    SenderNotWhitelistedError,
    StaleHistoryCursorError,
    SymlinkNotPermittedError,
    TransportAuthError,
    TransportError,
    ZipDefenseViolation,
    ZipPathTraversalError,
    ZipResourceLimitExceededError,
)
from sacl.transport.gateway import MailGateway
from sacl.transport.gmail_adapter import (
    GmailApiAdapter,
    IGmailApiAdapter,
    MockGmailApiAdapter,
)
from sacl.transport.oauth import (
    CREDENTIAL_TARGET_NAME,
    IOAuth2CredentialProvider,
    InMemoryOAuth2CredentialProvider,
    WindowsCredentialManagerProvider,
)
from sacl.transport.outbox import OutboxDispatcher
from sacl.transport.polling import FallbackPoller, PollingResult
from sacl.transport.pubsub import (
    IPubSubSubscriber,
    MockPubSubSubscriber,
    PubSubMessage,
    PubSubPullSubscriber,
    WakeSignal,
    parse_wake_signal,
)
from sacl.transport.reconciliation import (
    HistoryReconciliationManager,
    ReconciliationResult,
)
from sacl.transport.sanitization import ZipDefenseExtractor
from sacl.transport.watch import WatchLifecycleManager, parse_expiration_timestamp

__all__ = [
    # Gateway
    "MailGateway",
    # OAuth2 Credentials
    "IOAuth2CredentialProvider",
    "InMemoryOAuth2CredentialProvider",
    "WindowsCredentialManagerProvider",
    "CREDENTIAL_TARGET_NAME",
    # Gmail API
    "IGmailApiAdapter",
    "GmailApiAdapter",
    "MockGmailApiAdapter",
    # Pub/Sub
    "IPubSubSubscriber",
    "PubSubPullSubscriber",
    "MockPubSubSubscriber",
    "PubSubMessage",
    "WakeSignal",
    "parse_wake_signal",
    # Watch Lifecycle
    "WatchLifecycleManager",
    "parse_expiration_timestamp",
    # Sanitization & Zip Defense
    "ZipDefenseExtractor",
    # Envelope & Framing
    "parse_routing_hint",
    "format_outbound_subject",
    "generate_nonce",
    "compute_attachment_metadata",
    "build_outbound_mime",
    "create_mail_envelope",
    # Reconciliation
    "HistoryReconciliationManager",
    "ReconciliationResult",
    # Fallback Polling
    "FallbackPoller",
    "PollingResult",
    # Outbox Dispatch
    "OutboxDispatcher",
    # Exceptions
    "TransportError",
    "TransportAuthError",
    "RateLimitExceededError",
    "StaleHistoryCursorError",
    "DuplicateDeliveryError",
    "PayloadConflictError",
    "SenderNotWhitelistedError",
    "InvalidRoutingHintError",
    "ZipDefenseViolation",
    "ZipResourceLimitExceededError",
    "ZipPathTraversalError",
    "InvalidFilenameError",
    "SymlinkNotPermittedError",
]
