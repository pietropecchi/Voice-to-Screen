import Foundation

@MainActor
final class OverlayViewModel: ObservableObject {
    @Published var config = SessionConfig()
    @Published var isRunning = false
    @Published var captions: [CaptionSegment] = []

    private let pipelineClient: PipelineClient
    private var streamTask: Task<Void, Never>?

    init(pipelineClient: PipelineClient = MockPipelineClient()) {
        self.pipelineClient = pipelineClient
    }

    func toggleSession() {
        if isRunning {
            stop()
        } else {
            start()
        }
    }

    private func start() {
        guard !isRunning else { return }

        isRunning = true
        captions = []

        streamTask = Task {
            do {
                try await pipelineClient.startSession(config: config)
                for await update in pipelineClient.captionsStream() {
                    captions = update
                }
            } catch {
                isRunning = false
            }
        }
    }

    private func stop() {
        guard isRunning else { return }

        streamTask?.cancel()
        streamTask = nil
        isRunning = false

        Task {
            await pipelineClient.stopSession()
        }
    }
}
