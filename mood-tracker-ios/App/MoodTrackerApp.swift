import SwiftUI

@main
struct MoodTrackerApp: App {
    // Inject the shared MoodManager
    @StateObject private var moodManager = MoodManager.shared
    
    var body: some Scene {
        WindowGroup {
            if moodManager.currentUser != nil {
                HomeView()
                    .environmentObject(moodManager)
            } else {
                LoginView()
                    .environmentObject(moodManager)
            }
        }
    }
}
