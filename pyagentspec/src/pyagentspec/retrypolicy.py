# Copyright © 2025 Oracle and/or its affiliates.
#
# This software is under the Apache License 2.0
# (LICENSE-APACHE or http://www.apache.org/licenses/LICENSE-2.0) or Universal Permissive License
# (UPL) 1.0 (LICENSE-UPL or https://oss.oracle.com/licenses/upl), at your option.

"""Retry configuration shared across networked components.
Agent Spec treats ``RetryPolicy`` as a *non-Component* configuration object.
"""

from __future__ import annotations

from typing import Dict, List, Literal, Optional, cast

from pydantic import BaseModel, Field


class RetryPolicy(BaseModel):
    max_attempts: int = 2
    """Maximum number of retries for a request that fails with a recoverable status.

    This value does not include the initial attempt.
    """

    request_timeout: Optional[float] = None
    """Maximum allowed time (in seconds) for a single request attempt.

    This is a per-attempt timeout. When set, runtimes should pass this value to the
    underlying HTTP client / SDK timeout configuration. Values are expressed in
    seconds and may be fractional (e.g., ``0.5`` means 500 milliseconds).
    """

    initial_retry_delay: float = 1.0
    """Base amount of time to wait before retrying (in seconds).

    This is the base delay used for exponential backoff. For example, without
    jitter, retry backoff uses roughly:

    ``t = initial_retry_delay * (backoff_factor ** attempts)``.
    """

    max_retry_delay: float = 8.0
    """Maximum amount of time to wait between 2 retries (in seconds).

    This caps the backoff delay computed from ``initial_retry_delay`` and
    ``backoff_factor``.
    """

    backoff_factor: float = 2.0
    """Back-off factor to increase the amount of time between 2 retries: t(n+1) = backoff_factor * t(n)"""

    jitter: Optional[
        Literal[
            "equal",
            "full",
            "full_and_equal_for_throttle",
            "decorrelated",
        ]
    ] = "full_and_equal_for_throttle"
    """Method to add randomness to the retry time. Supported methods are:

    - None: t = min(initial_retry_delay * (backoff_factor ** attempts), max_retry_delay)
    - full: t = min(random(0, initial_retry_delay * (backoff_factor ** attempts)), max_retry_delay)
    - equal: t = min(initial_retry_delay * (backoff_factor ** attempts), max_retry_delay) * (1 + random(0, 1)) / 2)
    - full_and_equal_for_throttle: full for 5xx errors and equal for 4xx errors
    - decorrelated: t = min(initial_retry_delay * (backoff_factor ** attempts) + random(0, 1), max_retry_delay)
    """

    service_error_retry_on_any_5xx: bool = True
    """Whether to retry on all 5xx errors (network errors, except 501)"""

    # Note: The Agent Spec deserializer currently supports only `dict[str, ...]`
    # keys (JSON-compatible), so we use `str` keys here.
    recoverable_statuses: Dict[str, List[str]] = Field(
        default_factory=lambda: {
            "409": cast(List[str], []),
            "429": cast(List[str], []),
        }
    )
    """Some additional statuses considered as recoverable.

    By default retries on:

    - 409: conflict
    - 429: throttling (retry after x time)

    Note: keys are represented as strings because Agent Spec configurations must be
    valid JSON (object keys are strings).
    """
