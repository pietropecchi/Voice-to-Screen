# Shared Schemas

These schemas define the transport contract between the macOS app and the local pipeline service.

The first milestone should keep the transport simple:

- JSON messages
- line-delimited over `stdio`
- stable event names
- patch-friendly segment identifiers
