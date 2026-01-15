import SwiftUI

struct HomeView: View {
    @EnvironmentObject var moodManager: MoodManager
    @State private var showingMoodSelector = false
    
    var body: some View {
        NavigationView {
            VStack {
                // Header: My Status
                VStack(spacing: 12) {
                    Text("My Current Mood")
                        .font(.headline)
                        .foregroundColor(.secondary)
                    
                    if let myMood = moodManager.myLatestMood {
                        Text(myMood.mood.emoji)
                            .font(.system(size: 80))
                            .shadow(radius: 5)
                        
                        Text("I am feeling \(myMood.mood.title)")
                            .font(.title2)
                            .fontWeight(.medium)
                            .foregroundColor(myMood.mood.color)
                    } else {
                        Text("❓")
                            .font(.system(size: 80))
                        Text("Tap + to log your mood")
                            .font(.body)
                            .foregroundColor(.gray)
                    }
                    
                    Button(action: {
                        showingMoodSelector = true
                    }) {
                        Label("Update Mood", systemImage: "plus.circle.fill")
                            .font(.headline)
                            .padding(.horizontal, 20)
                            .padding(.vertical, 10)
                            .background(Color.blue.opacity(0.1))
                            .foregroundColor(.blue)
                            .cornerRadius(20)
                    }
                }
                .padding(.vertical, 30)
                
                Divider()
                
                // Friends List
                List {
                    Section(header: Text("Friends Updates")) {
                        ForEach(moodManager.friendsMoods) { friendMood in
                            HStack {
                                Text(friendMood.mood.emoji)
                                    .font(.system(size: 40))
                                    .padding(8)
                                    .background(friendMood.mood.color.opacity(0.2))
                                    .clipShape(Circle())
                                
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(friendMood.username)
                                        .font(.headline)
                                    Text("is feeling \(friendMood.mood.title)")
                                        .font(.subheadline)
                                        .foregroundColor(.secondary)
                                }
                                
                                Spacer()
                                
                                Text(timeAgo(from: friendMood.timestamp))
                                    .font(.caption2)
                                    .foregroundColor(.gray)
                            }
                            .padding(.vertical, 4)
                        }
                    }
                }
                .listStyle(InsetGroupedListStyle())
                .refreshable {
                    moodManager.refreshFriends()
                }
            }
            .navigationTitle("Mood Tracker")
            .sheet(isPresented: $showingMoodSelector) {
                MoodSelectorView()
                    .environmentObject(moodManager)
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Logout") {
                        moodManager.logout()
                    }
                }
            }
        }
    }
    
    private func timeAgo(from date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}
