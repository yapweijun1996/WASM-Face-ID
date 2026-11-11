# Repository Guidelines

## Project Status and Architecture

`wasm-face-id` is a planned browser-based face recognition SDK, not yet a verified product. Keep the SDK independent of attendance, HRMS, and ERP business rules. The proposed architecture uses a TypeScript API, ONNX Runtime Web for detection and embeddings, and Rust compiled to WebAssembly for vector processing and matching. Treat WebGPU as optional; the intended default is a WASM CPU backend.

## Project Structure

The repository currently contains no source packages or tests. The proposed monorepo places the browser demo in `apps/web-demo/`, the TypeScript SDK in `packages/core/`, Rust code in `packages/wasm-core/`, model integration in `packages/model-runtime/`, and benchmark tooling in `packages/benchmark/`. Use `models/` for model documentation and `datasets/` for dataset manifests. Introduce directories when they have a clear owner and purpose.

## Build, Test, and Development

No build system or executable commands are configured yet. When adding the proposed pnpm and Cargo workspaces, document the actual install, build, test, and demo commands in `README.md` and CI. Verify the commands from a clean checkout; do not present planned commands as working features.

## Coding and Testing

Write code, comments, identifiers, and technical documentation in English. Follow the formatting and naming conventions established by each package; configure standard Rust and TypeScript formatters when those packages are introduced. Keep public APIs explicit and avoid coupling model-specific preprocessing to business workflows.

Add focused tests alongside new behavior, including vector normalization, matching thresholds, unknown identities, and error handling. Test the full browser pipeline when models are available. Define dataset splits, metrics, and reproducible benchmark procedures before reporting accuracy, FAR, FRR, latency, or memory results. Do not treat planned benchmarks as verified results.

## Security and Model Licensing

Face images and embeddings are sensitive. Minimize retention, protect stored templates, and never commit personal biometric data or credentials. Document model provenance and separately verify code, weights, and training-data rights before commercial use. Browser-side matching alone must not be presented as a secure attendance authorization mechanism.

## Commits and Pull Requests

Git history currently contains only `Initial commit`; no established commit convention can be inferred. Use concise, imperative commit subjects. Pull requests should explain the change, its motivation, test evidence, and relevant issues; include screenshots for visible demo changes and disclose model or privacy implications.
