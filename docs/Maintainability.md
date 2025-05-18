# Maintainability

To ensure the solution remains **maintainable** and **extensible** as new external providers and media types are added, I would:

1.  **Introduce a provider abstraction layer** (parent class), and each new provider (child class) would inherit from it, ensuring a standard approach for data normalization, ingesting, and retrieval.
2. **Introduce a configuration-driven registration** for providers, so each provider will have a configuration file, allowing integration without code change.
3. **Normalize all incoming data** to a unified internal schema, ensuring consistent processing and API responses regardless of the source or media type.
4. **Maintain clear documentation and onboarding guides** for adding new providers or media types.