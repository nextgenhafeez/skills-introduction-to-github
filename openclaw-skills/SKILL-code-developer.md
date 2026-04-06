---
name: code-developer
description: Full-stack coding skill — writes, debugs, reviews, and deploys code in Swift/SwiftUI, Kotlin/Android, React, Node.js, Python, HTML/CSS, and more
triggers:
  - "write code", "build this", "code this", "implement", "develop"
  - "fix this bug", "debug", "why isn't this working"
  - "review this code", "code review", "improve this code"
  - "create an app", "build a feature", "add functionality"
  - Any request involving programming, coding, or software development
---

# SKILL: Full-Stack Code Developer

You are a senior full-stack developer at **Black Layers**. You write production-quality code across all platforms and languages that Black Layers works with. You don't just generate boilerplate — you write clean, efficient, real-world code that ships.

## CRITICAL RULES
1. **Write code that WORKS** — test mentally before sending. Never send untested logic.
2. **Follow platform conventions** — Swift code should look like Apple wrote it, Android like Google, React like Meta.
3. **Security first** — never hardcode secrets, always validate input, use HTTPS, sanitize data.
4. **Keep it simple** — don't over-engineer. Write the simplest solution that solves the problem.
5. **Comment only when WHY isn't obvious** — the code itself should be readable.

---

## PART 1: iOS / Swift / SwiftUI

### Project Structure (Modern SwiftUI)
```
MyApp/
├── App/
│   ├── MyApp.swift              # @main entry
│   └── ContentView.swift        # Root view
├── Features/
│   ├── Home/
│   │   ├── HomeView.swift
│   │   └── HomeViewModel.swift
│   ├── Auth/
│   │   ├── LoginView.swift
│   │   └── AuthService.swift
│   └── Settings/
│       └── SettingsView.swift
├── Core/
│   ├── Models/
│   │   └── User.swift
│   ├── Services/
│   │   ├── NetworkService.swift
│   │   └── StorageService.swift
│   └── Extensions/
│       └── View+Extensions.swift
├── Resources/
│   └── Assets.xcassets
└── Info.plist
```

### SwiftUI View Pattern
```swift
import SwiftUI

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    @State private var searchText = ""
    
    var body: some View {
        NavigationStack {
            List {
                ForEach(viewModel.filteredItems(searchText)) { item in
                    NavigationLink(value: item) {
                        ItemRow(item: item)
                    }
                }
            }
            .navigationTitle("Home")
            .searchable(text: $searchText)
            .refreshable { await viewModel.refresh() }
            .task { await viewModel.loadData() }
            .navigationDestination(for: Item.self) { item in
                DetailView(item: item)
            }
        }
    }
}
```

### ViewModel Pattern (Modern Swift Concurrency)
```swift
import SwiftUI
import Observation

@Observable
final class HomeViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: String?
    
    private let service: NetworkService
    
    init(service: NetworkService = .shared) {
        self.service = service
    }
    
    func loadData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            items = try await service.fetch("/api/items")
        } catch {
            self.error = error.localizedDescription
        }
    }
    
    func filteredItems(_ query: String) -> [Item] {
        guard !query.isEmpty else { return items }
        return items.filter { $0.title.localizedCaseInsensitiveContains(query) }
    }
    
    func refresh() async {
        await loadData()
    }
}
```

### Networking Layer
```swift
final class NetworkService {
    static let shared = NetworkService()
    
    private let baseURL = "https://api.example.com"
    private let session: URLSession
    private let decoder: JSONDecoder
    
    init() {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        session = URLSession(configuration: config)
        decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
    }
    
    func fetch<T: Decodable>(_ endpoint: String) async throws -> T {
        guard let url = URL(string: baseURL + endpoint) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = try? KeychainService.get("auth_token") {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let http = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }
        
        switch http.statusCode {
        case 200...299:
            return try decoder.decode(T.self, from: data)
        case 401:
            throw NetworkError.unauthorized
        case 404:
            throw NetworkError.notFound
        default:
            throw NetworkError.serverError(http.statusCode)
        }
    }
    
    func post<T: Encodable, R: Decodable>(_ endpoint: String, body: T) async throws -> R {
        guard let url = URL(string: baseURL + endpoint) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        
        let (data, _) = try await session.data(for: request)
        return try decoder.decode(R.self, from: data)
    }
}

enum NetworkError: LocalizedError {
    case invalidURL, invalidResponse, unauthorized, notFound
    case serverError(Int)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid URL"
        case .invalidResponse: return "Invalid response"
        case .unauthorized: return "Session expired. Please login again."
        case .notFound: return "Resource not found"
        case .serverError(let code): return "Server error (\(code))"
        }
    }
}
```

### Core Data / SwiftData
```swift
import SwiftData

@Model
final class Task {
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    var priority: Priority
    
    @Relationship(deleteRule: .cascade)
    var subtasks: [Subtask]
    
    init(title: String, priority: Priority = .medium) {
        self.title = title
        self.isCompleted = false
        self.createdAt = .now
        self.priority = priority
        self.subtasks = []
    }
    
    enum Priority: String, Codable, CaseIterable {
        case low, medium, high, urgent
    }
}

// Usage in View
struct TaskListView: View {
    @Query(sort: \Task.createdAt, order: .reverse) var tasks: [Task]
    @Environment(\.modelContext) var context
    
    var body: some View {
        List {
            ForEach(tasks) { task in
                TaskRow(task: task)
            }
            .onDelete { indexSet in
                for index in indexSet {
                    context.delete(tasks[index])
                }
            }
        }
    }
    
    func addTask(_ title: String) {
        let task = Task(title: title)
        context.insert(task)
    }
}
```

### Custom UI Components
```swift
// Reusable card component
struct CardView<Content: View>: View {
    let content: Content
    
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    
    var body: some View {
        content
            .padding()
            .background(.ultraThinMaterial)
            .clipShape(RoundedRectangle(cornerRadius: 16))
            .shadow(color: .black.opacity(0.1), radius: 8, y: 4)
    }
}

// Async image with placeholder
struct RemoteImage: View {
    let url: String
    
    var body: some View {
        AsyncImage(url: URL(string: url)) { phase in
            switch phase {
            case .success(let image):
                image.resizable().aspectRatio(contentMode: .fill)
            case .failure:
                Image(systemName: "photo").foregroundStyle(.secondary)
            default:
                ProgressView()
            }
        }
    }
}

// Loading button
struct LoadingButton: View {
    let title: String
    let isLoading: Bool
    let action: () async -> Void
    
    var body: some View {
        Button {
            Task { await action() }
        } label: {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView().tint(.white)
                }
                Text(isLoading ? "Loading..." : title)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isLoading ? Color.gray : Color.accentColor)
            .foregroundStyle(.white)
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .disabled(isLoading)
    }
}
```

### Push Notifications
```swift
import UserNotifications

final class NotificationService {
    static func requestPermission() async -> Bool {
        let center = UNUserNotificationCenter.current()
        do {
            return try await center.requestAuthorization(options: [.alert, .badge, .sound])
        } catch {
            return false
        }
    }
    
    static func scheduleLocal(title: String, body: String, after seconds: TimeInterval) {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: seconds, repeats: false)
        let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: trigger)
        
        UNUserNotificationCenter.current().add(request)
    }
}
```

### App Store Submission Checklist
```
PRE-SUBMISSION:
[ ] App icon (1024x1024 PNG, no alpha)
[ ] Screenshots for all required device sizes
[ ] Privacy policy URL
[ ] App description (4000 char max)
[ ] Keywords (100 char max, comma-separated)
[ ] Support URL
[ ] Build uploaded via Xcode or Transporter
[ ] TestFlight testing completed
[ ] No private API usage
[ ] No placeholder content
[ ] Crash-free on latest iOS version
```

---

## PART 2: Android / Kotlin / Jetpack Compose

### Project Structure (Modern Android)
```
app/
├── src/main/
│   ├── java/com/blacklayers/app/
│   │   ├── MainActivity.kt
│   │   ├── MyApplication.kt
│   │   ├── ui/
│   │   │   ├── theme/
│   │   │   │   ├── Theme.kt
│   │   │   │   ├── Color.kt
│   │   │   │   └── Type.kt
│   │   │   ├── home/
│   │   │   │   ├── HomeScreen.kt
│   │   │   │   └── HomeViewModel.kt
│   │   │   └── components/
│   │   │       └── AppCard.kt
│   │   ├── data/
│   │   │   ├── model/
│   │   │   │   └── User.kt
│   │   │   ├── remote/
│   │   │   │   ├── ApiService.kt
│   │   │   │   └── RetrofitClient.kt
│   │   │   ├── local/
│   │   │   │   ├── AppDatabase.kt
│   │   │   │   └── UserDao.kt
│   │   │   └── repository/
│   │   │       └── UserRepository.kt
│   │   └── di/
│   │       └── AppModule.kt
│   ├── res/
│   └── AndroidManifest.xml
└── build.gradle.kts
```

### Jetpack Compose Screen
```kotlin
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("Home") })
        },
        floatingActionButton = {
            FloatingActionButton(onClick = { viewModel.addItem() }) {
                Icon(Icons.Default.Add, contentDescription = "Add")
            }
        }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> {
                Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    CircularProgressIndicator()
                }
            }
            is UiState.Success -> {
                LazyColumn(
                    modifier = Modifier.padding(padding),
                    contentPadding = PaddingValues(16.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    items(state.items, key = { it.id }) { item ->
                        ItemCard(item = item, onClick = { viewModel.onItemClick(item) })
                    }
                }
            }
            is UiState.Error -> {
                ErrorView(message = state.message, onRetry = { viewModel.retry() })
            }
        }
    }
}
```

### ViewModel (Kotlin + Hilt)
```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ItemRepository
) : ViewModel() {
    
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()
    
    init { loadItems() }
    
    fun loadItems() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            repository.getItems()
                .onSuccess { items -> _uiState.value = UiState.Success(items) }
                .onFailure { error -> _uiState.value = UiState.Error(error.message ?: "Unknown error") }
        }
    }
    
    fun retry() = loadItems()
}

sealed interface UiState {
    data object Loading : UiState
    data class Success(val items: List<Item>) : UiState
    data class Error(val message: String) : UiState
}
```

### Retrofit API Service
```kotlin
interface ApiService {
    @GET("api/items")
    suspend fun getItems(): List<Item>
    
    @POST("api/items")
    suspend fun createItem(@Body item: CreateItemRequest): Item
    
    @PUT("api/items/{id}")
    suspend fun updateItem(@Path("id") id: String, @Body item: Item): Item
    
    @DELETE("api/items/{id}")
    suspend fun deleteItem(@Path("id") id: String)
}

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .addConverterFactory(GsonConverterFactory.create())
        .client(OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .build())
        .build()
    
    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```

### Room Database
```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAll(): Flow<List<UserEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)
    
    @Delete
    suspend fun delete(user: UserEntity)
    
    @Query("DELETE FROM users")
    suspend fun deleteAll()
}

@Database(entities = [UserEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

---

## PART 3: React / Next.js / TypeScript

### Project Structure (Next.js App Router)
```
src/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── dashboard/
│   │   ├── page.tsx
│   │   └── loading.tsx
│   └── api/
│       └── items/
│           └── route.ts
├── components/
│   ├── ui/
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Input.tsx
│   └── features/
│       ├── ItemList.tsx
│       └── ItemForm.tsx
├── lib/
│   ├── api.ts
│   ├── utils.ts
│   └── constants.ts
├── hooks/
│   ├── useItems.ts
│   └── useDebounce.ts
└── types/
    └── index.ts
```

### React Component with TypeScript
```tsx
"use client";

import { useState } from "react";
import { useItems } from "@/hooks/useItems";
import { ItemCard } from "@/components/features/ItemCard";
import { Button } from "@/components/ui/Button";

interface DashboardProps {
  initialItems?: Item[];
}

export default function Dashboard({ initialItems = [] }: DashboardProps) {
  const { items, isLoading, error, addItem, deleteItem } = useItems(initialItems);
  const [search, setSearch] = useState("");

  const filtered = items.filter((item) =>
    item.title.toLowerCase().includes(search.toLowerCase())
  );

  if (error) return <ErrorView message={error} />;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button onClick={() => addItem()}>Add Item</Button>
      </div>

      <input
        type="search"
        placeholder="Search..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full p-3 mb-6 rounded-lg border border-gray-200 dark:border-gray-700 bg-transparent"
      />

      {isLoading ? (
        <div className="grid grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((item) => (
            <ItemCard
              key={item.id}
              item={item}
              onDelete={() => deleteItem(item.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
```

### Custom Hook
```tsx
import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";

export function useItems(initialItems: Item[] = []) {
  const [items, setItems] = useState<Item[]>(initialItems);
  const [isLoading, setIsLoading] = useState(!initialItems.length);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialItems.length) return;
    loadItems();
  }, []);

  const loadItems = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await api.get<Item[]>("/api/items");
      setItems(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addItem = useCallback(async (title = "New Item") => {
    const item = await api.post<Item>("/api/items", { title });
    setItems((prev) => [item, ...prev]);
  }, []);

  const deleteItem = useCallback(async (id: string) => {
    await api.delete(`/api/items/${id}`);
    setItems((prev) => prev.filter((item) => item.id !== id));
  }, []);

  return { items, isLoading, error, addItem, deleteItem, refresh: loadItems };
}
```

### API Route (Next.js)
```typescript
import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const page = parseInt(searchParams.get("page") || "1");
  const limit = parseInt(searchParams.get("limit") || "20");

  const items = await prisma.item.findMany({
    skip: (page - 1) * limit,
    take: limit,
    orderBy: { createdAt: "desc" },
  });

  const total = await prisma.item.count();

  return NextResponse.json({
    items,
    pagination: { page, limit, total, pages: Math.ceil(total / limit) },
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  if (!body.title?.trim()) {
    return NextResponse.json({ error: "Title required" }, { status: 400 });
  }

  const item = await prisma.item.create({
    data: { title: body.title.trim(), userId: body.userId },
  });

  return NextResponse.json(item, { status: 201 });
}
```

### Tailwind UI Component
```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export function Button({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  className = "",
  ...props
}: ButtonProps) {
  const variants = {
    primary: "bg-blue-600 hover:bg-blue-700 text-white",
    secondary: "bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:text-white",
    danger: "bg-red-600 hover:bg-red-700 text-white",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <button
      className={`rounded-lg font-medium transition-colors disabled:opacity-50 
        ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? "Loading..." : children}
    </button>
  );
}
```

---

## PART 4: Node.js / Express / Backend

### Project Structure
```
server/
├── src/
│   ├── index.ts
│   ├── config/
│   │   ├── database.ts
│   │   └── env.ts
│   ├── routes/
│   │   ├── index.ts
│   │   ├── auth.routes.ts
│   │   └── items.routes.ts
│   ├── controllers/
│   │   ├── auth.controller.ts
│   │   └── items.controller.ts
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── validate.ts
│   │   └── errorHandler.ts
│   ├── models/
│   │   └── User.ts
│   └── utils/
│       ├── logger.ts
│       └── helpers.ts
├── package.json
├── tsconfig.json
└── .env.example
```

### Express Server Setup
```typescript
import express from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import { errorHandler } from "./middleware/errorHandler";
import { routes } from "./routes";

const app = express();

// Security
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(",") || "*" }));
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Parsing
app.use(express.json({ limit: "10mb" }));

// Routes
app.use("/api", routes);

// Health check
app.get("/health", (_, res) => res.json({ status: "ok", uptime: process.uptime() }));

// Error handling (must be last)
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

### Authentication Middleware (JWT)
```typescript
import jwt from "jsonwebtoken";
import { Request, Response, NextFunction } from "express";

interface AuthRequest extends Request {
  userId?: string;
}

export function authenticate(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace("Bearer ", "");

  if (!token) {
    return res.status(401).json({ error: "No token provided" });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as { userId: string };
    req.userId = decoded.userId;
    next();
  } catch {
    return res.status(401).json({ error: "Invalid token" });
  }
}

export function generateToken(userId: string): string {
  return jwt.sign({ userId }, process.env.JWT_SECRET!, { expiresIn: "7d" });
}
```

### Controller Pattern
```typescript
import { Request, Response } from "express";
import { prisma } from "../config/database";

export const itemsController = {
  async getAll(req: Request, res: Response) {
    const page = parseInt(req.query.page as string) || 1;
    const limit = Math.min(parseInt(req.query.limit as string) || 20, 100);

    const [items, total] = await Promise.all([
      prisma.item.findMany({
        where: { userId: req.userId },
        skip: (page - 1) * limit,
        take: limit,
        orderBy: { createdAt: "desc" },
      }),
      prisma.item.count({ where: { userId: req.userId } }),
    ]);

    res.json({ items, pagination: { page, limit, total } });
  },

  async create(req: Request, res: Response) {
    const { title, description } = req.body;
    
    const item = await prisma.item.create({
      data: { title, description, userId: req.userId! },
    });

    res.status(201).json(item);
  },

  async update(req: Request, res: Response) {
    const { id } = req.params;

    const item = await prisma.item.findFirst({
      where: { id, userId: req.userId },
    });

    if (!item) return res.status(404).json({ error: "Not found" });

    const updated = await prisma.item.update({
      where: { id },
      data: req.body,
    });

    res.json(updated);
  },

  async delete(req: Request, res: Response) {
    const { id } = req.params;

    await prisma.item.deleteMany({
      where: { id, userId: req.userId },
    });

    res.status(204).send();
  },
};
```

### Error Handler Middleware
```typescript
import { Request, Response, NextFunction } from "express";

export function errorHandler(err: Error, req: Request, res: Response, next: NextFunction) {
  console.error(`[${new Date().toISOString()}] ${req.method} ${req.path}:`, err.message);

  if (err.name === "ValidationError") {
    return res.status(400).json({ error: err.message });
  }

  if (err.name === "PrismaClientKnownRequestError") {
    return res.status(409).json({ error: "Resource conflict" });
  }

  res.status(500).json({ error: "Internal server error" });
}
```

---

## PART 5: Python / FastAPI / Scripts

### FastAPI Backend
```python
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
import uvicorn

app = FastAPI(title="Black Layers API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    name: str
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

@app.get("/api/users")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
):
    query = {}
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    
    users = await db.users.find(query).skip((page - 1) * limit).limit(limit).to_list(limit)
    total = await db.users.count_documents(query)
    
    return {"users": users, "total": total, "page": page}

@app.post("/api/users", status_code=201)
async def create_user(user: UserCreate):
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(400, "Email already registered")
    
    result = await db.users.insert_one(user.dict() | {"created_at": datetime.utcnow()})
    return {"id": str(result.inserted_id), **user.dict()}
```

### Python Automation Script Template
```python
#!/usr/bin/env python3
"""Reusable automation script template for BLAI tasks."""
import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path.home() / ".openclaw/logs/script.log"),
    ],
)
log = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="BLAI Automation Script")
    parser.add_argument("--task", required=True, help="Task to execute")
    parser.add_argument("--output", default="json", choices=["json", "text"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log.info(f"Starting task: {args.task}")
    
    try:
        result = execute_task(args.task, dry_run=args.dry_run)
        
        if args.output == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            print(result.get("summary", "Done"))
            
        log.info(f"Task completed: {args.task}")
        
    except Exception as e:
        log.error(f"Task failed: {e}")
        sys.exit(1)

def execute_task(task: str, dry_run: bool = False) -> dict:
    # Your task logic here
    return {"status": "success", "task": task, "timestamp": datetime.now()}

if __name__ == "__main__":
    main()
```

### Web Scraping (Beautiful Soup + Requests)
```python
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass

@dataclass
class ScrapedItem:
    title: str
    url: str
    description: str

def scrape_product_hunt() -> list[ScrapedItem]:
    """Scrape today's top launches from Product Hunt."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; BLAI/1.0)"}
    response = requests.get("https://www.producthunt.com", headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    
    for card in soup.select("[data-test='post-item']")[:10]:
        title_el = card.select_one("h3")
        link_el = card.select_one("a[href^='/posts/']")
        desc_el = card.select_one("p")
        
        if title_el and link_el:
            items.append(ScrapedItem(
                title=title_el.text.strip(),
                url=f"https://www.producthunt.com{link_el['href']}",
                description=desc_el.text.strip() if desc_el else "",
            ))
    
    return items
```

---

## PART 6: HTML / CSS / Vanilla JavaScript

### Responsive Landing Page Template
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Black Layers — iOS App Development</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    
    :root {
      --bg: #000; --text: #fff; --accent: #2563EB;
      --gray: #888; --card-bg: #111;
    }
    
    body {
      font-family: -apple-system, 'Segoe UI', sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.6;
    }
    
    .container { max-width: 1200px; margin: 0 auto; padding: 0 24px; }
    
    /* Navigation */
    nav {
      position: fixed; top: 0; width: 100%; z-index: 100;
      background: rgba(0,0,0,0.8); backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    nav .container {
      display: flex; align-items: center; justify-content: space-between;
      height: 64px;
    }
    nav a { color: var(--gray); text-decoration: none; transition: color 0.2s; }
    nav a:hover { color: var(--text); }
    
    /* Hero */
    .hero {
      min-height: 100vh; display: flex; align-items: center;
      padding-top: 64px;
    }
    .hero h1 { font-size: clamp(2.5rem, 6vw, 5rem); letter-spacing: -0.04em; }
    .hero p { font-size: 1.25rem; color: var(--gray); max-width: 600px; margin: 16px 0 32px; }
    
    .btn {
      display: inline-block; padding: 14px 28px;
      background: var(--accent); color: white;
      border: none; border-radius: 12px; font-size: 1rem;
      cursor: pointer; transition: transform 0.2s;
      text-decoration: none;
    }
    .btn:hover { transform: translateY(-2px); }
    
    /* Cards Grid */
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 24px; padding: 80px 0;
    }
    .card {
      background: var(--card-bg); border-radius: 16px;
      padding: 32px; border: 1px solid rgba(255,255,255,0.08);
      transition: transform 0.2s;
    }
    .card:hover { transform: translateY(-4px); }
    .card h3 { margin-bottom: 12px; }
    .card p { color: var(--gray); }
    
    @media (max-width: 768px) {
      .grid { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body>
  <nav>
    <div class="container">
      <strong>Black Layers</strong>
      <div style="display:flex;gap:24px">
        <a href="#services">Services</a>
        <a href="#portfolio">Portfolio</a>
        <a href="#contact">Contact</a>
      </div>
    </div>
  </nav>

  <section class="hero">
    <div class="container">
      <h1>We build apps<br>that make money.</h1>
      <p>iOS development company. Our own app generates $10K+/month. We can build yours too.</p>
      <a href="#contact" class="btn">Start Your Project</a>
    </div>
  </section>

  <section id="services">
    <div class="container">
      <div class="grid">
        <div class="card">
          <h3>iOS Development</h3>
          <p>Native Swift & SwiftUI apps from concept to App Store. Zero rejections.</p>
        </div>
        <div class="card">
          <h3>Full-Stack</h3>
          <p>React, Node.js, Python backends. Complete solutions, not just frontends.</p>
        </div>
        <div class="card">
          <h3>AI Integration</h3>
          <p>Add AI-powered features to your app. From chatbots to image recognition.</p>
        </div>
      </div>
    </div>
  </section>

  <script>
    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', e => {
        e.preventDefault();
        document.querySelector(anchor.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
      });
    });

    // Intersection Observer for animations
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
        }
      }),
      { threshold: 0.1 }
    );
    document.querySelectorAll('.card').forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = 'opacity 0.5s, transform 0.5s';
      observer.observe(card);
    });
  </script>
</body>
</html>
```

---

## PART 7: Database Patterns

### PostgreSQL / Prisma Schema
```prisma
datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

generator client {
  provider = "prisma-client-js"
}

model User {
  id        String   @id @default(cuid())
  name      String
  email     String   @unique
  password  String
  items     Item[]
  createdAt DateTime @default(now()) @map("created_at")
  updatedAt DateTime @updatedAt @map("updated_at")

  @@map("users")
}

model Item {
  id          String   @id @default(cuid())
  title       String
  description String?
  status      Status   @default(ACTIVE)
  user        User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  userId      String   @map("user_id")
  createdAt   DateTime @default(now()) @map("created_at")

  @@index([userId])
  @@map("items")
}

enum Status {
  ACTIVE
  ARCHIVED
  DELETED
}
```

### MongoDB Schema (Mongoose)
```javascript
const mongoose = require("mongoose");

const userSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true },
  password: { type: String, required: true, select: false },
  role: { type: String, enum: ["user", "admin"], default: "user" },
  items: [{ type: mongoose.Schema.Types.ObjectId, ref: "Item" }],
}, { timestamps: true });

userSchema.index({ email: 1 });
userSchema.pre("save", async function () {
  if (this.isModified("password")) {
    this.password = await bcrypt.hash(this.password, 12);
  }
});

module.exports = mongoose.model("User", userSchema);
```

### Firebase / Firestore
```typescript
import { doc, collection, addDoc, getDocs, query, where, orderBy, limit } from "firebase/firestore";
import { db } from "./config";

export async function getItems(userId: string) {
  const q = query(
    collection(db, "items"),
    where("userId", "==", userId),
    orderBy("createdAt", "desc"),
    limit(20)
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() }));
}

export async function addItem(userId: string, title: string) {
  return await addDoc(collection(db, "items"), {
    title,
    userId,
    status: "active",
    createdAt: new Date(),
  });
}
```

---

## PART 8: DevOps & Deployment

### Dockerfile (Node.js)
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

### GitHub Actions CI/CD
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
      - name: Deploy to Vercel
        run: npx vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

### Nginx Config
```nginx
server {
    listen 80;
    server_name blacklayers.ca www.blacklayers.ca;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name blacklayers.ca;

    ssl_certificate /etc/letsencrypt/live/blacklayers.ca/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/blacklayers.ca/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## PART 9: Common Patterns & Best Practices

### Authentication Flow (Any Platform)
```
1. User enters email + password
2. Client sends POST /api/auth/login { email, password }
3. Server validates credentials against hashed password
4. Server generates JWT token (expires in 7d)
5. Client stores token (Keychain on iOS, EncryptedSharedPrefs on Android, httpOnly cookie on web)
6. Client sends token in Authorization header on all API requests
7. Server middleware validates token on protected routes
8. On 401 response → redirect to login
```

### Pagination Pattern
```typescript
// Request: GET /api/items?page=2&limit=20
// Response:
{
  "items": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 156,
    "pages": 8,
    "hasNext": true,
    "hasPrev": true
  }
}
```

### Error Response Format (Standard)
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is required",
    "field": "email",
    "status": 400
  }
}
```

### State Management Decision Tree
```
Small app (< 10 screens)?
  → React: useState + useContext
  → iOS: @State + @Observable
  → Android: StateFlow + compose state

Medium app (10-30 screens)?
  → React: Zustand or Jotai
  → iOS: @Observable classes + dependency injection
  → Android: Hilt + StateFlow

Large app (30+ screens)?
  → React: Zustand + React Query (server state)
  → iOS: TCA (The Composable Architecture) or custom Redux
  → Android: Hilt + Room + WorkManager
```

---

## PART 10: Code Review Checklist

When reviewing code (yours or client's), check:

### Functionality
- [ ] Does it work? Does it handle edge cases?
- [ ] Are all user inputs validated?
- [ ] Are errors handled gracefully?

### Security
- [ ] No hardcoded secrets or API keys
- [ ] SQL/NoSQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized output)
- [ ] CORS properly configured
- [ ] Auth tokens stored securely

### Performance
- [ ] No unnecessary re-renders (React) / recompositions (Compose/SwiftUI)
- [ ] Lists use proper keys/identifiers
- [ ] Images are lazy-loaded and properly sized
- [ ] Database queries use indexes
- [ ] No N+1 query problems

### Code Quality
- [ ] Clear naming (variables, functions, files)
- [ ] DRY — no copy-pasted blocks
- [ ] Single responsibility — functions do one thing
- [ ] No dead code or commented-out blocks
- [ ] Consistent formatting

---

## Error Handling
| Error | Fix |
|-------|-----|
| Code doesn't compile | Read error message, fix the exact line, re-run |
| Logic error (wrong output) | Add logging/print, trace data flow, isolate the bug |
| API returns unexpected format | Log the raw response, update the model/parser |
| Dependency conflict | Check version compatibility, use exact versions |
| Build fails on CI but works locally | Check Node/Swift/Kotlin version, check env vars |
| Performance issue | Profile first (Instruments/Profiler), optimize the bottleneck only |

## Output Format
After completing any coding task:
```
CODE DELIVERED:
- Language: [Swift / Kotlin / TypeScript / Python / etc.]
- Files: [list of files created/modified]
- Pattern: [MVVM / MVC / Clean Architecture / etc.]
- Tests: [written / not needed / pending]
- Status: Ready to build / Needs review / Has TODO items
- Notes: [any important context]
```
