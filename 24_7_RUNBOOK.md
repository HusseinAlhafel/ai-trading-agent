# 24/7 Runbook

## Current state

- Paper Trading: enabled.
- IBKR live execution: disabled.
- Plus500 live execution: not supported by this project.

## Target architecture

Market data -> strategy -> risk manager -> IBKR adapter -> order monitoring -> emergency stop.

## Hosting

A persistent server/VM or equivalent always-on host is required. The iPhone can be used for monitoring, but should not be the sole execution host.

## Safety

The process must stop on broker disconnect, stale market data, unexpected account state, risk-limit breach, repeated order rejection, or heartbeat failure.
