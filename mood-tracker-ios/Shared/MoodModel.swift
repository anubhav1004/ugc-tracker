import Foundation
import SwiftUI

/// Represents the possible moods a user can select.
enum Mood: String, CaseIterable, Codable, Identifiable {
    case happy
    case sad
    case excited
    case angry
    case relaxed
    case stressed
    case loved
    case tired
    
    var id: String { self.rawValue }
    
    var emoji: String {
        switch self {
        case .happy: return "😊"
        case .sad: return "😢"
        case .excited: return "🤩"
        case .angry: return "😡"
        case .relaxed: return "😌"
        case .stressed: return "🤯"
        case .loved: return "🥰"
        case .tired: return "😴"
        }
    }
    
    var color: Color {
        switch self {
        case .happy: return .yellow
        case .sad: return .blue
        case .excited: return .orange
        case .angry: return .red
        case .relaxed: return .green
        case .stressed: return .purple
        case .loved: return .pink
        case .tired: return .gray
        }
    }
    
    var title: String {
        rawValue.capitalized
    }
}

/// A single entry of a mood log.
struct MoodEntry: Identifiable, Codable {
    let id: UUID
    let userId: String
    let username: String
    let mood: Mood
    let timestamp: Date
    
    init(id: UUID = UUID(), userId: String, username: String, mood: Mood, timestamp: Date = Date()) {
        self.id = id
        self.userId = userId
        self.username = username
        self.mood = mood
        self.timestamp = timestamp
    }
}
