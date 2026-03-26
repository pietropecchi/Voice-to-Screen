import SwiftUI

struct OverlayWindowView: View {
    @ObservedObject var viewModel: OverlayViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            header
            controls
            captionFeed
        }
        .padding(20)
        .frame(minWidth: 680, minHeight: 420)
        .background(.ultraThinMaterial.opacity(viewModel.config.overlayOpacity))
        .clipShape(RoundedRectangle(cornerRadius: 24, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 24, style: .continuous)
                .stroke(Color.white.opacity(0.14), lineWidth: 1)
        )
        .padding()
    }

    private var header: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text("Voice-to-Screen")
                    .font(.system(size: 24, weight: .semibold, design: .rounded))
                Text("Local live translation overlay")
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Button(viewModel.isRunning ? "Stop" : "Start") {
                viewModel.toggleSession()
            }
            .buttonStyle(.borderedProminent)
        }
    }

    private var controls: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Picker("Input", selection: $viewModel.config.sourceLanguage) {
                    ForEach(SourceLanguage.allCases) { language in
                        Text(language.displayName).tag(language)
                    }
                }

                Picker("Model", selection: $viewModel.config.modelTier) {
                    ForEach(ModelTier.allCases) { tier in
                        Text(tier.displayName).tag(tier)
                    }
                }
            }

            HStack {
                Toggle("Compact mode", isOn: $viewModel.config.compactMode)
                Toggle("Speaker labels", isOn: $viewModel.config.speakerLabelsEnabled)
                Toggle("Experimental gender hints", isOn: $viewModel.config.genderHintsEnabled)
            }

            HStack {
                Text("Opacity")
                Slider(value: $viewModel.config.overlayOpacity, in: 0.35...0.95)
            }
        }
    }

    private var captionFeed: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 12) {
                ForEach(viewModel.captions) { caption in
                    VStack(alignment: .leading, spacing: 6) {
                        if viewModel.config.speakerLabelsEnabled {
                            Text(caption.speakerLabel)
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(.secondary)
                        }

                        if !viewModel.config.compactMode {
                            Text(caption.sourceText)
                                .font(.body)
                                .foregroundStyle(.primary.opacity(0.86))
                        }

                        Text(caption.translatedText)
                            .font(.title3.weight(.medium))
                            .foregroundStyle(.white)

                        Text(caption.status.rawValue.uppercased())
                            .font(.caption2.monospaced())
                            .foregroundStyle(statusColor(caption.status))
                    }
                    .padding(14)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.black.opacity(0.18))
                    .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
                }
            }
        }
    }

    private func statusColor(_ status: CaptionSegment.Status) -> Color {
        switch status {
        case .draft:
            return .yellow
        case .revised:
            return .orange
        case .final:
            return .green
        }
    }
}
