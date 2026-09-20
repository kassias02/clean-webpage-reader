---
name: clean-webpage-reader
description: Fetch a URL and return clean main text plus Markdown. Use when an agent needs to read a web page without raw HTML. Paid via x402, $0.01 USDC per call.
---

# Clean Webpage Reader

Base URL: https://clean-webpage-reader-production.up.railway.app

## When to use
Use this when you need the main content of a public webpage as clean text or Markdown.

## How to call
GET /read?url=https://example.com

Free health check:
GET /health

## Payment
x402 exact scheme.
Network: eip155:8453 (Base mainnet)
Price: $0.01 USDC
Pay to: 0x3FfCEdBE43De60Dcc58ebF5c737F5c47e8De59FD
If the response is HTTP 402, pay using the payment-required header and retry.
