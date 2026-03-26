import Foundation

enum SourceLanguage: String, CaseIterable, Identifiable, Codable {
    case english
    case italian
    case chinese
    case japanese

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .english:
            return "English"
        case .italian:
            return "Italian"
        case .chinese:
            return "Chinese"
        case .japanese:
            return "Japanese"
        }
    }
}

enum ModelTier: String, CaseIterable, Identifiable, Codable {
    case balanced
    case fast
    case accurate

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .balanced:
            return "Balanced"
        case .fast:
            return "Fast"
        case .accurate:
            return "Accurate"
        }
    }
}

struct SessionConfig: Codable {
    var sourceLanguage: SourceLanguage = .japanese
    var targetLanguage: String = "English"
    var modelTier: ModelTier = .balanced
    var overlayOpacity: Double = 0.84
    var compactMode = false
    var speakerLabelsEnabled = true
    var genderHintsEnabled = false
}

struct CaptionSegment: Identifiable, Hashable {
    enum Status: String {
        case draft
        case revised
        case final
    }

    let id: UUID
    let speakerLabel: String
    let sourceText: String
    let translatedText: String
    let status: Status

    init(
        id: UUID = UUID(),
        speakerLabel: String,
        sourceText: String,
        translatedText: String,
        status: Status
    ) {
        self.id = id
        self.speakerLabel = speakerLabel
        self.sourceText = sourceText
        self.translatedText = translatedText
        self.status = status
    }
}
