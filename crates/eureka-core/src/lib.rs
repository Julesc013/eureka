#![forbid(unsafe_code)]
#![doc = "Core domain candidates for Eureka's Rust backend parity lane."]

pub mod query_planner;
pub mod source_registry;

/// Describes the current state of this crate.
///
/// Python remains the reference backend and oracle. This crate contains the
/// first isolated Rust parity candidates only; it is not wired into runtime
/// behavior.
pub const CRATE_STATUS: &str =
    "source_registry_and_query_planner_parity_candidates_v0_python_oracle_active";
