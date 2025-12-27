# Mobile Architecture Styles

## Table of Contents

- [Overview](#overview)
- [1. Native Mobile Architecture](#1-native-mobile-architecture)
- [2. Cross-Platform Architecture](#2-cross-platform-architecture)
- [3. Offline-First Architecture](#3-offline-first-architecture)
- [Architecture Comparison](#architecture-comparison)
- [Decision Guide](#decision-guide)
- [References](#references)

---

## Overview

Mobile architecture styles define how mobile applications are structured, how they interact with backend services, and how they handle the unique constraints of mobile environments. Choosing the right mobile architecture impacts:

- **Performance** - App responsiveness, battery life, and resource usage
- **User Experience** - Native feel, offline capabilities, and smooth interactions
- **Development Efficiency** - Code sharing, team skills, and time to market
- **Maintainability** - Code organization, testing, and long-term support
- **Platform Coverage** - iOS, Android, and other platforms

---

## 1. Native Mobile Architecture

### Definition

**Native Mobile Architecture** involves building applications specifically for each platform (iOS, Android) using platform-specific languages, frameworks, and tools.

### Platform Technologies

| Platform | Languages | UI Framework | IDE |
|----------|-----------|--------------|-----|
| **iOS** | Swift, Objective-C | SwiftUI, UIKit | Xcode |
| **Android** | Kotlin, Java | Jetpack Compose, XML Views | Android Studio |

### Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│              Native Mobile Architecture Patterns                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. MVC (Model-View-Controller) - Traditional iOS                   │
│     ┌─────────┐    ┌─────────┐    ┌─────────┐                      │
│     │  View   │◄──►│Controller│◄──►│  Model  │                      │
│     │ (UIKit) │    │(UIView- │    │ (Data)  │                      │
│     │         │    │Controller│    │         │                      │
│     └─────────┘    └─────────┘    └─────────┘                      │
│     - Simple for small apps                                         │
│     - Massive View Controller problem                               │
│                                                                      │
│  2. MVVM (Model-View-ViewModel) - SwiftUI, Jetpack Compose         │
│     ┌─────────┐    ┌─────────┐    ┌─────────┐                      │
│     │  View   │───►│ViewModel│───►│  Model  │                      │
│     │(SwiftUI)│◄───│ (State) │◄───│ (Data)  │                      │
│     │         │    │         │    │         │                      │
│     └─────────┘    └─────────┘    └─────────┘                      │
│     - Data binding                                                  │
│     - Testable ViewModels                                           │
│     - Reactive updates                                              │
│                                                                      │
│  3. MVP (Model-View-Presenter) - Android Traditional               │
│     ┌─────────┐    ┌─────────┐    ┌─────────┐                      │
│     │  View   │◄──►│Presenter│◄──►│  Model  │                      │
│     │(Activity│    │ (Logic) │    │ (Data)  │                      │
│     │/Fragment│    │         │    │         │                      │
│     └─────────┘    └─────────┘    └─────────┘                      │
│     - Passive View                                                  │
│     - Testable Presenters                                           │
│                                                                      │
│  4. Clean Architecture / VIPER                                      │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │                    Presentation                          │    │
│     │  View ◄──► Presenter/ViewModel                          │    │
│     └─────────────────────────────────────────────────────────┘    │
│                              │                                       │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │                      Domain                              │    │
│     │  Use Cases / Interactors                                 │    │
│     └─────────────────────────────────────────────────────────┘    │
│                              │                                       │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │                       Data                               │    │
│     │  Repositories, Data Sources, APIs                        │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### MVVM with SwiftUI Example

```swift
// Model
struct User: Codable, Identifiable {
    let id: String
    let name: String
    let email: String
}

// ViewModel
@MainActor
class UserListViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let userRepository: UserRepositoryProtocol
    
    init(userRepository: UserRepositoryProtocol = UserRepository()) {
        self.userRepository = userRepository
    }
    
    func loadUsers() async {
        isLoading = true
        errorMessage = nil
        
        do {
            users = try await userRepository.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
        
        isLoading = false
    }
}

// View
struct UserListView: View {
    @StateObject private var viewModel = UserListViewModel()
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    Text(error)
                } else {
                    List(viewModel.users) { user in
                        UserRow(user: user)
                    }
                }
            }
            .navigationTitle("Users")
            .task {
                await viewModel.loadUsers()
            }
        }
    }
}
```

### MVVM with Jetpack Compose Example

```kotlin
// Model
data class User(
    val id: String,
    val name: String,
    val email: String
)

// ViewModel
class UserListViewModel(
    private val userRepository: UserRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()
    
    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            
            userRepository.fetchUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(users = users, isLoading = false) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(error = error.message, isLoading = false) }
                }
        }
    }
}

data class UserListUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// View (Composable)
@Composable
fun UserListScreen(
    viewModel: UserListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    
    LaunchedEffect(Unit) {
        viewModel.loadUsers()
    }
    
    Scaffold(
        topBar = { TopAppBar(title = { Text("Users") }) }
    ) { padding ->
        when {
            uiState.isLoading -> CircularProgressIndicator()
            uiState.error != null -> Text(uiState.error!!)
            else -> LazyColumn(modifier = Modifier.padding(padding)) {
                items(uiState.users) { user ->
                    UserRow(user = user)
                }
            }
        }
    }
}
```

### Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Clean Architecture for Mobile                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Presentation Layer                        │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│   │  │    Views    │  │  ViewModels │  │    UI Models        │  │   │
│   │  │  (SwiftUI/  │  │ (Presenters)│  │    (Display Data)   │  │   │
│   │  │  Compose)   │  │             │  │                     │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                      Domain Layer                            │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│   │  │  Use Cases  │  │  Entities   │  │  Repository         │  │   │
│   │  │(Interactors)│  │ (Business   │  │  Interfaces         │  │   │
│   │  │             │  │  Objects)   │  │                     │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                       Data Layer                             │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│   │  │ Repository  │  │ Data Sources│  │    Data Models      │  │   │
│   │  │  Impl       │  │ (Remote/    │  │    (DTOs, Entities) │  │   │
│   │  │             │  │  Local)     │  │                     │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   Dependency Rule: Dependencies point INWARD                        │
│   Presentation → Domain ← Data                                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Advantages

- ✅ Best performance and user experience
- ✅ Full access to platform APIs and features
- ✅ Native look and feel
- ✅ Better app store optimization
- ✅ Smaller app size
- ✅ Latest platform features immediately

### Disadvantages

- ❌ Separate codebases for iOS and Android
- ❌ Higher development cost
- ❌ Requires platform-specific expertise
- ❌ Longer time to market
- ❌ Difficult to maintain feature parity

### When to Use

- Performance-critical applications (games, video)
- Apps requiring deep platform integration
- When native UX is paramount
- Large budget and dedicated platform teams
- Apps using platform-specific features extensively

---

## 2. Cross-Platform Architecture

### Definition

**Cross-Platform Architecture** enables building mobile applications from a single codebase that runs on multiple platforms (iOS, Android, and sometimes Web).

### Framework Comparison

| Framework | Language | UI Approach | Company |
|-----------|----------|-------------|---------|
| **React Native** | JavaScript/TypeScript | Native components | Meta |
| **Flutter** | Dart | Custom rendering (Skia) | Google |
| **Kotlin Multiplatform** | Kotlin | Native UI, shared logic | JetBrains |
| **Xamarin/MAUI** | C# | Native controls | Microsoft |
| **Capacitor/Ionic** | JS/TS | WebView | Ionic |

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│              Cross-Platform Architecture Approaches                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. React Native / Flutter (Shared UI + Logic)                      │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │                 Shared Codebase                          │    │
│     │  ┌─────────────────────────────────────────────────┐    │    │
│     │  │           UI Components + Business Logic         │    │    │
│     │  │                (90-95% shared)                   │    │    │
│     │  └─────────────────────────────────────────────────┘    │    │
│     │                     │                     │              │    │
│     │              ┌──────┴──────┐       ┌──────┴──────┐      │    │
│     │              │   iOS App   │       │ Android App │      │    │
│     │              │  (Native    │       │  (Native    │      │    │
│     │              │   Bridge)   │       │   Bridge)   │      │    │
│     │              └─────────────┘       └─────────────┘      │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  2. Kotlin Multiplatform (Shared Logic, Native UI)                  │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │              Shared Kotlin Module                        │    │
│     │  ┌─────────────────────────────────────────────────┐    │    │
│     │  │    Business Logic, Data Layer, Networking       │    │    │
│     │  │              (50-70% shared)                     │    │    │
│     │  └─────────────────────────────────────────────────┘    │    │
│     │                     │                     │              │    │
│     │              ┌──────┴──────┐       ┌──────┴──────┐      │    │
│     │              │  iOS App    │       │ Android App │      │    │
│     │              │  (SwiftUI)  │       │ (Compose)   │      │    │
│     │              │  Native UI  │       │ Native UI   │      │    │
│     │              └─────────────┘       └─────────────┘      │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  3. WebView/Hybrid (Capacitor, Ionic)                               │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │                 Web Application                          │    │
│     │  ┌─────────────────────────────────────────────────┐    │    │
│     │  │        HTML/CSS/JS (React, Angular, Vue)        │    │    │
│     │  │                 (100% shared)                    │    │    │
│     │  └─────────────────────────────────────────────────┘    │    │
│     │                     │                     │              │    │
│     │              ┌──────┴──────┐       ┌──────┴──────┐      │    │
│     │              │  iOS App    │       │ Android App │      │    │
│     │              │  (WKWebView)│       │  (WebView)  │      │    │
│     │              │  + Plugins  │       │  + Plugins  │      │    │
│     │              └─────────────┘       └─────────────┘      │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### React Native Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                   React Native Architecture                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   JavaScript Thread              Native Thread                      │
│   ┌─────────────────────┐       ┌─────────────────────┐            │
│   │                     │       │                     │            │
│   │  React Components   │       │   Native Modules    │            │
│   │  ┌───────────────┐  │       │  ┌───────────────┐  │            │
│   │  │ <View>        │  │       │  │ UIView /      │  │            │
│   │  │ <Text>        │  │       │  │ Android View  │  │            │
│   │  │ <Image>       │  │       │  └───────────────┘  │            │
│   │  └───────────────┘  │       │                     │            │
│   │                     │       │  Platform APIs      │            │
│   │  Business Logic     │       │  ┌───────────────┐  │            │
│   │  ┌───────────────┐  │       │  │ Camera        │  │            │
│   │  │ State Mgmt    │  │       │  │ Location      │  │            │
│   │  │ API Calls     │  │       │  │ Push Notif    │  │            │
│   │  └───────────────┘  │       │  └───────────────┘  │            │
│   │                     │       │                     │            │
│   └──────────┬──────────┘       └──────────┬──────────┘            │
│              │                             │                        │
│              │    ┌─────────────────┐      │                        │
│              └───►│   JSI / Bridge  │◄─────┘                        │
│                   │ (Communication) │                               │
│                   └─────────────────┘                               │
│                                                                      │
│   New Architecture (JSI - JavaScript Interface)                     │
│   • Direct native calls without serialization                       │
│   • Concurrent rendering with Fabric                                │
│   • TurboModules for lazy native module loading                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### React Native Example

```typescript
// React Native with TypeScript
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator } from 'react-native';

interface User {
  id: string;
  name: string;
  email: string;
}

const UserListScreen: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await fetch('https://api.example.com/users');
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError('Failed to load users');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <ActivityIndicator size="large" />;
  if (error) return <Text style={styles.error}>{error}</Text>;

  return (
    <FlatList
      data={users}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <View style={styles.userRow}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.email}>{item.email}</Text>
        </View>
      )}
    />
  );
};

const styles = StyleSheet.create({
  userRow: { padding: 16, borderBottomWidth: 1, borderBottomColor: '#eee' },
  name: { fontSize: 16, fontWeight: 'bold' },
  email: { fontSize: 14, color: '#666' },
  error: { color: 'red', textAlign: 'center', marginTop: 20 },
});

export default UserListScreen;
```

### Flutter Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Flutter Architecture                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Dart Application                          │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │              Widget Tree (UI)                        │    │   │
│   │  │     StatelessWidget / StatefulWidget                 │    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │            State Management                          │    │   │
│   │  │   Provider / Riverpod / Bloc / GetX                  │    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │              Business Logic                          │    │   │
│   │  │        Repositories, Services, Models               │    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   ┌──────────────────────────┴──────────────────────────────────┐   │
│   │                    Flutter Engine (C++)                      │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│   │  │   Skia      │  │    Dart     │  │     Platform        │  │   │
│   │  │ (Rendering) │  │   Runtime   │  │     Channels        │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│   ┌──────────────────────────┴──────────────────────────────────┐   │
│   │                   Platform Embedder                          │   │
│   │              iOS (Metal) / Android (OpenGL/Vulkan)          │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
│   Key: Flutter draws its own pixels (doesn't use native widgets)   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Flutter Example

```dart
// Flutter with Riverpod
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Model
class User {
  final String id;
  final String name;
  final String email;
  
  User({required this.id, required this.name, required this.email});
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
}

// Repository
class UserRepository {
  Future<List<User>> fetchUsers() async {
    final response = await http.get(Uri.parse('https://api.example.com/users'));
    final List<dynamic> data = jsonDecode(response.body);
    return data.map((json) => User.fromJson(json)).toList();
  }
}

// Providers
final userRepositoryProvider = Provider((ref) => UserRepository());

final usersProvider = FutureProvider<List<User>>((ref) async {
  final repository = ref.read(userRepositoryProvider);
  return repository.fetchUsers();
});

// UI
class UserListScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usersAsync = ref.watch(usersProvider);
    
    return Scaffold(
      appBar: AppBar(title: Text('Users')),
      body: usersAsync.when(
        loading: () => Center(child: CircularProgressIndicator()),
        error: (err, stack) => Center(child: Text('Error: $err')),
        data: (users) => ListView.builder(
          itemCount: users.length,
          itemBuilder: (context, index) {
            final user = users[index];
            return ListTile(
              title: Text(user.name),
              subtitle: Text(user.email),
            );
          },
        ),
      ),
    );
  }
}
```

### Kotlin Multiplatform (KMP)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Kotlin Multiplatform Architecture                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Shared Module (commonMain)                │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │              Domain Layer                            │    │   │
│   │  │   • Entities    • Use Cases    • Repository Interfaces │  │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │               Data Layer                             │    │   │
│   │  │   • Repository Impl  • DTOs  • Network Client (Ktor)│    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │             Shared ViewModels                        │    │   │
│   │  │   • KMM-ViewModel  • StateFlow  • Business Logic    │    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   └─────────────────────────────────────────────────────────────┘   │
│              │                                       │               │
│   ┌──────────┴──────────┐             ┌──────────────┴──────────┐   │
│   │   iosMain          │             │       androidMain        │   │
│   │  Platform-specific │             │    Platform-specific     │   │
│   │  implementations   │             │    implementations       │   │
│   └──────────┬──────────┘             └──────────────┬──────────┘   │
│              │                                       │               │
│   ┌──────────┴──────────┐             ┌──────────────┴──────────┐   │
│   │    iOS App         │             │      Android App         │   │
│   │   (SwiftUI)        │             │   (Jetpack Compose)      │   │
│   │   Native UI        │             │     Native UI            │   │
│   └─────────────────────┘             └─────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Advantages

- ✅ Single codebase reduces development time
- ✅ Easier to maintain feature parity
- ✅ Lower development cost
- ✅ Shared business logic across platforms
- ✅ Faster time to market
- ✅ Unified team and skillset

### Disadvantages

- ❌ Performance may not match native
- ❌ Platform-specific features require bridges
- ❌ Framework updates can break apps
- ❌ Larger app size (framework overhead)
- ❌ May not feel 100% native
- ❌ Debugging can be complex

### When to Use

- Limited budget or small team
- Content-focused apps (not performance-critical)
- MVP or proof of concept
- Apps with mostly shared logic
- When time to market is critical

---

## 3. Offline-First Architecture

### Definition

**Offline-First Architecture** designs applications to work seamlessly without network connectivity, treating the network as an enhancement rather than a requirement.

### Core Principles

```
┌─────────────────────────────────────────────────────────────────────┐
│               Offline-First Architecture Principles                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Local-First Data                                                │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  • Store data locally FIRST                              │    │
│     │  • UI reads from local database                          │    │
│     │  • Sync with server in background                        │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  2. Optimistic Updates                                              │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  • Apply changes immediately to local state              │    │
│     │  • Show success to user instantly                        │    │
│     │  • Sync with server asynchronously                       │    │
│     │  • Handle conflicts if server rejects                    │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  3. Conflict Resolution                                             │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  • Last-write-wins                                       │    │
│     │  • Server-wins                                           │    │
│     │  • Client-wins                                           │    │
│     │  • Merge (CRDT-based)                                    │    │
│     │  • User-mediated                                         │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  4. Background Sync                                                 │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  • Queue operations when offline                         │    │
│     │  • Retry with exponential backoff                        │    │
│     │  • Sync when connectivity restored                       │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Offline-First Architecture                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                        UI Layer                              │   │
│   │                 (Reactive to Local State)                    │   │
│   └──────────────────────────┬──────────────────────────────────┘   │
│                              │                                       │
│                              ▼                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    Repository Layer                          │   │
│   │  ┌─────────────────────────────────────────────────────┐    │   │
│   │  │            Single Source of Truth                    │    │   │
│   │  │         (Always reads from local DB)                 │    │   │
│   │  └─────────────────────────────────────────────────────┘    │   │
│   └───────────┬───────────────────────────────┬─────────────────┘   │
│               │                               │                      │
│               ▼                               ▼                      │
│   ┌───────────────────────┐       ┌───────────────────────┐         │
│   │   Local Data Source   │       │  Remote Data Source   │         │
│   │  ┌─────────────────┐  │       │  ┌─────────────────┐  │         │
│   │  │   SQLite /      │  │       │  │   REST API      │  │         │
│   │  │   Realm /       │  │       │  │   GraphQL       │  │         │
│   │  │   Room          │  │       │  │   Firebase      │  │         │
│   │  └─────────────────┘  │       │  └─────────────────┘  │         │
│   └───────────────────────┘       └───────────────────────┘         │
│               │                               │                      │
│               │                               │                      │
│               ▼                               ▼                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                   Sync Engine                                │   │
│   │  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐  │   │
│   │  │ Pending Queue │  │    Conflict   │  │   Network       │  │   │
│   │  │  (Operations) │  │    Resolver   │  │   Monitor       │  │   │
│   │  └───────────────┘  └───────────────┘  └─────────────────┘  │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Offline-First Data Flow                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  READ Operation:                                                    │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                         │
│  │   UI    │───►│  Repo   │───►│ Local   │  Always read from local │
│  │         │◄───│         │◄───│   DB    │                         │
│  └─────────┘    └─────────┘    └─────────┘                         │
│                                     ▲                               │
│                                     │ (Background sync updates DB) │
│                                     │                               │
│                               ┌─────┴─────┐                        │
│                               │  Remote   │                        │
│                               │   API     │                        │
│                               └───────────┘                        │
│                                                                      │
│  WRITE Operation (Online):                                          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │   UI    │───►│  Repo   │───►│ Local   │───►│ Remote  │          │
│  │         │    │         │    │   DB    │    │   API   │          │
│  └─────────┘    └─────────┘    └────┬────┘    └────┬────┘          │
│       ▲                            │              │                │
│       └────────────────────────────┴──────────────┘                │
│                    Immediate UI update                              │
│                                                                      │
│  WRITE Operation (Offline):                                         │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐          │
│  │   UI    │───►│  Repo   │───►│ Local   │───►│ Pending │          │
│  │         │    │         │    │   DB    │    │  Queue  │          │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘          │
│       ▲                                            │                │
│       └────────────────────────────────────────────┘                │
│              UI updated, operation queued for sync                  │
│                                                                      │
│  When Online Again:                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐                         │
│  │ Pending │───►│  Sync   │───►│ Remote  │  Process queue          │
│  │  Queue  │    │ Engine  │    │   API   │  in order               │
│  └─────────┘    └─────────┘    └─────────┘                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Sync Strategies

| Strategy | Description | Use Case |
|----------|-------------|----------|
| **Pull-based** | Client requests updates periodically | Simple, low-frequency changes |
| **Push-based** | Server pushes updates to client | Real-time requirements |
| **Hybrid** | Pull + Push notifications | Balance of freshness and efficiency |
| **Delta Sync** | Only sync changed data | Large datasets |
| **Full Sync** | Sync entire dataset | Small datasets, simple logic |

### Conflict Resolution Strategies

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Conflict Resolution Strategies                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. Last-Write-Wins (LWW)                                           │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Client A: { name: "Alice", timestamp: 10:00 }          │    │
│     │  Client B: { name: "Bob",   timestamp: 10:05 }          │    │
│     │  Result:   { name: "Bob" }  ← Latest timestamp wins     │    │
│     │                                                          │    │
│     │  + Simple to implement                                   │    │
│     │  - Can lose data silently                                │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  2. Server-Wins                                                     │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Server version always takes precedence                  │    │
│     │  Client must accept server state                         │    │
│     │                                                          │    │
│     │  + Consistent state                                      │    │
│     │  - Client changes may be lost                            │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  3. Field-Level Merge                                               │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Client A: { name: "Alice", email: unchanged }          │    │
│     │  Client B: { name: unchanged, email: "new@email" }      │    │
│     │  Result:   { name: "Alice", email: "new@email" }        │    │
│     │                                                          │    │
│     │  + Preserves non-conflicting changes                     │    │
│     │  - Complex to implement                                  │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  4. User-Mediated                                                   │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Show conflict to user, let them decide                  │    │
│     │  "Your version" vs "Server version"                      │    │
│     │                                                          │    │
│     │  + User has control                                      │    │
│     │  - Poor UX if frequent                                   │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
│  5. CRDTs (Conflict-free Replicated Data Types)                    │
│     ┌─────────────────────────────────────────────────────────┐    │
│     │  Data structures that automatically merge                │    │
│     │  G-Counter, LWW-Register, OR-Set                        │    │
│     │                                                          │    │
│     │  + Automatic, mathematically sound                       │    │
│     │  - Limited data types, complex                           │    │
│     └─────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation Example (Repository Pattern)

```kotlin
// Android with Room + Retrofit
class TaskRepository(
    private val localDataSource: TaskLocalDataSource,
    private val remoteDataSource: TaskRemoteDataSource,
    private val syncManager: SyncManager
) {
    // Single source of truth: always read from local
    fun getTasks(): Flow<List<Task>> = localDataSource.getTasks()
    
    // Offline-first write
    suspend fun createTask(task: Task): Result<Task> {
        // 1. Save locally first (optimistic)
        val localTask = task.copy(
            syncStatus = SyncStatus.PENDING,
            localId = UUID.randomUUID().toString()
        )
        localDataSource.insert(localTask)
        
        // 2. Queue for sync
        syncManager.queueOperation(
            SyncOperation.Create(localTask)
        )
        
        // 3. Try to sync immediately if online
        if (networkMonitor.isOnline()) {
            syncManager.syncNow()
        }
        
        return Result.success(localTask)
    }
    
    suspend fun syncWithServer() {
        // Pull remote changes
        val remoteChanges = remoteDataSource.getChangesSince(lastSyncTimestamp)
        
        // Merge with local
        remoteChanges.forEach { remoteTask ->
            val localTask = localDataSource.getById(remoteTask.id)
            val resolved = conflictResolver.resolve(localTask, remoteTask)
            localDataSource.upsert(resolved)
        }
        
        // Push local changes
        val pendingOperations = syncManager.getPendingOperations()
        pendingOperations.forEach { operation ->
            try {
                remoteDataSource.execute(operation)
                syncManager.markSynced(operation)
            } catch (e: ConflictException) {
                handleConflict(operation, e.serverVersion)
            }
        }
    }
}

// Sync Status tracking
enum class SyncStatus {
    SYNCED,     // In sync with server
    PENDING,    // Waiting to be synced
    CONFLICT,   // Conflict detected
    ERROR       // Sync failed
}
```

### Advantages

- ✅ Works without network connectivity
- ✅ Instant UI responsiveness
- ✅ Reduced server load
- ✅ Better user experience in poor network conditions
- ✅ Data available immediately on app start
- ✅ Lower data usage

### Disadvantages

- ❌ Complex conflict resolution
- ❌ Data consistency challenges
- ❌ Increased storage requirements
- ❌ Complex sync logic
- ❌ Testing complexity
- ❌ Stale data risks

### When to Use

- Field service applications
- Note-taking and document apps
- Apps used in areas with poor connectivity
- Collaborative applications
- Critical data that must not be lost
- Apps requiring instant responsiveness

---

## Architecture Comparison

### Feature Comparison Matrix

| Feature | Native | Cross-Platform | Offline-First |
|---------|--------|----------------|---------------|
| **Performance** | Best | Good | Good |
| **Development Cost** | High | Low | Medium |
| **Time to Market** | Slow | Fast | Medium |
| **Offline Support** | Manual | Manual | Built-in |
| **Native Feel** | Best | Good | Varies |
| **Code Sharing** | None | High | Medium |

### Platform-Specific Considerations

| Consideration | iOS | Android |
|---------------|-----|---------|
| **Local Storage** | Core Data, Realm, SQLite | Room, Realm, SQLite |
| **Background Sync** | Background Tasks API | WorkManager |
| **Network Monitor** | NWPathMonitor | ConnectivityManager |
| **Push Notifications** | APNs | FCM |

**Abbreviations:**
- **APNs** - Apple Push Notification service (Apple's cloud service for sending push notifications to iOS devices)
- **FCM** - Firebase Cloud Messaging (Google's cross-platform messaging solution for Android)

---

## Decision Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Mobile Architecture Decision Tree                    │
└─────────────────────────────────────────────────────────────────────┘

Start
  │
  ▼
Performance-critical (games, ──Yes──► Native (Swift/Kotlin)
video, AR/VR)?
  │
  No
  │
  ▼
Must work offline reliably? ──Yes──► Offline-First + any platform
  │
  No
  │
  ▼
Limited budget / small team? ──Yes──► Cross-Platform (Flutter/RN)
  │
  No
  │
  ▼
Need native UX but share ──Yes──► Kotlin Multiplatform
business logic?
  │
  No
  │
  ▼
Complex animations / ──Yes──► Flutter (custom rendering)
custom UI?
  │
  No
  │
  ▼
JavaScript team / web ──Yes──► React Native
background?
  │
  No
  │
  ▼
Default ────────────────────────► Cross-Platform for MVPs
                                  Native for mature products
```

---

## References

- Apple. [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
- Google. [Jetpack Compose Documentation](https://developer.android.com/jetpack/compose)
- [React Native Documentation](https://reactnative.dev/)
- [Flutter Documentation](https://flutter.dev/docs)
- [Kotlin Multiplatform](https://kotlinlang.org/docs/multiplatform.html)
- Martin Kleppmann. (2017). *Designing Data-Intensive Applications* (Chapter on Distributed Data)
- [Offline-First Web Apps](https://offlinefirst.org/)
