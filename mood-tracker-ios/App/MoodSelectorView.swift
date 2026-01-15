import SwiftUI

struct MoodSelectorView: View {
    @EnvironmentObject var moodManager: MoodManager
    @Environment(\.presentationMode) var presentationMode
    
    let columns = [
        GridItem(.flexible()),
        GridItem(.flexible()),
        GridItem(.flexible())
    ]
    
    var body: some View {
        NavigationView {
            ScrollView {
                LazyVGrid(columns: columns, spacing: 20) {
                    ForEach(Mood.allCases) { mood in
                        Button(action: {
                            moodManager.logMood(mood)
                            presentationMode.wrappedValue.dismiss()
                        }) {
                            VStack {
                                Text(mood.emoji)
                                    .font(.system(size: 50))
                                Text(mood.title)
                                    .font(.caption)
                                    .foregroundColor(.primary)
                            }
                            .padding()
                            .background(mood.color.opacity(0.2))
                            .cornerRadius(15)
                            .overlay(
                                RoundedRectangle(cornerRadius: 15)
                                    .stroke(mood.color, lineWidth: 2)
                            )
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("How are you feeling?")
            .navigationBarItems(trailing: Button("Cancel") {
                presentationMode.wrappedValue.dismiss()
            })
        }
    }
}
