# IBKR Live — Manual Approval Mode

This mode is designed for a real IBKR account without autonomous live order execution.

## Flow

1. The agent reads live account/market information.
2. The strategy produces a proposed trade.
3. The proposal includes symbol, side, quantity, order type, entry/reference price, stop-loss reference, take-profit reference, and risk checks.
4. The user reviews and explicitly approves the proposal.
5. Only after approval may the user submit the order in IBKR.

## Safety

- Never store IBKR credentials, 2FA codes, session cookies, or API keys in GitHub.
- Never enable autonomous live order submission.
- Never treat an analysis signal as an executed order.
- Keep Paper and Live configurations clearly separated.
