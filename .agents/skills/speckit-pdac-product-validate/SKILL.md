---
name: speckit-pdac-product-validate
description: Validate one ProductShape Product Change deterministically as an overlay.
compatibility: Requires spec-kit project structure with .specify/ directory
metadata:
  author: juangcarmona
  source: pdac-product:commands/speckit.pdac-product.validate.md
---

# Validate Product Change

Run `prodshape speckit-product validate <name> --format json` from the locally installed CLI. It must re-read `docs/product/model`, the complete proposed future state, and all other live Product Changes. Report sorted diagnostics and unresolved questions. Validation is advisory preflight only; apply must repeat it at execution time.