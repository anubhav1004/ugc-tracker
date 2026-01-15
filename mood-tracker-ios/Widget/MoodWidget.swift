import WidgetKit
import SwiftUI

// IMPORTANT: Ensure this matches the App Group ID in MoodManager.swift
let appGroupId = "group.com.example.moodtracker"

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: Date(), mood: .happy, username: "You")
    }

    func getSnapshot(in context: Context, completion: @escaping (SimpleEntry) -> ()) {
        let entry = getLatestMoodEntry()
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> ()) {
        let entry = getLatestMoodEntry()
        
        // Refresh every 15 minutes, or whenever the app forces a reload
        let nextUpdateDate = Calendar.current.date(byAdding: .minute, value: 15, to: Date())!
        let timeline = Timeline(entries: [entry], policy: .after(nextUpdateDate))
        completion(timeline)
    }
    
    private func getLatestMoodEntry() -> SimpleEntry {
        let userDefaults = UserDefaults(suiteName: appGroupId)
        
        if let data = userDefaults?.data(forKey: "myLatestMood"),
           let moodEntry = try? JSONDecoder().decode(MoodEntry.self, from: data) {
            return SimpleEntry(date: Date(), mood: moodEntry.mood, username: "You")
        }
        
        return SimpleEntry(date: Date(), mood: .happy, username: "You") // Default/Fallback
    }
}

struct SimpleEntry: TimelineEntry {
    let date: Date
    let mood: Mood
    let username: String
}

struct MoodWidgetEntryView : View {
    var entry: Provider.Entry

    var body: some View {
        ZStack {
            ContainerRelativeShape()
                .fill(entry.mood.color.opacity(0.2))
            
            VStack(spacing: 8) {
                Text(entry.username)
                    .font(.caption)
                    .fontWeight(.bold)
                    .foregroundColor(.secondary)
                
                Text(entry.mood.emoji)
                    .font(.system(size: 40))
                
                Text(entry.mood.title)
                    .font(.caption2)
                    .fontWeight(.medium)
                    .foregroundColor(entry.mood.color)
            }
            .padding()
        }
    }
}

@main
struct MoodWidget: Widget {
    let kind: String = "MoodWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            MoodWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("My Mood")
        .description("Shows your current mood.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}

// Preview Provider
struct MoodWidget_Previews: PreviewProvider {
    static var previews: some View {
        MoodWidgetEntryView(entry: SimpleEntry(date: Date(), mood: .excited, username: "You"))
            .previewContext(WidgetPreviewContext(family: .systemSmall))
    }
}
