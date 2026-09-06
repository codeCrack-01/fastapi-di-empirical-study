# DI-style runtime micro-benchmark

- Synthetic apps: 40 endpoints each, 1500 requests/app over ASGI (no network, no disk).

| style | median req | p95 | vs. fastest |
|---|---|---|---|
| bare (Depends(fn)) | 581 us | 1148 us | 1.51x |
| class (Depends(Cls)) | 632 us | 1250 us | 1.64x |
| request-scoped current_* | 683 us | 1294 us | 1.78x |
| zero-DI (direct call) | 385 us | 622 us | 1.00x |

**Honest conclusion:** in this minimal synthetic setup the three `Depends()` styles carry an extra 0.25 ms per request vs. the zero-DI baseline (geometric-mean 1.64x). The DI resolver (parameter matching + dependency construction) is therefore real, not free — but a single DB round-trip (~1-10 ms) dwarfs it, so the overhead is negligible against realistic handler work. Run-to-run variance is high, so treat the ratio as an order-of-magnitude upper bound on a body doing nothing, not a production number.

Fastest style (smallest best-of-3 median): **zero-DI (direct call)**.
