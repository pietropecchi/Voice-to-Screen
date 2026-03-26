import Foundation

protocol PipelineClient {
    func startSession(config: SessionConfig) async throws
    func stopSession() async
    func captionsStream() -> AsyncStream<[CaptionSegment]>
}

actor MockPipelineClient: PipelineClient {
    private let sampleBatches: [[CaptionSegment]] = [
        [
            CaptionSegment(
                speakerLabel: "Speaker 1",
                sourceText: "Kore wa mada tesuto no dankai desu.",
                translatedText: "This is still in the testing phase.",
                status: .draft
            ),
        ],
        [
            CaptionSegment(
                speakerLabel: "Speaker 1",
                sourceText: "Kore wa mada tesuto no dankai desu.",
                translatedText: "This is still in the testing phase.",
                status: .final
            ),
            CaptionSegment(
                speakerLabel: "Speaker 2",
                sourceText: "Demo jikkou wa mou sugu hajimarimasu.",
                translatedText: "But execution will begin very soon.",
                status: .revised
            ),
        ],
    ]

    func startSession(config: SessionConfig) async throws {
        _ = config
    }

    func stopSession() async {}

    func captionsStream() -> AsyncStream<[CaptionSegment]> {
        AsyncStream { continuation in
            Task {
                for batch in sampleBatches {
                    continuation.yield(batch)
                    try? await Task.sleep(for: .seconds(2))
                }
                continuation.finish()
            }
        }
    }
}
