import SwiftUI

@main
struct VoiceToScreenApp: App {
    @StateObject private var viewModel = OverlayViewModel()

    var body: some Scene {
        WindowGroup {
            OverlayWindowView(viewModel: viewModel)
        }
        .windowResizability(.contentSize)
    }
}
