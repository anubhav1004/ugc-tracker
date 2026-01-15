import SwiftUI

struct LoginView: View {
    @EnvironmentObject var moodManager: MoodManager
    @State private var username: String = ""
    
    var body: some View {
        VStack(spacing: 20) {
            Text("Welcome to MoodTracker")
                .font(.largeTitle)
                .fontWeight(.bold)
            
            Text("Share your vibe with friends.")
                .font(.subheadline)
                .foregroundColor(.secondary)
            
            TextField("Enter your username", text: $username)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .padding(.horizontal)
                .autocapitalization(.none)
            
            Button(action: {
                if !username.isEmpty {
                    moodManager.currentUser = username
                }
            }) {
                Text("Start Tracking")
                    .font(.headline)
                    .foregroundColor(.white)
                    .padding()
                    .frame(maxWidth: .infinity)
                    .background(Color.blue)
                    .cornerRadius(10)
            }
            .padding(.horizontal)
            .disabled(username.isEmpty)
        }
        .padding()
    }
}
