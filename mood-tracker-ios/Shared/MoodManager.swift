import Foundation
import WidgetKit

/// Manages the storage and retrieval of mood data.
/// Uses UserDefaults with App Groups to share data between the main App and the Widget.
class MoodManager: ObservableObject {
    static let shared = MoodManager()
    
    // IMPORTANT: In a real app, replace this with your actual App Group ID
    // configured in Xcode -> Signing & Capabilities -> App Groups.
    // Example: "group.com.yourname.moodtracker"
    private let appGroupId = "group.com.example.moodtracker"
    private let userDefaults: UserDefaults
    
    @Published var currentUser: String? {
        didSet {
            userDefaults.set(currentUser, forKey: "currentUser")
        }
    }
    
    @Published var myLatestMood: MoodEntry? {
        didSet {
            if let mood = myLatestMood, let data = try? JSONEncoder().encode(mood) {
                userDefaults.set(data, forKey: "myLatestMood")
                WidgetCenter.shared.reloadAllTimelines()
            }
        }
    }
    
    @Published var friendsMoods: [MoodEntry] = [] {
        didSet {
            if let data = try? JSONEncoder().encode(friendsMoods) {
                userDefaults.set(data, forKey: "friendsMoods")
            }
        }
    }

    private init() {
        // Fallback to standard UserDefaults if App Group is not set up yet
        self.userDefaults = UserDefaults(suiteName: appGroupId) ?? UserDefaults.standard
        
        self.currentUser = userDefaults.string(forKey: "currentUser")
        
        if let data = userDefaults.data(forKey: "myLatestMood"),
           let mood = try? JSONDecoder().decode(MoodEntry.self, from: data) {
            self.myLatestMood = mood
        }
        
        if let data = userDefaults.data(forKey: "friendsMoods"),
           let moods = try? JSONDecoder().decode([MoodEntry].self, from: data) {
            self.friendsMoods = moods
        } else {
            // Seed with some mock data for friends if empty
            self.friendsMoods = [
                MoodEntry(userId: "friend1", username: "Alice", mood: .happy, timestamp: Date().addingTimeInterval(-3600)),
                MoodEntry(userId: "friend2", username: "Bob", mood: .stressed, timestamp: Date().addingTimeInterval(-7200)),
                MoodEntry(userId: "friend3", username: "Charlie", mood: .excited, timestamp: Date().addingTimeInterval(-1800))
            ]
        }
    }
    
    func logMood(_ mood: Mood) {
        guard let username = currentUser else { return }
        let entry = MoodEntry(userId: UUID().uuidString, username: username, mood: mood, timestamp: Date())
        myLatestMood = entry
        
        // In a real app, you would send this to a backend here.
        print("Logged mood: \(mood.title) for user: \(username)")
    }
    
    func logout() {
        currentUser = nil
        myLatestMood = nil
    }
    
    func refreshFriends() {
        // Simulate fetching updates from backend
        // For now, just shuffle moods to show "activity"
        var newFriends = friendsMoods
        if let randomFriendIndex = newFriends.indices.randomElement() {
            let friend = newFriends[randomFriendIndex]
            newFriends[randomFriendIndex] = MoodEntry(
                userId: friend.userId,
                username: friend.username,
                mood: Mood.allCases.randomElement() ?? .happy,
                timestamp: Date()
            )
        }
        friendsMoods = newFriends
    }
}
